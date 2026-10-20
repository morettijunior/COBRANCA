from datetime import date
from pathlib import Path
import json

def obter_pasta_documentos():
    """Localiza a pasta Documentos do usuário e garante a subpasta ProjetoCobranca."""
    home = Path.home()
    docs = home / "Documents"
    if not docs.exists():
        docs = home / "Documentos"
        
    pasta_projeto = docs / "ProjetoCobranca"
    pasta_projeto.mkdir(parents=True, exist_ok=True)
    return pasta_projeto

def carregar_configuracoes():
    """Lê o arquivo config.json de Meus Documentos."""
    caminho_json = obter_pasta_documentos() / "config.json"
    
    config_padrao = {
        "nome": "",
        "assinatura_path": "",
        "feriados": [
            "01/01/2026", "16/02/2026", "17/02/2026", "03/04/2026", 
            "21/04/2026", "01/05/2026", "04/06/2026", "07/09/2026", 
            "12/10/2026", "02/11/2026", "15/11/2026", "20/11/2026", 
            "10/12/2026", "25/12/2026"
        ]
    }
    
    if caminho_json.exists():
        try:
            with open(caminho_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return config_padrao
    return config_padrao

def salvar_configuracoes(nome_operador, assinatura_path_str, lista_feriados_str):
    """Salva o nome, o caminho da assinatura e os feriados em config.json."""
    caminho_json = obter_pasta_documentos() / "config.json"
    
    dados = {
        "nome": nome_operador,
        "assinatura_path": assinatura_path_str,
        "feriados": lista_feriados_str
    }
    
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Carrega os dados salvos ao importar o config
_dados_iniciais = carregar_configuracoes()

nome = _dados_iniciais.get("nome", "")
assinatura_path = _dados_iniciais.get("assinatura_path", "")

feriados = set()
for f_str in _dados_iniciais.get("feriados", []):
    try:
        partes = f_str.split("/")
        if len(partes) == 3:
            d, m, a = map(int, partes)
            feriados.add(date(a, m, d))
    except ValueError:
        pass