#Projeto - Banco Central


import requests
from bs4 import BeautifulSoup as bs


import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


airtable_api = os.environ.get('AIRTABLE_KEY')
base_k3 = os.environ.get('BASE3')


#MailGun keys

mailgun_acc = os.environ.get('MAILGUN_ACC')
mailgun_pass = os.environ.get('MAILGUN_KEY')
destino3 = os.environ.get('DESTINO_EMAIL3')



def get_bc_swaps():
    url = 'http://www.bcb.gov.br/pre/normativos/busca/buscaSharePoint.asp?conteudo=swap&startRow=0'

    data_base = requests.get(url).json()

    look = data_base['d']['query']['PrimaryQueryResult']['RelevantResults']['Table']['Rows']['results']

    #funçoes para arrumar o texto
    def get_data(item):
        return item['Cells']['results'][3]['Value']

    def get_id(item):
        """função para pegar o id dos contratos de swap"""
        return item['Cells']['results'][2]['Value']

    def get_title(item):
        """fiz para usar futuramente. Ele pega a data do rolamento dos contratos"""
        import re
        b = item['Cells']['results'][4]['Value']
        return re.findall(r'\d\d\/\d\d/\d\d\d\d', b)

    #criando a lista
    list_bc = []
    for item in look:
        case = {'Id': get_id(item).split(' N° ')[1], 'Data': get_data(item).split('#')[1]}
        list_bc.append(case)

    return list_bc



def get_bc_base(base_k3=base_k3, table_n='Swap'):
    from airtable import Airtable
    airtable = Airtable(base_k3, table_n, api_key=airtable_api)
    records = airtable.get_all()
    table_id = []
    for v in records:
        try:
            table_id.append(v['fields']['Id'])
        except KeyError:
            pass

    return table_id


def compara(table_id, lista_id):
    #aqui no compara ele, mas não vai inserir
    novidade_full = []
    novidade = []
    for item in lista_id:
        if item['Id'] in table_id:
            pass
        else:
            novidade.append(item['Id'])
            novidade_full.append(item)
    return novidade, novidade_full



def get_bc_text(report_id):
    """Recebe o id do relatório e retorna o texto dele e a data e hora de publicação"""
    report_id = report_id.replace('.', '')
    url2 = f'http://www.bcb.gov.br/pre/normativos/busca/sharepointproxyDetalharNormativo.asp?metodo=Demais%20Normativos&numero={report_id}&tipo=Comunicado'
    resposta = requests.get(url2).json()
    text_bc = resposta['d']['results'][0]['Texto']
    hora_report = resposta['d']['results'][0]['DataTexto']

    return text_bc, hora_report



def insert_bc_airtable(novos_dados, table_n='Swap', base_k3=base_k3):
    import pendulum
    from airtable import Airtable
    airtable = Airtable(base_k3, table_n, api_key=airtable_api)
    for item in novos_dados:
        data = {'Id': item['Id'], 'Data': item['Data']}
        airtable.insert(data)


def send_email(novidade):
    import smtplib

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    mail = smtplib.SMTP_SSL('smtp.mailgun.org', 465)

    mail.login(mailgun_acc, mailgun_pass)

    for item in novidade:
        if novidade == []:
            pass
        else:

            #montando o e-mail
            data, hora = get_bc_text(item)
            me = "noreply@cristianfavaro.com.br"
            you = destino3

            # Create message container - the correct MIME type is multipart/alternative.
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Swap Cambial - BC ({hora}) / Release AE"
            msg['From'] = me
            msg['To'] = you


            # Create the body of the message (a plain-text and an HTML version).
            text = "Segue Comunicado de Swap Cambial do BC:\n\nProjeto João\nAE / O Estado de S.Paulo\n\n==="
            html = data

            # Record the MIME types of both parts - text/plain and text/html.
            part1 = MIMEText(text, 'plain', None)
            part2 = MIMEText(html, 'html', None)


            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(part1)
            msg.attach(part2)

            # Send the message via local SMTP server.

            mail.sendmail(me, you.split(","), msg.as_string())


    mail.quit()


def main():
    list_bc = get_bc_swaps()
    table_bc = get_bc_base()
    novidade, novidade_full = compara(table_bc, list_bc)
    send_email(novidade)
    insert_bc_airtable(novidade_full)

    

if __name__ == '__main__':
    main()
    
