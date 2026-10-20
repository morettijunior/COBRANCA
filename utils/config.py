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
        "email_remetente": "",
        "email_senha": "",
        "whats_url": "http://servidor:8080",
        "whats_instance": "rondochassis",
        "whats_apikey": "",
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
                dados = json.load(f)
                # Garante compatibilidade caso o json antigo não tenha as novas chaves
                for k, v in config_padrao.items():
                    if k not in dados:
                        dados[k] = v
                return dados
        except Exception:
            return config_padrao
    return config_padrao

def salvar_configuracoes(dados_novos):
    """Salva todas as configurações em config.json."""
    caminho_json = obter_pasta_documentos() / "config.json"
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(dados_novos, f, ensure_ascii=False, indent=4)

# Carrega os dados salvos ao importar o config
_dados_iniciais = carregar_configuracoes()

nome = _dados_iniciais.get("nome", "")
assinatura_path = _dados_iniciais.get("assinatura_path", "")
email_remetente = _dados_iniciais.get("email_remetente", "")
email_senha = _dados_iniciais.get("email_senha", "")
whats_url = _dados_iniciais.get("whats_url", "http://servidor:8080")
whats_instance = _dados_iniciais.get("whats_instance", "rondochassis")
whats_apikey = _dados_iniciais.get("whats_apikey", "")

feriados = set()
for f_str in _dados_iniciais.get("feriados", []):
    try:
        partes = f_str.split("/")
        if len(partes) == 3:
            d, m, a = map(int, partes)
            feriados.add(date(a, m, d))
    except ValueError:
        pass