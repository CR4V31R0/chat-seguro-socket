import json
import struct
from seguranca.criptografia import criptografar_bytes, descriptografar_bytes


def enviar_pacote(conexao, dados):
    """
    Serializa o dicionário em JSON, criptografa e envia com cabeçalho de tamanho.
    """
    texto_json = json.dumps(dados, ensure_ascii=False)
    dados_bytes = texto_json.encode("utf-8")
    dados_criptografados = criptografar_bytes(dados_bytes)

    tamanho = len(dados_criptografados)
    cabecalho = struct.pack("!I", tamanho)

    conexao.sendall(cabecalho + dados_criptografados)


def receber_exatamente(conexao, quantidade):
    """
    Lê exatamente 'quantidade' bytes do socket.
    """
    dados = b""

    while len(dados) < quantidade:
        pacote = conexao.recv(quantidade - len(dados))

        if not pacote:
            return None

        dados += pacote

    return dados


def receber_pacote(conexao):
    """
    Lê cabeçalho de tamanho, depois lê os dados criptografados,
    descriptografa e transforma em dicionário Python.
    """
    cabecalho = receber_exatamente(conexao, 4)

    if cabecalho is None:
        return None

    tamanho = struct.unpack("!I", cabecalho)[0]

    dados_criptografados = receber_exatamente(conexao, tamanho)

    if dados_criptografados is None:
        return None

    dados_bytes = descriptografar_bytes(dados_criptografados)
    texto_json = dados_bytes.decode("utf-8")

    return json.loads(texto_json)