import mysql.connector
from mysql.connector import Error
from datetime import datetime
       
# Classe que gerencia a conexão e operações com o banco de dados
class GerenciadorCooperados:
       def __init__(self, config):
         self.config = config # Configuração do banco de dados
         
       
       # Conecta ao banco de dados
       def conectar(self):
         try:
            print(
               self.config.get("host"),
               self.config.get("user"),
               self.config.get("password"),
               self.config.get("database"),
               flush=True
            )
            
            conexao = mysql.connector.connect(**self.config)
            if conexao.is_connected():
                print("Conexão bem-sucedida com o banco de dados.")
                return conexao
         except Error as e:
                print(f"Erro ao conectar no MySQL: {e}")
                return None
       
       # Cria a tabela "cooperados" se ela não existir
       def criar_tabela_PSS(self):
         conexao = self.conectar()
         if conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS PSS (
                    Matricula VARCHAR(20) PRIMARY KEY,
                    nome VARCHAR(20) NOT NULL
                )
            """)
            conexao.commit()
            conexao.close()
     
       def criar_tabela_Pendencia(self):
        conexao = self.conectar()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Pendencias (
                    IdPedencias INT AUTO_INCREMENT PRIMARY KEY,
                    Matricula VARCHAR(20),
                    TipoPendencia VARCHAR(100),
                    StatusPendecia VARCHAR(20),
                    Data date,
                    Descricao VARCHAR(100),
                    FOREIGN KEY(Matricula) REFERENCES PSS(Matricula)
                )""")
            conexao.commit()
            conexao.close()
       
       # Cadastra um novo cooperado no banco de dados
       def cadastrar_PSS(self, Matricula, nome):
        conexao = self.conectar()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO PSS (Matricula, nome) VALUES (%s, %s)", (Matricula, nome)
            )
            conexao.commit()
            conexao.close()
           
       def cadastrar_pendencia(self, Matricula, TipoPendencia, StatusPendecia,Data, Descricao):
          conexao = self.conectar()
          # Inverte a data para o formato YYYY-MM-DD
          Data = self.inverterData(Data)
          if conexao:
            try:
              cursor = conexao.cursor()
              cursor.execute("""
                INSERT INTO Pendencias (Matricula, TipoPendencia, StatusPendecia, Data, Descricao)
                VALUES (%s, %s, %s, %s, %s)
                """, (Matricula, TipoPendencia, StatusPendecia, Data, Descricao))
              conexao.commit()
              return {"sucesso": True, "mensagem": "Pendência cadastrada com sucesso"}
            except Error as e:
              print(f"Erro ao cadastrar pendência: {e}")
              return {"sucesso": False, "mensagem": f"Erro: {e}"}
            finally:
              conexao.close()
            
       def inverterData(self,i):
          data_obj = datetime.strptime(i, "%d/%m/%Y")  # Converte string em data
          data_convertida = data_obj.strftime("%Y-%m-%d")  # Converte data em string no formato certo
          return data_convertida
          
                                      
       # Busca cooperados pelo nome
       def buscar_cooperados(self, nome):
        cooperados = [ { 
                   "none":"none" ,
                   "none":"none" ,
                   "none":"none" ,
                   "none":"none" ,
                   "none":"none" ,
                   "none":"none" ,
                   "none":"none" ,
         }]
        conexao = self.conectar()

        if not conexao:
         return cooperados

        try:
          
          #Criado cursor para retornar dicionário. E executado a variável sql com parametro nome.
          cursor = conexao.cursor(dictionary=True)
          cursor.execute("""
            SELECT 
            p.Matricula,
            p.nome,
            pe.IdPedencias AS IdPedencias,
            pe.TipoPendencia,
            pe.StatusPendecia,
            pe.Data,
            pe.Descricao
            FROM PSS p
            INNER JOIN Pendencias pe ON p.Matricula = pe.Matricula
            WHERE LOWER(p.nome) LIKE %s  """, ("%" + nome.lower() + "%",))
          

          resultado = cursor.fetchall()
          print(f"Qtd registros encontrados: {len(resultado)}", flush=True)
          for row in resultado:
            print("Linha retornada:", row, flush=True)
      

        #Retorna os dados eonctrado na busca.
          if resultado:
            cooperados = [
                {
                    "IdPedencias": row["IdPedencias"],
                    "Matricula": row["Matricula"],
                    "nome": row["nome"],
                    "TipoPendencia": row["TipoPendencia"],
                    "StatusPendecia": row["StatusPendecia"],
                    "Data": row["Data"],
                    "Descricao": row["Descricao"]
                }
                for row in resultado
            ]
          else:
            print("Nenhum cooperado encontrado.")
        

        except Error as e:
          print(f"Erro ao buscar cooperados: {e}")
        finally:
            if conexao.is_connected():  #garante que a conexão existe antes de fechar
              conexao.close()
        return cooperados

       # Atualiza dados de um cooperado
       def atualizar_pendencia(self, IdPendencia, PessoaAutorizada, AssinaturaCooperado):
            conexao = self.conectar()
            if conexao:
              try:
                cursor = conexao.cursor()
                cursor.execute("""
                  UPDATE Pendencias 
                   SET StatusPendecia = %s, TipoPendencia = %s
                   WHERE IdPedencias = %s           
                  """, (PessoaAutorizada, AssinaturaCooperado, IdPendencia))

                conexao.commit()  # ✅ commit vem antes do close
                print("Pendência atualizada com sucesso!")

              except Error as e:
                print(f"Erro ao atualizar pendência: {e}")

              finally:
                if conexao.is_connected():
                  conexao.close()
