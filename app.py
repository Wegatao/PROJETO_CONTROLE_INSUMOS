# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from gerenciador import GerenciadorCooperados
from CadastrarPendencia import CadastrarPendencia
from CadastrarPessoa import CadastrarPessoa
from config import CONFING
import os

# ===== IMPORTS NOVOS PARA AUTENTICAÇÃO =====
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from functools import wraps
# ==========================================

app = Flask(__name__)
CORS(app)

# --- AUTENTICAÇÃO: chave secreta e serializer de token ---
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "trocar-essa-chave-em-producao")
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

gg = GerenciadorCooperados(CONFING)
# opcional: garantir tabela de usuários existe
# gg.criar_tabela_usuarios()


# --- HELPERS DE AUTENTICAÇÃO (TOKEN SIMPLES) ---

def gerar_token(user_id):
    """Gera um token de autenticação simples a partir do id do usuário."""
    return serializer.dumps({"user_id": user_id})


def validar_token(token, max_age=60 * 60 * 8):  # 8 horas
    """Valida token e retorna dados ou None."""
    try:
        dados = serializer.loads(token, max_age=max_age)
        return dados  # ex: {"user_id": 1}
    except SignatureExpired:
        return None  # token expirou
    except BadSignature:
        return None  # token inválido


def requer_autenticacao(f):
    """Decorator para proteger rotas com token Bearer."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"sucesso": False, "mensagem": "Token não enviado."}), 401

        token = auth_header.split(" ", 1)[1]
        dados = validar_token(token)
        if not dados:
            return jsonify({"sucesso": False, "mensagem": "Token inválido ou expirado."}), 401

        # Se quiser usar o id do usuário na rota:
        request.user_id = dados["user_id"]
        return f(*args, **kwargs)
    return wrapper


# ============================
# ======== ROTAS API =========
# ============================

@app.route("/", methods=["GET"])
def home():
    return jsonify({"mensagem": "Backend do ERP está online!"})


# ---------- AUTENTICAÇÃO ----------

@app.route("/registrarUsuario", methods=["POST"])
def registrar_usuario():
    dados = request.get_json() or {}
    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return jsonify({"sucesso": False, "mensagem": "Nome, email e senha são obrigatórios."}), 400

    # Verifica se já existe usuário com esse email
    usuario_existente = gg.buscar_usuario_por_email(email)
    if usuario_existente:
        return jsonify({"sucesso": False, "mensagem": "Email já cadastrado."}), 400

    # Gera hash da senha
    senha_hash = generate_password_hash(senha)

    resultado = gg.cadastrar_usuario(nome, email, senha_hash)
    status = 200 if resultado.get("sucesso") else 400
    return jsonify(resultado), status


@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json() or {}
    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({"sucesso": False, "mensagem": "Email e senha são obrigatórios."}), 400

    usuario = gg.buscar_usuario_por_email(email)
    if not usuario:
        return jsonify({"sucesso": False, "mensagem": "Usuário ou senha inválidos."}), 401

    # Confere senha
    if not check_password_hash(usuario["senha_hash"], senha):
        return jsonify({"sucesso": False, "mensagem": "Usuário ou senha inválidos."}), 401

    # Gera token
    token = gerar_token(usuario["id"])

    return jsonify({
        "sucesso": True,
        "mensagem": "Login realizado com sucesso.",
        "token": token,
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "papel": usuario["papel"],
        }
    }), 200


# ---------- ROTAS DO SISTEMA ----------

@app.route("/cadastrarPessoa", methods=["POST"])
# @requer_autenticacao  # habilita depois que o front estiver enviando o token
def cadastrarPessoa():
    dados = request.get_json()
    resultado = CadastrarPessoa(dados).CadastraPessoaMethod()
    return jsonify(resultado), 200 if resultado.get("sucesso") else 400


@app.route("/cadastrarPendencia", methods=["POST"])
# @requer_autenticacao
def cadastrarPendencia():
    dados = request.get_json()
    resultado = CadastrarPendencia(dados).CadastrarPendenciaMethod()
    return jsonify(resultado), 200 if resultado.get("sucesso") else 400


@app.route("/buscar", methods=["POST"])
# @requer_autenticacao
def buscar():
    dados = request.get_json()
    print("DADOS RECEBIDOS:", dados, flush=True)

    if dados is None:
        return jsonify({"sucesso": False, "mensagem": "JSON inválido ou não enviado."}), 400

    nome = dados.get('nome', '').strip()

    if not nome:
        return jsonify({"sucesso": False, "mensagem": "nome não fornecido."}), 400

    print(f"Nome recebido para busca: {nome}", flush=True)
    resultado = gg.buscar_cooperados(nome)
    print("DADOS RECEBIDOS:", nome, flush=True)

    cooperados = []
    for linha in resultado:
        print("Montando cooperado com linha:", linha, flush=True)
        cooperados.append({
            "IdPedencias": linha.get("IdPedencias"),
            "id": linha.get("Matricula"),
            "nome": linha.get("nome"),
            "pendencias": linha.get("TipoPendencia"),
            "StatusPedencia": linha.get("StatusPedecia") if "StatusPedecia" in linha else linha.get("StatusPendecia"),
            "observacao": linha.get("Descricao"),
            "data_emissao": linha.get("Data"),
        })

    return jsonify({"cooperados": cooperados}), 200


@app.route("/atualizar", methods=["PUT"])
# @requer_autenticacao
def atualizar():
    dados = request.get_json()
    IdPendencia = dados.get("IdPedencias")  # Matricula usada como ID
    PessoaAutorizada = dados.get("PessoaAutorizada")
    AssinaturaCooperado = dados.get("AssinaturaCooperado")

    if not PessoaAutorizada or not AssinaturaCooperado:
        return jsonify({"sucesso": False, "mensagem": "Campos obrigatórios não informados."})

    gg.atualizar_pendencia(IdPendencia, PessoaAutorizada, AssinaturaCooperado)

    return jsonify({"sucesso": True, "mensagem": "Pendência atualizada com sucesso"})


# Essa função ainda não está criada no gerenciador.py (cuidado ao usar)
@app.route("/deletar", methods=["DELETE"])
# @requer_autenticacao
def deletar():
    dados = request.get_json()
    matricula = dados.get("id")
    if not matricula:
        return jsonify({"sucesso": False, "mensagem": "Matricula não informada."})
    gg.deletar_pendencia(matricula)  # ainda precisa ser implementado no GerenciadorCooperados
    return jsonify({"sucesso": True, "mensagem": "Pendência deletada com sucesso"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
