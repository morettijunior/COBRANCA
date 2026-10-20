from datetime import date
from pathlib import Path
import json
import fdb
from config import feriados
from ultimo_dia_util import obter_ultimo_dia_util_anterior, gerar_fins_de_semana_atual_e_anterior
from modelos import TituloCobranca, ClienteCobranca, obter_pasta_titulos

# --- CONFIGURAÇÕES DO BANCO FIREBIRD (TGA) ---
DB_HOST = "SERVIDOR"
DB_PORT = 3050
DB_PATH = r"c:\tga\dados\tga.fdb"
DB_USER = "SYSDBA"
DB_PASSWORD = "masterkey"

def conectar_banco():
    try:
        return fdb.connect(
            dsn=f"{DB_HOST}/{DB_PORT}:{DB_PATH}",
            user=DB_USER,
            password=DB_PASSWORD,
            charset="ISO8859_1",
        )
    except Exception as e:
        print(f"Erro ao conectar no Firebird: {e}")
        return None

def sincronizar_titulos(data_limite):
    conexao = conectar_banco()
    if not conexao:
        print("Não foi possível conectar ao banco de dados.")
        return
    
    cursor = conexao.cursor()
    
    # Adicionado L.PARCELA na consulta
    sql = """
        SELECT 
            L.CODCFO,
            C.NOME,
            L.NUMERODOCUMENTO,
            L.PARCELA,
            L.DATAVENCIMENTO,
            L.VALORORIGINAL
        FROM FLAN L
        JOIN FCFO C ON L.CODCFO = C.CODCFO
        WHERE L.PAGREC = 'R'
          AND L.STATUSLAN = 'A'
          AND L.CODTDO IN ('DP', 'NF', 'BO')
          AND L.DATAVENCIMENTO <= ?
    """
    
    try:
        cursor.execute(sql, (data_limite,))
        registros_banco = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao executar a consulta SQL: {e}")
        cursor.close()
        conexao.close()
        return

    cursor.close()
    conexao.close()

    titulos_banco_dict = {}
    clientes_encontrados = {}

    for reg in registros_banco:
        cod_cfo, nome_cfo, num_doc, parcela, data_venc, valor = reg
        
        if cod_cfo not in clientes_encontrados:
            cli_existente = ClienteCobranca.carregar_json(cod_cfo)
            if not cli_existente:
                novo_cli = ClienteCobranca(cod_cfo=cod_cfo, nome_cliente=nome_cfo)
                novo_cli.salvar_json()
            clientes_encontrados[cod_cfo] = nome_cfo

        parcela_val = parcela if parcela is not None else 1
        # Chave única inclui o documento, a parcela e o cliente
        chave = (str(num_doc), str(parcela_val), str(cod_cfo))
        titulos_banco_dict[chave] = {
            "cod_cfo": cod_cfo,
            "numero_documento": str(num_doc),
            "parcela": parcela_val,
            "data_vencimento": data_venc,
            "valor_original": float(valor) if valor else 0.0
        }

    pasta_titulos = obter_pasta_titulos()
    arquivos_json = list(pasta_titulos.glob("titulo_*.json"))
    chaves_processadas_disco = set()

    for arquivo in arquivos_json:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados_json = json.load(f)
                
            num_doc = str(dados_json.get("numero_documento"))
            parcela_val = str(dados_json.get("parcela", 1))
            cod_cfo = str(dados_json.get("cod_cfo"))
            chave = (num_doc, parcela_val, cod_cfo)
            chaves_processadas_disco.add(chave)

            titulo_obj = TituloCobranca(
                cod_cfo=cod_cfo,
                numero_documento=num_doc,
                parcela=dados_json.get("parcela", 1),
                data_vencimento=dados_json.get("data_vencimento"),
                valor_original=dados_json.get("valor_original"),
                ativo=dados_json.get("ativo", "S"),
                historico_cobrancas=dados_json.get("historico_cobrancas", [])
            )

            if chave in titulos_banco_dict:
                titulo_obj.ativo = "S"
            else:
                titulo_obj.ativo = "N"

            titulo_obj.salvar_json()
        except Exception as e:
            print(f"Erro ao processar ficheiro {arquivo.name}: {e}")

    for chave, info in titulos_banco_dict.items():
        if chave not in chaves_processadas_disco:
            novo_titulo = TituloCobranca(
                cod_cfo=info["cod_cfo"],
                numero_documento=info["numero_documento"],
                parcela=info["parcela"],
                data_vencimento=info["data_vencimento"],
                valor_original=info["valor_original"],
                ativo="S",
                historico_cobrancas=[]
            )
            novo_titulo.salvar_json()

    print("Sincronização de títulos concluída com sucesso!")

if __name__ == "__main__":
    hoje = date.today()
    fds = gerar_fins_de_semana_atual_e_anterior()
    ultimo_dia_util = obter_ultimo_dia_util_anterior(data_referencia=hoje, conjunto_fds=fds, conjunto_feriados=feriados)
    
    print(f"Executando busca até o último dia útil: {ultimo_dia_util.strftime('%d/%m/%Y')}")
    sincronizar_titulos(ultimo_dia_util)