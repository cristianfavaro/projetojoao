import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

airtable_api = os.environ.get('AIRTABLE_KEY')
gmail_acc = os.environ.get('G-MAIL_ACC')
gmail_pass = os.environ.get('G-MAIL_KEY')

airtable_fonte_api_url = os.environ.get('AIR_FONTE_URL')
base_k = os.environ.get('BASE')
table_n = "Table 1"


def iniciar_procura():
    from pendulum import Time
    from pendulum import Date

    rodar_programa = False
    hora_agora = Time.now(False)
    hora_inicial = Time(0, 5, 0)
    hora_final = Time(6, 20, 0)

    if hora_inicial < hora_agora < hora_final:
        rodar_programa = True
    
    date_b = Date.today()
    date = str(date_b).replace("-", "/")
    dateWSJ = str(date_b).replace("-", "")
    #Lembrar de definir o que você quer? [0] para rodar e [1] para o dia do mês
    return rodar_programa, date, dateWSJ, hora_agora


def enviar_email(hora_agora):
    import smtplib
    subject = f'Manchete disponivel para o NewsPaper'
    msg = 'Subject:{}\n\nSegue manchete:\n\n\n'.format(subject)
    
    msg+= f"{hora_agora}\n\n"

    gmail_sender = 'cfc.jornalista@gmail.com'

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(gmail_acc, gmail_pass)

    para = os.environ.get('DESTINO_EMAIL')

    corpo = msg.encode('utf8')
    server.sendmail(gmail_sender, para.split(","), corpo)

    server.quit()

def main():
    hora_agora = iniciar_procura()[3]
    enviar_email(hora_agora)


if __name__ == '__main__':
    main()