import base64
import hashlib
from cryptography.fernet import Fernet

# Frase secreta fixa do projeto.
# A chave AES usada pelo Fernet será derivada dela.
FRASE_SECRETA = "chat_seguro_infra_redes_2025"

# Gera sempre a mesma chave a partir da frase acima.
CHAVE_COMPARTILHADA = base64.urlsafe_b64encode(
    hashlib.sha256(FRASE_SECRETA.encode("utf-8")).digest()
)

cifra = Fernet(CHAVE_COMPARTILHADA)


def criptografar_bytes(dados_bytes):
    return cifra.encrypt(dados_bytes)


def descriptografar_bytes(dados_criptografados):
    return cifra.decrypt(dados_criptografados)