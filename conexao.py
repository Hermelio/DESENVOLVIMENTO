import os
import json
from imbox import Imbox  
from datetime import datetime


CREDENTIONS_PATH = os.path.join(os.path.dirname(__file__), 'credencial.json')

print(f"Buscando arquivo em: {CREDENTIONS_PATH}")  # Isso ajuda a depurar

# Verifica se o arquivo existe antes de abrir
if not os.path.exists(CREDENTIONS_PATH):
    raise FileNotFoundError(f"Arquivo não encontrado: {CREDENTIONS_PATH}")

with open(CREDENTIONS_PATH, 'r', encoding='utf-8') as file:
    credential_data = json.load(file)

host = 'imap.gmail.com'
email = credential_data['email']
password = credential_data['google_password']

with Imbox(host, username=email, password=password) as imbox:
    messages = imbox.messages(unread=True)

    if not messages:
        print("Não conseguimos extrair mensagens.")
        quit()

    print('Temos mensagens ---------------------')


    # Marcar todas as mensagens como lidas de uma vez só
    for uid, message in messages:
        imbox.mark_seen(uid)
        print(f"De: {message.sent_from}")
        print(f"Para: {message.sent_to}")
        print(f"Assunto: {message.subject}")
        print(f"Data: {message.date}")
        print(f"Corpo: {message.body['plain']}")
        print('-----------------------------------')



