import smtplib
import imaplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.encoders import encode_base64
from email.utils import formatdate, make_msgid
from pathlib import Path
import sys

# Garante acesso ao módulo config em Meus Documentos / ProjetoCobranca
sys.path.append(str(Path(__file__).parent))
import config

def formatar_moeda(valor):
    if not valor:
        return "0,00"
    val_str = f"{float(valor):,.2f}"
    return val_str.replace(",", "X").replace(".", ",").replace("X", ".")

def enviar_email_cobranca_cliente(cliente_obj, titulos_cliente, arquivo_anexo_path=None):
    """
    Envia e-mail de cobrança utilizando as configurações seguras do config.json e assinatura configurada.
    """
    email_raw = cliente_obj.email_cobranca
    
    if not email_raw:
        raise ValueError("O cliente não possui e-mail cadastrado.")
        
    email_tratado = str(email_raw).replace(";", ",")
    destinatarios = [e.strip() for e in email_tratado.split(",") if e.strip()]
    
    if not destinatarios:
        raise ValueError("Nenhum e-mail válido foi encontrado no cadastro do cliente.")

    cliente_nome = cliente_obj.nome_cliente
    
    # Configurações de Servidor fixas da empresa (ou podem ir para o config se preferir)
    smtp_host = "smtp.hostinger.com"
    smtp_port = 465
    imap_host = "imap.hostinger.com"
    imap_port = 993
    
    # Lê as credenciais seguras do config (salvas em Meus Documentos)
    remetente = getattr(config, "email_remetente", "")
    senha = getattr(config, "email_senha", "")
    assinatura_path = getattr(config, "assinatura_path", "")
    
    if not remetente or not senha:
        raise ValueError("Configure o e-mail remetente e a senha na tela de 'Configurações' do sistema.")
    
    assunto = f"Cobrança - Títulos em Aberto | Rondochassis"
        
    detalhes_titulos_html = "<br>"
    valor_total = 0.0
    
    for idx, tit in enumerate(titulos_cliente, start=1):
        vencimento = tit.get("data_vencimento", "")
        venc_fmt = "/".join(vencimento.split("-")[::-1]) if "-" in vencimento else vencimento
        valor = float(tit.get("valor_original", 0.0))
        valor_total += valor
        num_doc = tit.get("numero_documento", "")
        parcela = tit.get("parcela", "1")
        
        detalhes_titulos_html += f"<b>{idx}.</b> Documento: {num_doc} (Parcela {parcela}) — Vencimento: {venc_fmt} — Valor: R$ {formatar_moeda(valor)}<br>\n"

    valor_total_fmt = formatar_moeda(valor_total)

    corpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333333; font-size: 14px; line-height: 1.5;">
        <p>Prezado(a) <b>{cliente_nome}</b>,</p>
        <p>Esperamos que esteja tudo bem.</p>
        <p>Entramos em contato para lembrar sobre a existência de títulos pendentes em nossa base:</p>
        
        <p style="background-color: #f3f4f6; padding: 10px; border-left: 4px solid #2563eb;">
        {detalhes_titulos_html}
        <br><b>VALOR TOTAL PENDENTE: R$ {valor_total_fmt}</b>
        </p>
        
        <p>Caso já tenha efetuado o pagamento, por gentileza desconsidere esta mensagem e nos envie o comprovante para baixa.</p>
        
        <p>Se houver alguma dúvida ou necessidade de segunda via, estamos à total disposição.<br>
        Agradecemos pela atenção!</p>
        
        <p>Atenciosamente,<br><b>RONDOCHASSIS SERVIÇOS LTDA</b></p>
    """

    if assinatura_path and Path(assinatura_path).exists():
        corpo_html += f'<br><img src="cid:assinatura_imagem" alt="Assinatura" style="max-width: 750px; height: auto;"><br>'

    corpo_html += """
    </body>
    </html>
    """
    
    msg = MIMEMultipart('related')
    msg['From'] = remetente
    msg['To'] = ", ".join(destinatarios)
    msg['Subject'] = assunto
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid()
    
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    msg_alternative.attach(MIMEText(corpo_html, 'html', 'utf-8'))
    
    if assinatura_path and Path(assinatura_path).exists():
        try:
            with open(assinatura_path, "rb") as f:
                img_data = f.read()
                img = MIMEImage(img_data)
                img.add_header('Content-ID', '<assinatura_imagem>')
                img.add_header('Content-Disposition', 'inline', filename=Path(assinatura_path).name)
                msg.attach(img)
        except Exception as e:
            print(f"⚠️ Aviso ao anexar assinatura: {e}")

    if arquivo_anexo_path and Path(arquivo_anexo_path).exists():
        caminho_arq = Path(arquivo_anexo_path)
        with open(caminho_arq, "rb") as f:
            parte = MIMEBase('application', 'octet-stream')
            parte.set_payload(f.read())
        encode_base64(parte)
        parte.add_header('Content-Disposition', f'attachment; filename="{caminho_arq.name}"')
        msg.attach(parte)
        
    try:
        contexto = smtplib.ssl.create_default_context()
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=contexto, timeout=30) as server:
                server.login(remetente, senha)
                server.sendmail(remetente, destinatarios, msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                server.starttls(context=contexto)
                server.login(remetente, senha)
                server.sendmail(remetente, destinatarios, msg.as_string())
    except Exception as e:
        raise Exception(f"Erro ao enviar e-mail via SMTP: {str(e)}")

    try:
        with imaplib.IMAP4_SSL(imap_host, imap_port, timeout=30) as imap:
            imap.login(remetente, senha)
            try:
                imap.append('INBOX.Sent', '(\\Seen)', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
            except Exception:
                imap.append('Sent', '(\\Seen)', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    except Exception as imap_erro:
        print(f"⚠️ Aviso: E-mail enviado, mas erro ao salvar em Enviados: {imap_erro}")

    return True