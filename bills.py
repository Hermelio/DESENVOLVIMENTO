# Importa todas as funções e classes do módulo barcode_read
from barcode_read import *
# Importa a classe Imbox para manipulação de emails
from imbox import Imbox
# Importa as classes datetime e timedelta para manipulação de datas e horas
from datetime import datetime, timedelta
# Importa o módulo pandas para manipulação e análise de dados
import pandas as pd
# Importa o módulo uuid para geração de identificadores únicos
import uuid
# Importa a classe Workbook do módulo openpyxl para criação e manipulação de arquivos Excel
from openpyxl import Workbook
import os
import json
import fitz  # PyMuPDF para verificar se o PDF está protegido



# Caminhos para credenciais e corpo do e-mail
# CREDENTIONS_PATH = os.path.join(os.path.dirname(__file__), 'credencial.json')
# Definir __file__ se não estiver disponível
# Obtém o diretório base onde está o script
# Obtém o diretório onde está rodando o script
base_dir = os.path.dirname(os.path.abspath(__file__))  

# Define pasta para boletos protegidos por senha
boletos_protegidos_folder = os.path.join(base_dir, "boletos_protegidos")

# Criar a pasta de boletos protegidos se ela não existir
if not os.path.exists(boletos_protegidos_folder):
    os.makedirs(boletos_protegidos_folder)



# Verifique se `base_dir` já contém `AUTOMACAO EMAILS`
if "AUTOMACAO EMAILS" in base_dir:
    CREDENTIONS_PATH = os.path.join(base_dir, "credencial.json")  # Apenas o nome do arquivo
else:
    CREDENTIONS_PATH = os.path.join(base_dir, "AUTOMACAO EMAILS", "credencial.json")  # Inclui a pasta

# Verifica se o arquivo realmente existe antes de abrir
if not os.path.exists(CREDENTIONS_PATH):
    raise FileNotFoundError(f"Arquivo credencial.json não encontrado: {CREDENTIONS_PATH}")


# Carrega credenciais
with open(CREDENTIONS_PATH, 'r', encoding='utf-8') as file:
    credential_data = json.load(file)

#Mapeando as credenciais
email = credential_data['email']
password = credential_data['google_password']
host = 'imap.gmail.com'

# Define o caminho para a pasta 'boletos' dentro de 'AUTOMACAO EMAILS'
boletos_folder = os.path.join(base_dir, "boletos")
outros_pdfs_folder = os.path.join(base_dir, "outros_pdfs")  # Pasta para PDFs sem código de barras


# Criar a pasta 'boletos' se ela não existir
for folder in [boletos_folder, outros_pdfs_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

mail = Imbox(host,username=email,password=password, ssl=True)
messages = mail.messages(date__gt=datetime.today() - timedelta(days=30), raw="has:attachment")

# Processar os e-mails
for (uid, message) in messages:
    for attach in message.attachments:
        att_file = attach['filename']
        
        if '.pdf' in att_file:
            print(message.subject, '-', att_file)

            unique_filename = str(uuid.uuid4()) + ".pdf"  # Adiciona extensão ao nome do arquivo
            
            # Caminho temporário antes da verificação
            temp_path = os.path.join(base_dir, unique_filename)

            # Salvar o anexo temporariamente
            with open(temp_path, 'wb') as file:
                file.write(attach['content'].read())

            try:
                # Verifica se o PDF está protegido por senha
                with fitz.open(temp_path) as doc:
                    if doc.is_encrypted:
                        print(f"🔒 O arquivo {att_file} está protegido por senha e não pode ser processado.")
                        final_path = os.path.join(boletos_protegidos_folder, unique_filename)
                        os.rename(temp_path, final_path)
                        print(f"📂 Arquivo movido para {final_path} para análise manual.")
                        continue  # Pula para o próximo arquivo

                # Ler o código de barras do PDF
                barcode = barcode_reader(temp_path)

                if barcode:
                    # Se houver código de barras, move para a pasta de boletos
                    final_path = os.path.join(boletos_folder, unique_filename)
                    os.rename(temp_path, final_path)

                    # Formatar o código de barras
                    barcode_format = formatar_linha_digitavel(barcode)
                    print(f"✅ Boleto detectado! Código formatado: {barcode_format}")

                else:
                    # Se NÃO for um boleto, move para a pasta de outros PDFs
                    final_path = os.path.join(outros_pdfs_folder, unique_filename)
                    os.rename(temp_path, final_path)
                    print(f"⚠️ PDF sem código de barras, movido para: {final_path}")

            except Exception as e:
                print(f"❌ Erro ao processar o arquivo {att_file}: {e}")

                # Em caso de erro, move para a pasta de erro para análise
                error_folder = os.path.join(base_dir, "pdfs_com_erro")
                if not os.path.exists(error_folder):
                    os.makedirs(error_folder)

                error_path = os.path.join(error_folder, unique_filename)
                os.rename(temp_path, error_path)
                print(f"📂 Arquivo movido para {error_path} para análise.")



