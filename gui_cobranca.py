import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import sys

# Adiciona a pasta utils ao path
sys.path.append(str(Path(__file__).parent / "utils"))
from relatorio import gerar_relatorio_cobranca_pdf
from gerenciar_cobranca import JanelaGerenciarCobranca

class JanelaCobranca:
    def __init__(self, root):
        self.root = root
        self.root.title("GERENCIAMENTO DE COBRANÇAS")
        self.root.geometry("500x420")
        self.root.resizable(False, False)
        
        self.criar_componentes()

    def criar_componentes(self):
        lbl_titulo = tk.Label(self.root, text="CENTRAL DE COBRANÇA", font=("Arial", 16, "bold"))
        lbl_titulo.pack(pady=20)

        # Botão: Emitir Relatório
        btn_relatorio = tk.Button(
            self.root,
            text="Emitir Relatório de Títulos",
            font=("Arial", 11),
            width=30,
            height=2,
            bg="#2563eb",
            fg="white",
            command=self.acao_emitir_relatorio
        )
        btn_relatorio.pack(pady=10)

        # Botão: Gerenciar Cobrança
        btn_gerenciar = tk.Button(
            self.root,
            text="Gerenciar Cobrança",
            font=("Arial", 11),
            width=30,
            height=2,
            bg="#059669",
            fg="white",
            command=self.acao_gerenciar_cobranca
        )
        btn_gerenciar.pack(pady=10)

        # Botão Fechar
        btn_fechar = tk.Button(
            self.root,
            text="Voltar ao Menu Principal",
            font=("Arial", 10),
            width=25,
            command=self.root.destroy
        )
        btn_fechar.pack(pady=20)

    def acao_emitir_relatorio(self):
        caminho_pdf, erro = gerar_relatorio_cobranca_pdf()
        if erro:
            messagebox.showwarning("Aviso", erro, parent=self.root)
        # Removido o messagebox de sucesso com o caminho, abrindo direto o PDF

    def acao_gerenciar_cobranca(self):
        """Abre a janela de gerenciamento por clientes."""
        JanelaGerenciarCobranca(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = JanelaCobranca(root)
    root.mainloop()