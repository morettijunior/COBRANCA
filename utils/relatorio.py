from pathlib import Path
import json
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def obter_pasta_documentos():
    home = Path.home()
    docs = home / "Documents"
    if not docs.exists():
        docs = home / "Documentos"
    return docs / "ProjetoCobranca"

def obter_pasta_titulos():
    return obter_pasta_documentos() / "titulos"

def obter_pasta_clientes():
    return obter_pasta_documentos() / "clientes"

def obter_pasta_relatorios():
    pasta_relatorios = obter_pasta_documentos() / "relatorios"
    pasta_relatorios.mkdir(parents=True, exist_ok=True)
    return pasta_relatorios

def gerar_relatorio_cobranca_pdf():
    pasta_titulos = obter_pasta_titulos()
    pasta_clientes = obter_pasta_clientes()
    pasta_relatorios = obter_pasta_relatorios()
    
    if not pasta_titulos.exists():
        return None, "Pasta de títulos não encontrada. Execute 'Receber Dados' primeiro."

    titulos_ativos = []
    for arquivo in pasta_titulos.glob("titulo_*.json"):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                if dados.get("ativo") == "S":
                    titulos_ativos.append(dados)
        except Exception:
            pass

    if not titulos_ativos:
        return None, "Nenhum título ativo encontrado para gerar o relatório."

    for t in titulos_ativos:
        cod_cfo = t.get("cod_cfo")
        arq_cliente = pasta_clientes / f"cliente_{cod_cfo}.json"
        nome_cliente = f"Cliente {cod_cfo}"
        if arq_cliente.exists():
            try:
                with open(arq_cliente, 'r', encoding='utf-8') as f:
                    c_dados = json.load(f)
                    nome_cliente = c_dados.get("nome_cliente", nome_cliente)
            except Exception:
                pass
        t["_nome_cliente"] = nome_cliente

    def chave_ordenacao(item):
        try:
            dt = datetime.strptime(item.get("data_vencimento"), "%Y-%m-%d")
        except ValueError:
            dt = datetime.min
        return (item.get("_nome_cliente"), dt, item.get("numero_documento"), str(item.get("parcela", 1)))

    titulos_ativos.sort(key=chave_ordenacao)

    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho_pdf = pasta_relatorios / f"relatorio_cobranca_{timestamp_str}.pdf"

    doc = SimpleDocTemplate(str(caminho_pdf), pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elementos = []
    estilos = getSampleStyleSheet()

    titulo_estilo = ParagraphStyle(
        'TituloRelatorio',
        parent=estilos['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=colors.HexColor('#1f2937'),
        alignment=1,
        spaceAfter=10
    )
    
    sub_estilo = ParagraphStyle(
        'SubTituloRelatorio',
        parent=estilos['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#4b5563'),
        alignment=1,
        spaceAfter=15
    )

    cliente_heading_estilo = ParagraphStyle(
        'ClienteHeading',
        parent=estilos['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=10,
        spaceAfter=4
    )

    celula_estilo = ParagraphStyle(
        'CelulaTexto',
        parent=estilos['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#1f2937')
    )

    celula_header_estilo = ParagraphStyle(
        'CelulaHeader',
        parent=estilos['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.whitesmoke
    )

    elementos.append(Paragraph("RELATÓRIO DE TÍTULOS EM ABERTO", titulo_estilo))
    elementos.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", sub_estilo))

    from itertools import groupby

    total_geral = 0.0

    for cliente_nome, grupo_itens in groupby(titulos_ativos, key=lambda x: x["_nome_cliente"]):
        itens_cliente = list(grupo_itens)
        
        # Lista temporária para conter todos os elementos do cliente atual
        bloco_cliente = []

        # Cabeçalho do Grupo de Cliente
        bloco_cliente.append(Paragraph(f"Cliente: {cliente_nome}", cliente_heading_estilo))

        # Tabela do grupo
        dados_tabela = [
            [
                Paragraph("Nº DOC", celula_header_estilo),
                Paragraph("PARC", celula_header_estilo),
                Paragraph("VENCIMENTO", celula_header_estilo),
                Paragraph("CÓDIGO", celula_header_estilo),
                Paragraph("VALOR (R$)", celula_header_estilo)
            ]
        ]

        subtotal_cliente = 0.0

        for t in itens_cliente:
            cod_cli = str(t.get("cod_cfo"))
            num_doc = str(t.get("numero_documento"))
            parcela_val = str(t.get("parcela", "1"))
            
            venc_raw = t.get("data_vencimento")
            try:
                venc_fmt = datetime.strptime(venc_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                venc_fmt = venc_raw

            valor = float(t.get("valor_original", 0.0))
            subtotal_cliente += valor
            total_geral += valor

            dados_tabela.append([
                Paragraph(num_doc, celula_estilo),
                Paragraph(parcela_val, celula_estilo),
                Paragraph(venc_fmt, celula_estilo),
                Paragraph(cod_cli, celula_estilo),
                Paragraph(f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), celula_estilo)
            ])

        tabela = Table(dados_tabela, colWidths=[110, 55, 95, 75, 219])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('TOPPADDING', (1, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (1, 1), (-1, -1), 4),
        ]))

        bloco_cliente.append(tabela)

        # Linha de Subtotal do Cliente
        subtotal_estilo = ParagraphStyle(
            'SubtotalEstilo',
            parent=estilos['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.HexColor('#374151'),
            alignment=2,
            spaceBefore=4,
            spaceAfter=10
        )
        sub_str = f"Subtotal do Cliente: R$ {subtotal_cliente:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        bloco_cliente.append(Paragraph(sub_str, subtotal_estilo))

        # O KeepTogether garante que o nome do cliente, a tabela e o subtotal fiquem juntos na mesma página
        elementos.append(KeepTogether(bloco_cliente))

    elementos.append(Spacer(1, 10))

    # Resumo Total Geral da Carteira
    resumo_estilo = ParagraphStyle(
        'ResumoEstilo',
        parent=estilos['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#1f2937'),
        alignment=2
    )
    total_str = f"VALOR TOTAL DA CARTEIRA: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elementos.append(Paragraph(total_str, resumo_estilo))

    doc.build(elementos)

    try:
        os.startfile(caminho_pdf)
    except Exception:
        pass

    return str(caminho_pdf), None