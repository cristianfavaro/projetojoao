#Projeto Inter
#Projeto Inter

import io
import requests
from bs4 import BeautifulSoup as bs


import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

airtable_api = os.environ.get('AIRTABLE_KEY')
destino2 = os.environ.get('DESTINO_EMAIL2')
base_k2 = os.environ.get('BASE2')
mailgun_acc = os.environ.get('MAILGUN_ACC')
mailgun_pass = os.environ.get('MAILGUN_KEY')


def get_id():
    
    url = 'https://factba.se/topic/latest/email'

    data = requests.get(url)
    bsOb = bs(data.content, "lxml")

    base_info = bsOb.find("div", {"id":"topicblock"})


    tabela_selecao = base_info.findAll("div", {"class":"media topic-media-row mediahover"})

    lista_id = []
    for item in tabela_selecao:
        lista_id.append(item.find("div", {'class':'media-floater'}).a.get('id'))

    return lista_id


def base_airtable_import(base_k2, table_n='WH'):
    from airtable import Airtable
    airtable = Airtable(base_k2, table_n, api_key=airtable_api)
    records = airtable.get_all()
    table_id = []
    for v in records:
        try:
            table_id.append(v['fields']['Id'])
        except KeyError:
            pass

    return table_id


#Compara se tem novidade


def compara(table_id, lista_id):
    #aqui no compara ele, mas não vai inserir
    novidade = []
    for item in lista_id:
        if item in table_id:
            pass
        else:
            novidade.append(item)
    return novidade


#pega o texto final

def get_html_text(id):

    html = requests.get(f"https://factba.se/json/latest-helper-json.php?platform=email&id={id}")

    BsObj = bs(html.text, "lxml")

    Texto = str(BsObj.find('center')).split('###')[0]
    Texto2 = BsObj.find('center')

    return Texto, Texto2


#inserir informacoes no airtable
def base_airtable_insert(base_k2, novos_dados, table_n='WH'):
    import pendulum
    from airtable import Airtable
    airtable = Airtable(base_k2, table_n, api_key=airtable_api)
    for item in novos_dados:
        data = {'Id': item, 'Texto': get_html_text(item)[1].text.split("###")[0], 'Data': str(pendulum.today())}
        airtable.insert(data)


#envia e-mail

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
            data = get_html_text(item)[0]


            me = "noreply@cristianfavaro.com.br"
            you = destino2

            # Create message container - the correct MIME type is multipart/alternative.
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Release - White House"
            msg['From'] = me
            msg['To'] = you

            # Create the body of the message (a plain-text and an HTML version).
            text = "Segue release publicado pelo Factbase.se:\n\nProjeto Inter\nAE / O Estado de S.Paulo\n\n==="
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
    

def run_projeto_inter():

    lista_id = get_id()
    table_id = base_airtable_import(base_k2)
    novidade = compara(table_id, lista_id)
    base_airtable_insert(base_k2, novidade)
    send_email(novidade)
    
    
def main():
    run_projeto_inter()




if __name__ == '__main__':
    main()