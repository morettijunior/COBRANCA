import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import json
from datetime import datetime
from modelos import ClienteCobranca, obter_pasta_titulos, obter_pasta_clientes, TituloCobranca
from enviar_email import enviar_email_cobranca_cliente
from enviar_whatsapp import enviar_whatsapp_cobranca_cliente

class JanelaGerenciarCobranca:
    def __init__(self, master):
        self.master = master
        self.janela = tk.Toplevel(master)
        self.janela.title("Gerenciamento de Clientes com Cobrança Ativa")
        self.janela.geometry("780x700")
        self.janela.grab_set()

        lbl_topo = tk.Label(self.janela, text="Selecione um cliente para gerenciar (Botão direito para Cobrança Especial):", font=("Arial", 11, "bold"))
        lbl_topo.pack(pady=10)

        # Container principal com scroll para toda a listagem de clientes
        self.canvas = tk.Canvas(self.janela, bg="#f3f4f6")
        self.scrollbar = tk.Scrollbar(self.janela, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f3f4f6")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y", pady=10)

        self.carregar_clientes_ativos()

    def carregar_clientes_ativos(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        pasta_titulos = obter_pasta_titulos()
        pasta_clientes = obter_pasta_clientes()

        if not pasta_titulos.exists():
            messagebox.showwarning("Aviso", "Nenhum título encontrado. Execute 'Receber Dados' primeiro.", parent=self.janela)
            return

        cods_clientes_ativos = set()
        titulos_por_cliente = {}

        for arquivo in pasta_titulos.glob("titulo_*.json"):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    if dados.get("ativo") == "S":
                        cod_cfo = str(dados.get("cod_cfo"))
                        cods_clientes_ativos.add(cod_cfo)
                        if cod_cfo not in titulos_por_cliente:
                            titulos_por_cliente[cod_cfo] = []
                        titulos_por_cliente[cod_cfo].append(dados)
            except Exception:
                pass

        if not cods_clientes_ativos:
            lbl_vazio = tk.Label(self.scrollable_frame, text="Nenhum cliente com títulos ativos no momento.", font=("Arial", 10), bg="#f3f4f6")
            lbl_vazio.pack(pady=20)
            return

        lista_comum = []
        lista_especial = []

        for cod_cfo in cods_clientes_ativos:
            arq_cli = pasta_clientes / f"cliente_{cod_cfo}.json"
            nome_cli = f"Cliente {cod_cfo}"
            is_especial = False

            if arq_cli.exists():
                try:
                    with open(arq_cli, 'r', encoding='utf-8') as f:
                        c_dados = json.load(f)
                        nome_cli = c_dados.get("nome_cliente", nome_cli)
                        is_especial = c_dados.get("cobranca_especial", False)
                except Exception:
                    pass

            cliente_info = {
                "cod_cfo": cod_cfo,
                "nome_cli": nome_cli,
                "titulos": titulos_por_cliente.get(cod_cfo, [])
            }

            if is_especial:
                lista_especial.append(cliente_info)
            else:
                lista_comum.append(cliente_info)

        lista_comum.sort(key=lambda x: x["nome_cli"].lower())
        lista_especial.sort(key=lambda x: x["nome_cli"].lower())

        # --- SEÇÃO 1: COBRANÇA COMUM ---
        lbl_secao_comum = tk.Label(self.scrollable_frame, text="📌 Cobranças Comuns", font=("Arial", 10, "bold"), fg="#1e293b", bg="#f3f4f6")
        lbl_secao_comum.pack(anchor="w", padx=10, pady=(5, 0))

        frame_comum = tk.Frame(self.scrollable_frame, bg="#f3f4f6")
        frame_comum.pack(fill="x", padx=5, pady=5)
        self.renderizar_grade_clientes(frame_comum, lista_comum, especial=False)

        # Se houver cobranças especiais, cria a faixa de separação e a seção inferior
        if lista_especial:
            # Faixa de separação visual
            separator = tk.Frame(self.scrollable_frame, bg="#cbd5e1", height=2)
            separator.pack(fill="x", padx=10, pady=15)

            lbl_secao_esp = tk.Label(self.scrollable_frame, text="⚖️ Cobranças Especiais (Jurídico / Outros)", font=("Arial", 10, "bold"), fg="#dc2626", bg="#f3f4f6")
            lbl_secao_esp.pack(anchor="w", padx=10, pady=(5, 0))

            frame_especial = tk.Frame(self.scrollable_frame, bg="#f3f4f6")
            frame_especial.pack(fill="x", padx=5, pady=5)
            self.renderizar_grade_clientes(frame_especial, lista_especial, especial=True)

    def renderizar_grade_clientes(self, parent_frame, lista_clientes, especial=False):
        if not lista_clientes:
            lbl_vazio = tk.Label(parent_frame, text="Nenhum cliente nesta categoria.", font=("Arial", 9, "italic"), fg="gray", bg="#f3f4f6")
            lbl_vazio.pack(anchor="w", padx=10, pady=5)
            return

        coluna = 0
        linha = 0
        max_colunas = 3

        # Frame interno para a grid
        grid_frame = tk.Frame(parent_frame, bg="#f3f4f6")
        grid_frame.pack(anchor="w")

        for cli in lista_clientes:
            cod_cfo = cli["cod_cfo"]
            nome_cli = cli["nome_cli"]
            titulos = cli["titulos"]

            # Cor de fundo do card: Branco para comum, avermelhado claro para especial
            bg_card = "#fff5f5" if especial else "white"
            borda_card = "#ef4444" if especial else "solid"
            relief_card = "solid" if especial else "solid"

            card = tk.Frame(grid_frame, bg=bg_card, bd=1, relief=relief_card, width=220, height=105)
            card.grid_propagate(False)
            card.grid(row=linha, column=coluna, padx=8, pady=8)

            # Destaca a bordinha se for especial (via cor do texto/rótulo)
            lbl_nome = tk.Label(card, text=nome_cli, font=("Arial", 10, "bold"), fg="#991b1b" if especial else "#111827", bg=bg_card, wraplength=200, justify="center")
            lbl_nome.pack(pady=(12, 4))

            qtd_titulos = len(titulos)
            lbl_qtd = tk.Label(card, text=f"{qtd_titulos} título(s) em aberto", font=("Arial", 8), fg="#b91c1c" if especial else "gray", bg=bg_card)
            lbl_qtd.pack(pady=(0, 8))

            # Associa eventos de clique esquerdo (abrir detalhes)
            for widget in (card, lbl_nome, lbl_qtd):
                widget.bind("<Button-1>", lambda e, c=cod_cfo, n=nome_cli: self.abrir_detalhes_cliente(c, n))
                # Botão direito abre o menu de contexto para alternar o tipo de cobrança
                widget.bind("<Button-3>", lambda e, c=cod_cfo, esp=especial: self.mostrar_menu_contexto(e, c, esp))

            coluna += 1
            if coluna >= max_colunas:
                coluna = 0
                linha += 1

    def mostrar_menu_contexto(self, event, cod_cfo, estado_atual):
        """Exibe o menu de contexto ao clicar com o botão direito no card do cliente."""
        menu = tk.Menu(self.janela, tearoff=0)
        
        if estado_atual:
            menu.add_command(label="Mover para Cobrança Comum", command=lambda: self.alterar_tipo_cobranca(cod_cfo, especial=False))
        else:
            menu.add_command(label="Mover para Cobrança Especial", command=lambda: self.alterar_tipo_cobranca(cod_cfo, especial=True))
            
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def alterar_tipo_cobranca(self, cod_cfo, especial):
        """Atualiza o status de cobrança especial do cliente no seu arquivo JSON."""
        cliente_obj = ClienteCobranca.carregar_json(cod_cfo)
        if not cliente_obj:
            cliente_obj = ClienteCobranca(cod_cfo=cod_cfo)
        
        # Salva a flag de cobrança especial
        cliente_obj.cobranca_especial = especial
        cliente_obj.salvar_json()
        
        # Recarrega a tela para atualizar as seções instantaneamente
        self.carregar_clientes_ativos()

    def obter_titulos_atualizados_cliente(self, cod_cfo):
        pasta_titulos = obter_pasta_titulos()
        titulos_cliente = []
        for arquivo in pasta_titulos.glob("titulo_*.json"):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    if str(dados.get("cod_cfo")) == str(cod_cfo) and dados.get("ativo") == "S":
                        titulos_cliente.append(dados)
            except Exception:
                pass
        return titulos_cliente

    def abrir_detalhes_cliente(self, cod_cfo, nome_cliente):
        if hasattr(self, "sub_janela") and self.sub_janela.winfo_exists():
            self.sub_janela.destroy()

        self.sub_janela = tk.Toplevel(self.janela)
        self.sub_janela.title(f"Cobrança: {nome_cliente}")
        self.sub_janela.geometry("700x780")
        self.sub_janela.transient(self.janela)
        self.sub_janela.grab_set()

        sub = self.sub_janela
        titulos = self.obter_titulos_atualizados_cliente(cod_cfo)

        cliente_obj = ClienteCobranca.carregar_json(cod_cfo)
        if not cliente_obj:
            cliente_obj = ClienteCobranca(cod_cfo=cod_cfo, nome_cliente=nome_cliente)

        tk.Label(sub, text=f"Cliente: {nome_cliente} (Cód: {cod_cfo})", font=("Arial", 11, "bold")).pack(anchor="w", padx=20, pady=(15, 5))

        # --- SEÇÃO DE CONTATOS PERSISTIDOS ---
        frame_contatos = tk.LabelFrame(sub, text=" Informações de Contato ", font=("Arial", 9, "bold"))
        frame_contatos.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_contatos, text="WhatsApp:", font=("Arial", 9)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        entry_whats = tk.Entry(frame_contatos, font=("Arial", 9), width=25)
        entry_whats.grid(row=0, column=1, padx=5, pady=5)
        entry_whats.insert(0, cliente_obj.whatsapp_cobranca)

        tk.Label(frame_contatos, text="E-mail:", font=("Arial", 9)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        entry_email = tk.Entry(frame_contatos, font=("Arial", 9), width=38)
        entry_email.grid(row=1, column=1, padx=5, pady=5)
        entry_email.insert(0, cliente_obj.email_cobranca)

        def salvar_contatos():
            cliente_obj.whatsapp_cobranca = entry_whats.get().strip()
            cliente_obj.email_cobranca = entry_email.get().strip()
            cliente_obj.salvar_json()
            messagebox.showinfo("Sucesso", "Contatos salvos e persistidos com sucesso!", parent=sub)

        btn_salvar_contatos = tk.Button(frame_contatos, text="Salvar Contatos", font=("Arial", 8, "bold"), command=salvar_contatos)
        btn_salvar_contatos.grid(row=0, column=2, rowspan=2, padx=10, pady=5)

        self.frame_historicos_container = tk.Frame(sub)
        self.frame_historicos_container.pack(fill="both", expand=True, padx=20, pady=5)

        self.atualizar_painel_historico(self.frame_historicos_container, titulos)

        # --- BOTÕES DE AÇÃO DE COBRANÇA ---
        frame_botoes = tk.Frame(sub)
        frame_botoes.pack(pady=15)

        def atualizar_interface_pos_acao():
            nonlocal titulos
            titulos = self.obter_titulos_atualizados_cliente(cod_cfo)
            for widget in self.frame_historicos_container.winfo_children():
                widget.destroy()
            self.atualizar_painel_historico(self.frame_historicos_container, titulos)
            self.carregar_clientes_ativos()

        def acao_whatsapp():
            w_num = entry_whats.get().strip()
            if not w_num:
                messagebox.showwarning("Aviso", "Preencha o número de WhatsApp do cliente.", parent=sub)
                return
            
            cliente_obj.whatsapp_cobranca = w_num
            cliente_obj.salvar_json()

            try:
                enviar_whatsapp_cobranca_cliente(cliente_obj, titulos)
                for t_dados in titulos:
                    t_obj = TituloCobranca.carregar_json(t_dados.get("numero_documento"), t_dados.get("parcela", 1), t_dados.get("cod_cfo"))
                    if t_obj:
                        t_obj.adicionar_historico(canal="WHATSAPP", status="ENVIADO", observacao=f"Mensagem enviada para {w_num}")
                        t_obj.salvar_json()

                messagebox.showinfo("Sucesso", f"Cobrança via WhatsApp enviada com sucesso para:\n{w_num}", parent=sub)
                atualizar_interface_pos_acao()
            except Exception as e:
                messagebox.showerror("Erro no Envio", f"Não foi possível enviar o WhatsApp:\n{e}", parent=sub)

        def acao_email():
            e_end = entry_email.get().strip()
            if not e_end:
                messagebox.showwarning("Aviso", "Preencha o e-mail do cliente.", parent=sub)
                return
            
            cliente_obj.email_cobranca = e_end
            cliente_obj.salvar_json()

            try:
                enviar_email_cobranca_cliente(cliente_obj, titulos)
                for t_dados in titulos:
                    t_obj = TituloCobranca.carregar_json(t_dados.get("numero_documento"), t_dados.get("parcela", 1), t_dados.get("cod_cfo"))
                    if t_obj:
                        t_obj.adicionar_historico(canal="EMAIL", status="ENVIADO", observacao=f"E-mail enviado para {e_end}")
                        t_obj.salvar_json()

                messagebox.showinfo("Sucesso", f"E-mail de cobrança enviado com sucesso para:\n{e_end}", parent=sub)
                atualizar_interface_pos_acao()
            except Exception as e:
                messagebox.showerror("Erro no Envio", f"Não foi possível enviar o e-mail:\n{e}", parent=sub)

        def acao_personalizado():
            sub_pers = tk.Toplevel(sub)
            sub_pers.title(f"Cobrança Personalizada - {nome_cliente}")
            sub_pers.geometry("450x300")
            sub_pers.transient(sub)
            sub_pers.grab_set()

            tk.Label(sub_pers, text="Digite a mensagem de cobrança personalizada:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
            text_msg = tk.Text(sub_pers, font=("Arial", 9), width=50, height=8)
            text_msg.pack(padx=20, pady=5)
            text_msg.focus()

            def gravar_personalizado():
                mensagem_digitada = text_msg.get("1.0", tk.END).strip()
                if not mensagem_digitada:
                    messagebox.showwarning("Aviso", "A mensagem não pode estar vazia.", parent=sub_pers)
                    return

                observacao_formatada = f'"{mensagem_digitada}"'
                try:
                    for t_dados in titulos:
                        t_obj = TituloCobranca.carregar_json(t_dados.get("numero_documento"), t_dados.get("parcela", 1), t_dados.get("cod_cfo"))
                        if t_obj:
                            t_obj.adicionar_historico(canal="PERSONALIZADO", status="REGISTRADO", observacao=observacao_formatada)
                            t_obj.salvar_json()

                    messagebox.showinfo("Sucesso", "Cobrança personalizada registrada em todos os documentos ativos!", parent=sub_pers)
                    sub_pers.destroy()
                    atualizar_interface_pos_acao()
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível gravar o histórico:\n{e}", parent=sub_pers)

            btn_gravar = tk.Button(sub_pers, text="Gravar no Histórico", font=("Arial", 9, "bold"), bg="#2563eb", fg="white", width=20, height=2, command=gravar_personalizado)
            btn_gravar.pack(pady=10)

        btn_whats = tk.Button(frame_botoes, text="Cobrar WhatsApp", font=("Arial", 9, "bold"), bg="#10b981", fg="white", width=16, height=2, command=acao_whatsapp)
        btn_whats.grid(row=0, column=0, padx=8)

        btn_email = tk.Button(frame_botoes, text="Cobrar E-mail", font=("Arial", 9, "bold"), bg="#3b82f6", fg="white", width=16, height=2, command=acao_email)
        btn_email.grid(row=0, column=1, padx=8)

        btn_pers = tk.Button(frame_botoes, text="Cobrar Personalizado", font=("Arial", 9, "bold"), bg="#6b7280", fg="white", width=18, height=2, command=acao_personalizado)
        btn_pers.grid(row=0, column=2, padx=8)

    def atualizar_painel_historico(self, container, titulos):
        todos_historicos = []
        ultimas_por_documento = {}

        for t in titulos:
            num_doc = t.get("numero_documento", "")
            parcela = t.get("parcela", "1")
            doc_chave = f"{num_doc}/{parcela}"

            hist_titulo = t.get("historico_cobrancas", [])
            if hist_titulo:
                hist_titulo_ordenado = sorted(hist_titulo, key=lambda x: x.get("data_hora", ""), reverse=True)
                ultima_h = hist_titulo_ordenado[0]
                
                dt_raw_ult = ultima_h.get("data_hora", "")
                try:
                    dt_obj_ult = datetime.strptime(dt_raw_ult.split(" ")[0], "%Y-%m-%d")
                    dt_fmt_ult = dt_obj_ult.strftime("%d/%m/%Y")
                except ValueError:
                    dt_fmt_ult = dt_raw_ult.split(" ")[0]

                canal_ult = ultima_h.get("canal", "").upper()
                obs_ult = ultima_h.get("observacao", "")
                
                if canal_ult == "PERSONALIZADO":
                    ultimas_por_documento[doc_chave] = f"{dt_fmt_ult} - DOC {doc_chave} - {obs_ult}"
                else:
                    detalhe_obs = obs_ult.replace("E-mail enviado para ", "").replace("Mensagem enviada para ", "")
                    ultimas_por_documento[doc_chave] = f"{dt_fmt_ult} - DOC {doc_chave} - COBRADO VIA {canal_ult} ({detalhe_obs})"

            for h in hist_titulo:
                dt_raw = h.get("data_hora", "")
                try:
                    dt_obj = datetime.strptime(dt_raw.split(" ")[0], "%Y-%m-%d")
                    dt_fmt = dt_obj.strftime("%d/%m/%Y")
                except ValueError:
                    dt_fmt = dt_raw.split(" ")[0]

                canal = h.get("canal", "").upper()
                obs = h.get("observacao", "")

                if canal == "PERSONALIZADO":
                    linha_formatada = f"{dt_fmt} - DOC {num_doc}/{parcela} - {obs}"
                else:
                    detalhe_obs = obs.replace("E-mail enviado para ", "").replace("Mensagem enviada para ", "")
                    linha_formatada = f"{dt_fmt} - DOC {num_doc}/{parcela} - COBRADO VIA {canal} ({detalhe_obs})"

                todos_historicos.append({
                    "data_hora": dt_raw,
                    "texto": linha_formatada
                })

        todos_historicos.sort(key=lambda x: x["data_hora"], reverse=True)

        frame_ultima = tk.LabelFrame(container, text=" Última Cobrança Realizada (Por Documento) ", font=("Arial", 9, "bold"), fg="#1d4ed8")
        frame_ultima.pack(fill="x", padx=0, pady=(2, 2))

        texto_ultimas = "\n".join(ultimas_por_documento.values()) if ultimas_por_documento else "Nenhuma cobrança registrada para os títulos ativos."
        lbl_ultima = tk.Label(frame_ultima, text=texto_ultimas, font=("Arial", 9, "bold"), justify="left", fg="#374151")
        lbl_ultima.pack(anchor="w", padx=10, pady=6)

        tk.Label(container, text="Histórico Completo:", font=("Arial", 9, "bold")).pack(anchor="w", padx=0, pady=(4, 2))
        
        text_historico = tk.Text(container, font=("Arial", 9), width=85, height=18)
        text_historico.pack(padx=0)
        text_historico.config(state="normal")
        
        if todos_historicos:
            text_historico.insert("1.0", "\n".join([h["texto"] for h in todos_historicos]))
        else:
            text_historico.insert("1.0", "Nenhum histórico registrado para os títulos deste cliente.")
        text_historico.config(state="disabled")