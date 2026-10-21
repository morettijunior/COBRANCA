import json
from pathlib import Path
from datetime import datetime

def obter_pasta_documentos():
    """Retorna a pasta raiz do projeto em Meus Documentos."""
    home = Path.home()
    docs = home / "Documents"
    if not docs.exists():
        docs = home / "Documentos"
        
    pasta_projeto = docs / "ProjetoCobranca"
    pasta_projeto.mkdir(parents=True, exist_ok=True)
    return pasta_projeto

def obter_pasta_clientes():
    """Retorna a subpasta exclusiva para os arquivos JSON dos clientes."""
    pasta_projeto = obter_pasta_documentos()
    pasta_clientes = pasta_projeto / "clientes"
    pasta_clientes.mkdir(parents=True, exist_ok=True)
    return pasta_clientes

def obter_pasta_titulos():
    """Retorna a subpasta exclusiva para os arquivos JSON dos títulos."""
    pasta_projeto = obter_pasta_documentos()
    pasta_titulos = pasta_projeto / "titulos"
    pasta_titulos.mkdir(parents=True, exist_ok=True)
    return pasta_titulos


class ClienteCobranca:
    def __init__(self, cod_cfo, nome_cliente="", email_cobranca="", whatsapp_cobranca="", cobranca_especial=False):
        self.cod_cfo = cod_cfo
        self.nome_cliente = nome_cliente
        self.email_cobranca = email_cobranca
        self.whatsapp_cobranca = whatsapp_cobranca
        self.cobranca_especial = cobranca_especial  # True se estiver no jurídico/especial, False se for comum

    def para_dicionario(self):
        return {
            "cod_cfo": self.cod_cfo,
            "nome_cliente": self.nome_cliente,
            "email_cobranca": self.email_cobranca,
            "whatsapp_cobranca": self.whatsapp_cobranca,
            "cobranca_especial": self.cobranca_especial
        }

    def salvar_json(self):
        """Salva os dados de contato e status de cobrança do cliente na subpasta 'clientes'."""
        pasta_clientes = obter_pasta_clientes()
        arquivo = pasta_clientes / f"cliente_{self.cod_cfo}.json"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(self.para_dicionario(), f, ensure_ascii=False, indent=4)

    @classmethod
    def carregar_json(cls, cod_cfo):
        """Carrega os dados do cliente da subpasta 'clientes' se o arquivo já existir."""
        pasta_clientes = obter_pasta_clientes()
        arquivo = pasta_clientes / f"cliente_{cod_cfo}.json"
        
        if arquivo.exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                return cls(
                    cod_cfo=dados.get("cod_cfo"),
                    nome_cliente=dados.get("nome_cliente", ""),
                    email_cobranca=dados.get("email_cobranca", ""),
                    whatsapp_cobranca=dados.get("whatsapp_cobranca", ""),
                    cobranca_especial=dados.get("cobranca_especial", False)
                )
        return None


class TituloCobranca:
    def __init__(self, cod_cfo, numero_documento, parcela, data_vencimento, valor_original, ativo="S", historico_cobrancas=None):
        self.cod_cfo = cod_cfo
        self.numero_documento = numero_documento
        self.parcela = parcela if parcela is not None else 1
        self.data_vencimento = data_vencimento
        self.valor_original = valor_original
        self.ativo = ativo  # 'S' ou 'N'
        self.historico_cobrancas = historico_cobrancas if historico_cobrancas is not None else []

    def adicionar_historico(self, canal, status, observacao=""):
        """Adiciona um registro de tentativa/envio de cobrança ao histórico."""
        registo = {
            "data_hora": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "canal": canal,  # Ex: 'EMAIL', 'WHATSAPP', 'PERSONALIZADO'
            "status": status,  # Ex: 'ENVIADO', 'REGISTRADO'
            "observacao": observacao
        }
        self.historico_cobrancas.append(registo)

    def para_dicionario(self):
        venc = self.data_vencimento
        if hasattr(venc, 'strftime'):
            str_venc = venc.strftime('%Y-%m-%d')
        else:
            str_venc = str(venc)
        
        return {
            "cod_cfo": self.cod_cfo,
            "numero_documento": self.numero_documento,
            "parcela": self.parcela,
            "data_vencimento": str_venc,
            "valor_original": float(self.valor_original) if self.valor_original else 0.0,
            "ativo": self.ativo,
            "historico_cobrancas": self.historico_cobrancas
        }

    def salvar_json(self):
        """Salva ou atualiza o título individualmente na subpasta 'titulos'."""
        pasta_titulos = obter_pasta_titulos()
        doc_limpo = str(self.numero_documento).replace("/", "_").replace("\\", "_")
        arquivo = pasta_titulos / f"titulo_{doc_limpo}_P{self.parcela}_{self.cod_cfo}.json"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(self.para_dicionario(), f, ensure_ascii=False, indent=4)

    @classmethod
    def carregar_json(cls, numero_documento, parcela, cod_cfo):
        """Carrega um título existente da subpasta 'titulos'."""
        pasta_titulos = obter_pasta_titulos()
        doc_limpo = str(numero_documento).replace("/", "_").replace("\\", "_")
        arquivo = pasta_titulos / f"titulo_{doc_limpo}_P{parcela}_{cod_cfo}.json"
        
        if arquivo.exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                return cls(
                    cod_cfo=dados.get("cod_cfo"),
                    numero_documento=dados.get("numero_documento"),
                    parcela=dados.get("parcela", 1),
                    data_vencimento=dados.get("data_vencimento"),
                    valor_original=dados.get("valor_original"),
                    ativo=dados.get("ativo", "S"),
                    historico_cobrancas=dados.get("historico_cobrancas", [])
                )
        return None