import socket
import threading
import json
from pathlib import Path
from comum.protocolo import enviar_pacote, receber_pacote

HOST = "127.0.0.1"
PORTA = 5000

clientes_conectados = {}
trava_clientes = threading.Lock()

CAMINHO_USUARIOS = Path(__file__).resolve().parent.parent / "dados" / "usuarios.json"


def carregar_usuarios():
    with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


usuarios = carregar_usuarios()


def enviar_para_um_cliente(conexao, dados):
    try:
        enviar_pacote(conexao, dados)
    except Exception:
        pass


def enviar_para_todos(dados):
    conexoes_para_remover = []

    with trava_clientes:
        for conexao in list(clientes_conectados.keys()):
            try:
                enviar_pacote(conexao, dados)
            except Exception:
                conexoes_para_remover.append(conexao)

        for conexao in conexoes_para_remover:
            remover_cliente(conexao)


def remover_cliente(conexao):
    with trava_clientes:
        if conexao in clientes_conectados:
            usuario = clientes_conectados[conexao]
            del clientes_conectados[conexao]

            try:
                conexao.close()
            except Exception:
                pass

            print(f"[DESCONECTADO] {usuario}")

            enviar_para_todos({
                "tipo": "sistema",
                "texto": f"{usuario} saiu do chat."
            })


def autenticar_usuario(dados_login):
    if dados_login is None:
        return False, None

    if dados_login.get("tipo") != "login":
        return False, None

    usuario = dados_login.get("usuario", "").strip()
    senha = dados_login.get("senha", "").strip()

    if usuario in usuarios and usuarios[usuario] == senha:
        return True, usuario

    return False, usuario


def tratar_cliente(conexao, endereco):
    print(f"[NOVA CONEXÃO] Cliente conectado: {endereco}")

    try:
        dados_login = receber_pacote(conexao)
        autenticado, usuario = autenticar_usuario(dados_login)

        if not autenticado:
            enviar_para_um_cliente(conexao, {
                "tipo": "login",
                "status": "falha",
                "mensagem": "Usuário ou senha inválidos."
            })
            conexao.close()
            print(f"[LOGIN FALHOU] Endereço: {endereco}")
            return

        with trava_clientes:
            clientes_conectados[conexao] = usuario

        enviar_para_um_cliente(conexao, {
            "tipo": "login",
            "status": "ok",
            "mensagem": f"Bem-vindo, {usuario}!"
        })

        print(f"[LOGIN OK] {usuario} autenticado com sucesso.")

        enviar_para_todos({
            "tipo": "sistema",
            "texto": f"{usuario} entrou no chat."
        })

        while True:
            dados = receber_pacote(conexao)

            if dados is None:
                break

            tipo = dados.get("tipo")

            if tipo == "mensagem":
                texto = dados.get("texto", "").strip()

                if texto == "":
                    continue

                print(f"[MENSAGEM] {usuario}: {texto}")

                enviar_para_todos({
                    "tipo": "mensagem",
                    "remetente": usuario,
                    "texto": texto
                })

            elif tipo == "sair":
                print(f"[SAÍDA] {usuario} encerrou a conexão.")
                break

    except Exception as erro:
        print(f"[ERRO] Problema com o cliente {endereco}: {erro}")

    finally:
        remover_cliente(conexao)


def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORTA))
    servidor.listen()

    print(f"Servidor iniciado em {HOST}:{PORTA}")
    print("Aguardando conexões...")

    while True:
        conexao, endereco = servidor.accept()

        thread_cliente = threading.Thread(
            target=tratar_cliente,
            args=(conexao, endereco),
            daemon=True
        )
        thread_cliente.start()


if __name__ == "__main__":
    iniciar_servidor()