import time
import base64
import requests
from pathlib import Path
import sys

# Garante acesso ao módulo config na pasta utils ou raiz
sys.path.append(str(Path(__file__).parent))
import config

# --- AGORA AS VARIÁVEIS PODEM LER DO CONFIG COM SEGURANÇA ---
URL_BASE_DEFAULT = getattr(config, "whats_url", "http://servidor:8080").rstrip("/")
INSTANCE_DEFAULT = getattr(config, "whats_instance", "rondochassis")
APIKEY_DEFAULT = getattr(config, "whats_apikey", "RondoChassis2026*")

# Garante acesso ao módulo config em Meus Documentos / ProjetoCobranca
sys.path.append(str(Path(__file__).parent))
import config

# --- CONFIGURAÇÕES INTERNAS DA EVOLUTION API ---
CONFIG_WHATSAPP_INTERNO = {
    "url_base": getattr(config, "whats_url", "http://servidor:8080"),
    "instance": getattr(config, "whats_instance", "rondochassis"),
    "apikey": getattr(config, "whats_apikey", "")
}

def formatar_moeda(valor):
    if not valor:
        return "0,00"
    val_str = f"{float(valor):,.2f}"
    return val_str.replace(",", "X").replace(".", ",").replace("X", ".")

def limpar_telefone(telefone):
    if not telefone:
        return None
    digitos = "".join([c for c in str(telefone) if c.isdigit()])
    if len(digitos) < 10:
        return None
    if not digitos.startswith("55"):
        digitos = "55" + digitos
    return digitos

def enviar_whatsapp_cobranca_cliente(cliente_obj, titulos_cliente):
    """
    Envia a notificação de cobrança de títulos em aberto via Evolution API,
    incluindo de forma pessoal o nome do operador configurado.
    """
    telefone_raw = cliente_obj.whatsapp_cobranca
    telefone = limpar_telefone(telefone_raw)
    
    if not telefone:
        raise ValueError("O cliente não possui um número de WhatsApp válido cadastrado.")
    
    url_base = CONFIG_WHATSAPP_INTERNO.get("url_base", "http://servidor:8080").rstrip("/")
    instance = CONFIG_WHATSAPP_INTERNO.get("instance", "rondochassis")
    apikey = CONFIG_WHATSAPP_INTERNO.get("apikey", "RondoChassis2026*")

    if not instance or not apikey:
        raise ValueError("A 'instance' ou 'apikey' da Evolution API não estão configuradas.")

    cliente_nome = cliente_obj.nome_cliente
    
    # Obtém o nome do operador cadastrado nas configurações (config.json)
    nome_operador = getattr(config, "nome", "").strip()
    if not nome_operador:
        nome_operador = "Equipe Financeira"

    # Monta a listagem detalhada dos títulos em aberto
    detalhes_titulos_txt = ""
    valor_total = 0.0

    for idx, tit in enumerate(titulos_cliente, start=1):
        num_doc = tit.get("numero_documento", "")
        parcela = tit.get("parcela", "1")
        vencimento = tit.get("data_vencimento", "")
        venc_fmt = "/".join(vencimento.split("-")[::-1]) if "-" in vencimento else vencimento
        valor = float(tit.get("valor_original", 0.0))
        valor_total += valor

        detalhes_titulos_txt += f"• Doc: *{num_doc}* (Parc. {parcela}) — Venc.: *{venc_fmt}* — R$ *{formatar_moeda(valor)}*\n"

    valor_total_fmt = formatar_moeda(valor_total)

    # Mensagem com tom pessoal e profissional incluindo o nome do operador
    mensagem = (
        f"Olá *{cliente_nome}*, tudo bem?\n\n"
        f"Aqui é o(a) *{nome_operador}*, da *RONDOCHASSIS*. "
        f"Entramos em contato para lembrar sobre a existência de títulos pendentes em nossa base:\n\n"
        f"{detalhes_titulos_txt}\n"
        f"💰 *VALOR TOTAL PENDENTE: R$ {valor_total_fmt}*\n\n"
        f"Caso já tenha efetuado o pagamento, por gentileza desconsidere e nos envie o comprovante.\n"
        f"Se precisar de segunda via ou tiver alguma dúvida, estou à disposição!\n\n"
        f"_RONDOCHASSIS SERVIÇOS LTDA_"
    )

    headers = {
        "apikey": apikey,
        "Content-Type": "application/json"
    }

    url_texto = f"{url_base}/message/sendText/{instance}"
    payload_texto = {
        "number": telefone,
        "text": mensagem
    }

    try:
        resp = requests.post(url_texto, json=payload_texto, headers=headers, timeout=60)
        if resp.status_code not in [200, 201]:
            raise Exception(f"Erro HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        raise Exception(f"Erro ao conectar com a Evolution API (WhatsApp): {str(e)}")

    return True