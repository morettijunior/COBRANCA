import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import sys
from datetime import datetime

from utils import bd

class AppCobranca:
    def __init__(self, root):
        self.root = root
        self.root.title("COBRANÇA DE CLIENTES")
        self.root.geometry("450x3905" if False else "450x380")
        self.root.resizable(False, False)
        
        self.criar_componentes()

    def criar_componentes(self):
        # Título Principal com Versão 1.0.0
        lbl_titulo = tk.Label(self.root, text="COBRANÇA DE CLIENTES", font=("Arial", 16, "bold"))
        lbl_titulo.pack(pady=(20, 2))

        lbl_versao = tk.Label(self.root, text="Versão 1.0.0", font=("Arial", 9, "italic"), fg="#6b7280")
        lbl_versao.pack(pady=(0, 15))

        # Botão: Configuração
        btn_config = tk.Button(
            self.root, 
            text="Configuração", 
            font=("Arial", 11), 
            width=25, 
            height=2, 
            command=self.abrir_configuracao
        )
        btn_config.pack(pady=8)

        # Botão: Receber Dados
        btn_receber = tk.Button(
            self.root, 
            text="Receber Dados", 
            font=("Arial", 11), 
            width=25, 
            height=2, 
            command=self.executar_receber_dados
        )
        btn_receber.pack(pady=8)

        # Botão: Cobrança
        btn_cobranca = tk.Button(
            self.root, 
            text="Cobrança", 
            font=("Arial", 11), 
            width=25, 
            height=2, 
            command=self.abrir_cobranca
        )
        btn_cobranca.pack(pady=8)

        # Botão discreto de Versionamento no Rodapé
        btn_sobre = tk.Button(
            self.root,
            text="v1.0.0 - Histórico de Versões",
            font=("Arial", 8),
            fg="#4b5563",
            bd=0,
            cursor="hand2",
            relief="flat",
            command=self.abrir_historico_versoes
        )
        btn_sobre.pack(pady=(12, 10))

    def abrir_configuracao(self):
        """Abre a janela de configurações preenchendo com os dados salvos em Meus Documentos."""
        from tkinter import filedialog
        from utils import config

        janela_config = tk.Toplevel(self.root)
        janela_config.title("Configurações do Sistema")
        janela_config.geometry("560x650")
        janela_config.grab_set()

        # Canvas com Scrollbar para acomodar todos os campos de configuração com conforto
        canvas_cfg = tk.Canvas(janela_config, bg="#f3f4f6")
        scrollbar_cfg = tk.Scrollbar(janela_config, orient="vertical", command=canvas_cfg.yview)
        scroll_frame_cfg = tk.Frame(canvas_cfg, bg="#f3f4f6")

        scroll_frame_cfg.bind("<Configure>", lambda e: canvas_cfg.configure(scrollregion=canvas_cfg.bbox("all")))
        canvas_cfg.create_window((0, 0), window=scroll_frame_cfg, anchor="nw")
        canvas_cfg.configure(yscrollcommand=scrollbar_cfg.set)

        canvas_cfg.pack(side="left", fill="both", expand=True)
        scrollbar_cfg.pack(side="right", fill="y")

        # 1. Seção Operador
        tk.Label(scroll_frame_cfg, text="Nome de quem está cobrando:", font=("Arial", 9, "bold"), bg="#f3f4f6").pack(anchor="w", padx=20, pady=(15, 2))
        entry_operador = tk.Entry(scroll_frame_cfg, font=("Arial", 9), width=50)
        entry_operador.pack(anchor="w", padx=20)
        entry_operador.insert(0, config.nome)

        # 2. Seção Assinatura de E-mail
        tk.Label(scroll_frame_cfg, text="Imagem de Assinatura (para e-mails):", font=("Arial", 9, "bold"), bg="#f3f4f6").pack(anchor="w", padx=20, pady=(12, 2))
        frame_assinatura = tk.Frame(scroll_frame_cfg, bg="#f3f4f6")
        frame_assinatura.pack(anchor="w", padx=20, fill="x")
        
        entry_assinatura = tk.Entry(frame_assinatura, font=("Arial", 9), width=38)
        entry_assinatura.pack(side="left", padx=(0, 5))
        entry_assinatura.insert(0, config.assinatura_path)

        def procurar_assinatura():
            arquivo_img = filedialog.askopenfilename(
                title="Selecionar Imagem de Assinatura",
                filetypes=[("Imagens PNG/JPG", "*.png *.jpg *.jpeg"), ("Todos los arquivos", "*.*")],
                parent=janela_config
            )
            if arquivo_img:
                entry_assinatura.delete(0, tk.END)
                entry_assinatura.insert(0, arquivo_img)

        tk.Button(frame_assinatura, text="Procurar...", font=("Arial", 9), command=procurar_assinatura).pack(side="left")

        # 3. Seção Credenciais de E-mail
        tk.Label(scroll_frame_cfg, text="E-mail Remetente:", font=("Arial", 9, "bold"), bg="#f3f4f6").pack(anchor="w", padx=20, pady=(12, 2))
        entry_email_rem = tk.Entry(scroll_frame_cfg, font=("Arial", 9), width=50)
        entry_email_rem.pack(anchor="w", padx=20)
        entry_email_rem.insert(0, config.email_remetente)

        tk.Label(scroll_frame_cfg, text="Senha do E-mail:", font=("Arial", 9, "bold"), bg="#f3f4f6").pack(anchor="w", padx=20, pady=(8, 2))
        entry_email_sen = tk.Entry(scroll_frame_cfg, font=("Arial", 9), width=50, show="*")
        entry_email_sen.pack(anchor="w", padx=20)
        entry_email_sen.insert(0, config.email_senha)

        # 4. Seção WhatsApp (Evolution API)
        tk.Label(scroll_frame_cfg, text="WhatsApp - URL Base (Evolution API):", font=("Arial", 9, "bold"), bg="#f3f4f6").pack(anchor="w", padx=20, pady=(12, 2))
        entry_whats_url = tk.Entry(scroll_frame_cfg, font=("Arial", 9), width=50)
        entry_whats_url.pack(anchor="w", padx=20)
        entry_whats_url.insert(0, config.whats_url)

        tk.Label(scroll_frame_cfg, text="WhatsApp - Instância:", font=("Arial", 9, "bold"), bg="#f3f4f6").pack(anchor="w", padx=20, pady=(8, 2))
        entry_whats_inst = tk.Entry(scroll_frame_cfg, font=("Arial", 9), width=50)
        entry_whats_inst.pack(anchor="w", padx=20)
        entry_whats_inst.insert(0, config.whats_instance)

        tk.Label(scroll_frame_cfg, text="WhatsApp - API Key / Token:", font=("Arial", 9, "bold"), bg="#f3f4f6").pack(anchor="w", padx=20, pady=(8, 2))
        entry_whats_key = tk.Entry(scroll_frame_cfg, font=("Arial", 9), width=50, show="*")
        entry_whats_key.pack(anchor="w", padx=20)
        entry_whats_key.insert(0, config.whats_apikey)

        # 5. Seção Feriados
        tk.Label(scroll_frame_cfg, text="Feriados (DD/MM/AAAA, separados por vírgula):", font=("Arial", 9, "bold"), bg="#f3f4f6").pack(anchor="w", padx=20, pady=(12, 2))
        text_feriados = tk.Text(scroll_frame_cfg, font=("Arial", 9), width=48, height=4)
        text_feriados.pack(anchor="w", padx=20)
        
        if hasattr(config, "feriados") and config.feriados:
            feriados_ordenados = sorted(list(config.feriados))
            str_feriados_atuais = ", ".join([d.strftime("%d/%m/%Y") for d in feriados_ordenados])
            text_feriados.insert("1.0", str_feriados_atuais)

        def salvar_config():
            feriados_bruto = text_feriados.get("1.0", tk.END).strip()
            datas_lista = [d.strip() for d in feriados_bruto.split(",") if d.strip()]
            datas_validas = []
            
            for data_str in datas_lista:
                try:
                    datetime.strptime(data_str, "%d/%m/%Y")
                    datas_validas.append(data_str)
                except ValueError:
                    messagebox.showerror("Erro de Formato", f"A data '{data_str}' está inválida.\nUse o formato DD/MM/AAAA.", parent=janela_config)
                    return

            novos_dados = {
                "nome": entry_operador.get().strip(),
                "assinatura_path": entry_assinatura.get().strip(),
                "email_remetente": entry_email_rem.get().strip(),
                "email_senha": entry_email_sen.get().strip(),
                "whats_url": entry_whats_url.get().strip(),
                "whats_instance": entry_whats_inst.get().strip(),
                "whats_apikey": entry_whats_key.get().strip(),
                "feriados": datas_validas
            }

            config.salvar_configuracoes(novos_dados)
            messagebox.showinfo("Sucesso", "Configurações salvas e persistidas com sucesso!", parent=janela_config)
            janela_config.destroy()

        btn_salvar = tk.Button(scroll_frame_cfg, text="Salvar Configurações", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", width=25, height=2, command=salvar_config)
        btn_salvar.pack(pady=20)

    def executar_receber_dados(self):
        """Executa a rotina de sincronização do banco de dados importando o módulo bd."""
        try:
            if hasattr(bd, "sincronizar_dados"):
                bd.sincronizar_dados()
            elif hasattr(bd, "main"):
                bd.main()
            messagebox.showinfo("Sucesso", "Dados recebidos e arquivos JSON atualizados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao sincronizar os dados:\n{e}")

    def abrir_cobranca(self):
        """Abre a central de cobranças."""
        from gui_cobranca import JanelaCobranca
        nova_janela = tk.Toplevel(self.root)
        JanelaCobranca(nova_janela)

    def abrir_historico_versoes(self):
        """Abre uma janela limpa exibindo o histórico de versionamento do sistema."""
        janela_sobre = tk.Toplevel(self.root)
        janela_sobre.title("Histórico de Versões")
        janela_sobre.geometry("440x380")
        janela_sobre.resizable(False, False)
        janela_sobre.grab_set()

        tk.Label(janela_sobre, text="Histórico de Atualizações", font=("Arial", 12, "bold")).pack(pady=(15, 10))

        # Caixa de texto com barra de rolando contendo o histórico
        txt_historico = tk.Text(janela_sobre, font=("Arial", 9), wrap="word", padx=10, pady=10)
        txt_historico.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        historico_conteudo = (
            "v1.0.0 (Novembro/2026)\n"
            "• Lançamento oficial da versão estável.\n"
            "• Integração completa com ERP TGA (Firebird) e persistência local em Meus Documentos.\n"
            "• Suporte a disparos automáticos via E-mail e WhatsApp (Evolution API).\n"
            "• Gerenciamento de Clientes de Cobrança Comum e Cobrança Especial (Jurídico).\n"
            "• Filtro de títulos ativos e relatórios em PDF otimizados.\n"
            "• Compilação nativa em executável otimizada via PyInstaller."
        )

        txt_historico.insert("1.0", historico_conteudo)
        txt_historico.config(state="disabled")  # Torna o texto apenas leitura

        btn_fechar = tk.Button(janela_sobre, text="Fechar", font=("Arial", 9), width=15, command=janela_sobre.destroy)
        btn_fechar.pack(pady=(0, 15))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppCobranca(root)
    root.mainloop()