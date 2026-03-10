import socket
import threading
import queue
import tkinter as tk
from tkinter import messagebox, scrolledtext
from comum.protocolo import enviar_pacote, receber_pacote

HOST = "127.0.0.1"
PORTA = 5000


class AplicacaoChat:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Chat Seguro")
        self.janela.geometry("700x500")
        self.janela.resizable(False, False)

        self.conexao = None
        self.usuario = None
        self.fila_interface = queue.Queue()
        self.conectado = False

        self.criar_tela_login()
        self.janela.protocol("WM_DELETE_WINDOW", self.ao_fechar_janela)
        self.atualizar_interface()
        self.janela.mainloop()

    def criar_tela_login(self):
        self.quadro_login = tk.Frame(self.janela, padx=20, pady=20)
        self.quadro_login.pack(fill="both", expand=True)

        titulo = tk.Label(
            self.quadro_login,
            text="Acesso ao Chat Seguro",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        tk.Label(self.quadro_login, text="Usuário:", font=("Arial", 11)).pack(pady=(20, 5))
        self.campo_usuario = tk.Entry(self.quadro_login, font=("Arial", 11), width=30)
        self.campo_usuario.pack()

        tk.Label(self.quadro_login, text="Senha:", font=("Arial", 11)).pack(pady=(15, 5))
        self.campo_senha = tk.Entry(self.quadro_login, font=("Arial", 11), show="*", width=30)
        self.campo_senha.pack()

        self.botao_entrar = tk.Button(
            self.quadro_login,
            text="Entrar",
            font=("Arial", 11, "bold"),
            width=15,
            command=self.realizar_login
        )
        self.botao_entrar.pack(pady=20)

        self.janela.bind("<Return>", self.realizar_login_por_enter)

    def criar_tela_chat(self):
        self.quadro_login.destroy()

        self.quadro_chat = tk.Frame(self.janela, padx=10, pady=10)
        self.quadro_chat.pack(fill="both", expand=True)

        self.rotulo_topo = tk.Label(
            self.quadro_chat,
            text=f"Usuário conectado: {self.usuario}",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        self.rotulo_topo.pack(fill="x", pady=(0, 8))

        self.area_chat = scrolledtext.ScrolledText(
            self.quadro_chat,
            font=("Arial", 11),
            state="disabled",
            wrap="word"
        )
        self.area_chat.pack(fill="both", expand=True)

        quadro_envio = tk.Frame(self.quadro_chat)
        quadro_envio.pack(fill="x", pady=(10, 0))

        self.campo_mensagem = tk.Entry(quadro_envio, font=("Arial", 11))
        self.campo_mensagem.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.campo_mensagem.bind("<Return>", self.enviar_mensagem_por_enter)

        self.botao_enviar = tk.Button(
            quadro_envio,
            text="Enviar",
            font=("Arial", 11, "bold"),
            width=10,
            command=self.enviar_mensagem
        )
        self.botao_enviar.pack(side="right")

        self.campo_mensagem.focus()

    def realizar_login_por_enter(self, event):
        self.realizar_login()

    def realizar_login(self):
        usuario = self.campo_usuario.get().strip()
        senha = self.campo_senha.get().strip()

        if usuario == "" or senha == "":
            messagebox.showwarning("Aviso", "Preencha usuário e senha.")
            return

        try:
            self.conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conexao.connect((HOST, PORTA))

            enviar_pacote(self.conexao, {
                "tipo": "login",
                "usuario": usuario,
                "senha": senha
            })

            resposta = receber_pacote(self.conexao)

            if resposta is None:
                messagebox.showerror("Erro", "Servidor não respondeu.")
                self.conexao.close()
                return

            if resposta.get("tipo") == "login" and resposta.get("status") == "ok":
                self.usuario = usuario
                self.conectado = True
                self.criar_tela_chat()
                self.adicionar_texto_chat("[SISTEMA] Login realizado com sucesso.")

                thread_recebimento = threading.Thread(
                    target=self.receber_mensagens,
                    daemon=True
                )
                thread_recebimento.start()
            else:
                mensagem = resposta.get("mensagem", "Falha no login.")
                messagebox.showerror("Erro de autenticação", mensagem)
                self.conexao.close()

        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor.\n\n{erro}")

    def receber_mensagens(self):
        while self.conectado:
            try:
                dados = receber_pacote(self.conexao)

                if dados is None:
                    self.fila_interface.put(("sistema", "Conexão encerrada pelo servidor."))
                    self.conectado = False
                    break

                tipo = dados.get("tipo")

                if tipo == "mensagem":
                    remetente = dados.get("remetente", "Desconhecido")
                    texto = dados.get("texto", "")
                    self.fila_interface.put(("mensagem", f"{remetente}: {texto}"))

                elif tipo == "sistema":
                    texto = dados.get("texto", "")
                    self.fila_interface.put(("sistema", texto))

            except Exception:
                if self.conectado:
                    self.fila_interface.put(("sistema", "Conexão perdida com o servidor."))
                self.conectado = False
                break

    def enviar_mensagem_por_enter(self, event):
        self.enviar_mensagem()

    def enviar_mensagem(self):
        if not self.conectado:
            return

        texto = self.campo_mensagem.get().strip()

        if texto == "":
            return

        if texto.lower() == "/sair":
            try:
                enviar_pacote(self.conexao, {"tipo": "sair"})
            except Exception:
                pass

            try:
                self.conexao.close()
            except Exception:
                pass

            self.conectado = False
            self.janela.destroy()
            return

        try:
            enviar_pacote(self.conexao, {
                "tipo": "mensagem",
                "texto": texto
            })

            self.campo_mensagem.delete(0, tk.END)

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível enviar a mensagem.\n\n{erro}"
            )

    def adicionar_texto_chat(self, texto):
        self.area_chat.configure(state="normal")
        self.area_chat.insert(tk.END, texto + "\n")
        self.area_chat.see(tk.END)
        self.area_chat.configure(state="disabled")

    def atualizar_interface(self):
        try:
            while True:
                tipo, texto = self.fila_interface.get_nowait()

                if tipo == "mensagem":
                    self.adicionar_texto_chat(texto)
                elif tipo == "sistema":
                    self.adicionar_texto_chat("[SISTEMA] " + texto)

        except queue.Empty:
            pass

        self.janela.after(100, self.atualizar_interface)

    def ao_fechar_janela(self):
        try:
            if self.conexao and self.conectado:
                enviar_pacote(self.conexao, {"tipo": "sair"})
        except Exception:
            pass

        try:
            if self.conexao:
                self.conexao.close()
        except Exception:
            pass

        self.conectado = False
        self.janela.destroy()


if __name__ == "__main__":
    AplicacaoChat()