from email.message import EmailMessage
import ssl
import smtplib
import os
import json

# Caminhos para credenciais e corpo do e-mail
CREDENTIONS_PATH = os.path.join(os.path.dirname(__file__), 'credencial.json')
CORPO2 = os.path.join(os.path.dirname(__file__), 'corpo1_html.txt')

# Configuração correta do host SMTP (para envio)
host = 'smtp.gmail.com'

# Carrega credenciais
with open(CREDENTIONS_PATH, 'r', encoding='utf-8') as file:
    credential_data = json.load(file)

#Mapeando as credenciais
email = credential_data['email']
password = credential_data['google_password']

# Lê corpo do e-mail
with open(CORPO2, 'r', encoding='utf-8') as f:
    body = f.read()

# Configuração do e-mail
email_destino = 'hermelio.ifma@gmail.com'
assunto = 'Testando envio de email'

mensagem = EmailMessage()
mensagem["From"] = email
mensagem["To"] = email_destino
mensagem["Subject"] = assunto
mensagem.set_content(body, subtype='html')

# Conexão segura
safe = ssl.create_default_context()

# Envia o e-mail
with smtplib.SMTP_SSL(host, 465, context=safe) as smtp:
    smtp.login(email, password)
    smtp.sendmail(email, email_destino, mensagem.as_string())

print("E-mail enviado com sucesso!")
