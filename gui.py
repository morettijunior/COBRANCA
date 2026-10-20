import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import subprocess
import sys
from datetime import datetime

# Adiciona a pasta 'utils' ao path do Python para conseguir importar os módulos de lá
sys.path.append(str(Path(__file__).parent / "utils"))

class AppCobranca:
    def __init__(self, root):
        self.root = root
        self.root.title("COBRANÇA DE CLIENTES")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        self.criar_componentes()

    def criar_componentes(self):
        # Título Principal
        lbl_titulo = tk.Label(self.root, text="COBRANÇA DE CLIENTES", font=("Arial", 16, "bold"))
        lbl_titulo.pack(pady=25)

        # Botão: Configuração
        btn_config = tk.Button(
            self.root, 
            text="Configuração", 
            font=("Arial", 11), 
            width=25, 
            height=2, 
            command=self.abrir_configuracao
        )
        btn_config.pack(pady=10)

        # Botão: Receber Dados
        btn_receber = tk.Button(
            self.root, 
            text="Receber Dados", 
            font=("Arial", 11), 
            width=25, 
            height=2, 
            command=self.executar_receber_dados
        )
        btn_receber.pack(pady=10)

        # Botão: Cobrança
        btn_cobranca = tk.Button(
            self.root, 
            text="Cobrança", 
            font=("Arial", 11), 
            width=25, 
            height=2, 
            command=self.abrir_cobranca
        )
        btn_cobranca.pack(pady=10)

    def abrir_configuracao(self):
        """Abre a janela de configurações preenchendo com os dados salvos em Meus Documentos."""
        import sys
        from pathlib import Path
        from tkinter import filedialog
        
        utils_path = Path(__file__).parent / "utils"
        if str(utils_path) not in sys.path:
            sys.path.append(str(utils_path))
            
        import config

        janela_config = tk.Toplevel(self.root)
        janela_config.title("Configurações do Sistema")
        janela_config.geometry("520x440")
        janela_config.grab_set()

        # Campo: Operador / Quem está cobrando
        tk.Label(janela_config, text="Nome de quem está cobrando:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        entry_operador = tk.Entry(janela_config, font=("Arial", 10), width=50)
        entry_operador.pack(anchor="w", padx=20)
        entry_operador.insert(0, config.nome)

        # Campo: Caminho da Imagem de Assinatura
        tk.Label(janela_config, text="Imagem de Assinatura (para e-mails):", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        frame_assinatura = tk.Frame(janela_config)
        frame_assinatura.pack(anchor="w", padx=20, fill="x")
        
        entry_assinatura = tk.Entry(frame_assinatura, font=("Arial", 9), width=38)
        entry_assinatura.pack(side="left", padx=(0, 5))
        entry_assinatura.insert(0, config.assinatura_path if hasattr(config, "assinatura_path") else "")

        def procurar_assinatura():
            arquivo_img = filedialog.askopenfilename(
                title="Selecionar Imagem de Assinatura",
                filetypes=[("Imagens PNG/JPG", "*.png *.jpg *.jpeg"), ("Todos os arquivos", "*.*")],
                parent=janela_config
            )
            if arquivo_img:
                entry_assinatura.delete(0, tk.END)
                entry_assinatura.insert(0, arquivo_img)

        btn_procurar = tk.Button(frame_assinatura, text="Procurar...", font=("Arial", 9), command=procurar_assinatura)
        btn_procurar.pack(side="left")
        
        # Campo: Feriados
        tk.Label(janela_config, text="Feriados (formato DD/MM/AAAA, separados por vírgula):", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        text_feriados = tk.Text(janela_config, font=("Arial", 9), width=55, height=4)
        text_feriados.pack(padx=20)
        
        if hasattr(config, "feriados") and config.feriados:
            feriados_ordenados = sorted(list(config.feriados))
            str_feriados_atuais = ", ".join([d.strftime("%d/%m/%Y") for d in feriados_ordenados])
            text_feriados.insert("1.0", str_feriados_atuais)

        def salvar_config():
            operador = entry_operador.get().strip()
            assinatura_path_val = entry_assinatura.get().strip()
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

            config.salvar_configuracoes(operador, assinatura_path_val, datas_validas)
            
            messagebox.showinfo("Sucesso", "Configurações salvas e persistidas com sucesso!", parent=janela_config)
            janela_config.destroy()

        btn_salvar = tk.Button(janela_config, text="Salvar Configurações", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=salvar_config)
        btn_salvar.pack(pady=15)

    def executar_receber_dados(self):
        """Executa o script utils/bd.py para atualizar os JSONs."""
        try:
            caminho_bd = Path("utils") / "bd.py"
            
            if not caminho_bd.exists():
                messagebox.showerror("Erro", f"O arquivo de banco de dados não foi encontrado em:\n{caminho_bd}")
                return

            resultado = subprocess.run([sys.executable, str(caminho_bd)], capture_output=True, text=True, check=True)
            
            messagebox.showinfo("Sucesso", "Dados recebidos e arquivos JSON atualizados com sucesso!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro de Execução", f"Ocorreu um erro ao rodar o script de banco:\n{e.stderr}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível executar a rotina: {e}")

    def abrir_cobranca(self):
        """Abre a janela secundária de gerenciamento de cobranças."""
        import subprocess
        import sys
        
        caminho_cobranca_gui = Path("gui_cobranca.py")
        if not caminho_cobranca_gui.exists():
            messagebox.showerror("Erro", "O arquivo gui_cobranca.py não foi encontrado na raiz.")
            return
            
        # Abre como um processo separado ou Toplevel
        subprocess.Popen([sys.executable, str(caminho_cobranca_gui)])

if __name__ == "__main__":
    root = tk.Tk()
    app = AppCobranca(root)
    root.mainloop()