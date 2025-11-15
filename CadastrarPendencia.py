from gerenciador import GerenciadorCooperados
from config import CONFING


#Estanciando objeto da classe de gerenciamento.
gerenciador = GerenciadorCooperados(CONFING)


#class CadastrarPendencia:
class CadastrarPendencia:
     def __init__(self,dados):
        self.Matricula = dados.get("Matricula")
        self.TipoPendencia = dados.get("TipoPendencia")
        self.StatusPendecia = dados.get("StatusPendecia")
        self.Data = dados.get("Data")
        self.Descricao = dados.get("Descricao")
       
      
     def CadastrarPendenciaMethod(self):
       try:
        if not self.Matricula or not self.TipoPendencia or not self.StatusPendecia or not self.Data:
            return {"sucesso": False, "mensagem": "Todos os campos obrigatórios devem ser preenchidos."}
        
        # Verifica se a data está no formato correto
        gerenciador.criar_tabela_Pendencia()
        gerenciador.cadastrar_pendencia(self.Matricula, self.TipoPendencia, self.StatusPendecia, self.Data, self.Descricao)
        
        return {"sucesso": True, "mensagem": f"Pendência cadastrada com sucesso!"}

       except Exception as e:
        print("Erro ao cadastrar pendência:", e)
        return {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"}, 500
