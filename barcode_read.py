from pyzbar.pyzbar import decode
from pdf2image import convert_from_path
import os
import numpy as np
from PIL import ImageEnhance


def formatar_linha_digitavel(codigo_barras):
    """
    Converte o código de barras de 44 dígitos para a linha digitável de 48 dígitos.

    Exemplo:
    Entrada:  "00191101000000482960000003339683000116742617"
    Saída:    "00190.00009 03339.683009 01167.426178 1 10100000048296"
    """

    if len(codigo_barras) != 44:
        raise ValueError("O código de barras deve ter exatamente 44 dígitos.")

    # Campos extraídos do código de barras
    campo1 = codigo_barras[0:4] + codigo_barras[19:24]  # Banco + Moeda + Primeira parte do campo livre
    campo2 = codigo_barras[24:34]  # Segunda parte do campo livre
    campo3 = codigo_barras[34:44]  # Terceira parte do campo livre
    campo4 = codigo_barras[4]  # DV geral do boleto
    campo5 = codigo_barras[5:19]  # Valor + Fator de vencimento

    # Gerar os dígitos verificadores de cada campo
    campo1 = campo1[:5] + "." + campo1[5:] + str(calcular_dv(campo1))
    campo2 = campo2[:5] + "." + campo2[5:] + str(calcular_dv(campo2))
    campo3 = campo3[:5] + "." + campo3[5:] + str(calcular_dv(campo3))

    # Montar a linha digitável final
    linha_digitavel = f"{campo1} {campo2} {campo3} {campo4} {campo5}"
    return linha_digitavel

def calcular_dv(campo):
    """
    Calcula o dígito verificador (DV) para um bloco da linha digitável usando o Módulo 10.
    """
    soma = 0
    peso = 2

    for digito in reversed(campo):
        multiplicacao = int(digito) * peso
        soma += sum(divmod(multiplicacao, 10))  # Soma os dígitos do resultado

        # Alterna peso entre 2 e 1
        peso = 1 if peso == 2 else 2

    dv = (10 - (soma % 10)) % 10  # Calcula o DV
    return dv

def barcode_reader(pdf_path):
    # Caminho correto da pasta bin do Poppler / caso nao tenha instalado
    poppler_path = r"C:\poppler-24.08.0\Library\bin"
    # Converter PDF em imagem
    pages = convert_from_path(pdf_path, poppler_path=poppler_path)
    img = pages[0]
    # Converter a imagem para escala de cinza (preto e branco)
    gray_img = img.convert("L")
    # Aumentar o contraste para destacar os códigos
    contrast = ImageEnhance.Contrast(gray_img)
    img_enhanced = contrast.enhance(2.0)  # Ajuste para testar

    # Decodificar novamente
    decoded_objects = decode(img_enhanced)

    for decod in decoded_objects:
        decod_data = decod[0]
        if decod_data != "" and type(decod_data) == "I25":
            decod_ = decod_data.decode('utf-8')
            return decod_
        
if __name__ == '__main__':
    # Caminho correto da pasta bin do Poppler
    poppler_path = r"C:\poppler-24.08.0\Library\bin"

    # Diretório onde estão os PDFs
    pdf_dir = r"C:\Users\douglas.lsilva\DESENVOLVIMENTO\AUTOMACAO EMAILS"

    # Listar todos os PDFs no diretório
    pdfs = [i for i in os.listdir(pdf_dir) if i.lower().endswith(".pdf")]

    # Verificar se encontrou arquivos PDF
    if not pdfs:
        print("Nenhum arquivo PDF encontrado na pasta!")
        exit()

    # Criar o caminho absoluto para o primeiro PDF da lista
    pdf_path = os.path.join(pdf_dir, pdfs[0])