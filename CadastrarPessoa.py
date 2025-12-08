from gerenciador import GerenciadorCooperados
from config import CONFING
gerenciador = GerenciadorCooperados(CONFING)


class CadastrarPessoa:
   def __init__(self,dados):
        self.nome = dados.get("nome")
        self.Matricula = dados.get("Matricula")
        self.email =  dados.get("email")
        self.whatsapp =  dados.get("whatsapp")
        self. dataEntrada = dados.get("dataEntrada")
        self.tipoCooperado = dados.get("tipoCooperado")
        self.situacao = dados.get("situacao")
        self.Mensagem = dados.get("Mensagem")
   
   def CadastraPessoaMethod(self):
       try:
        
        if not self.Matricula or not self.nome:
            return {"sucesso": False, "mensagem": "Todos os campos obrigatórios devem ser preenchidos."}
        
        gerenciador.criar_tabela_PSS()
        gerenciador.cadastrar_PSS(self.Matricula, self.nome, self.email, self.whatsapp, self.dataEntrada, self.tipoCooperado, self.situacao)
        return {"sucesso": True, "mensagem": f"Cooperado {self.nome} cadastrado com sucesso!"}
    
       except Exception as e:
         print("Erro ao cadastrar pessoa:", e)
         return {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"},500
