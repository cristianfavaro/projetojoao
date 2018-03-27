##APP Joao


import tweepy
import requests


#Arquivos com senhas 

import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

airtable_api = os.environ.get('AIRTABLE_KEY')
gmail_acc = os.environ.get('G-MAIL_ACC')
gmail_pass = os.environ.get('G-MAIL_KEY')

airtable_fonte_api_url = os.environ.get('AIR_FONTE_URL')
base_k = os.environ.get('BASE')
table_n = "Table 1"

#Twitter

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
acces_token = os.environ.get('ACCES_TOKEN')
acces_token_secret = os.environ.get('ACCES_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(acces_token, acces_token_secret)
api = tweepy.API(auth)


#Definindo funcoes


#definir o relogio

def iniciar_procura():
    from pendulum import Time
    from pendulum import Date

    rodar_programa = False
    hora_agora = Time.now(False)
    hora_inicial = Time(0, 30, 0)
    hora_final = Time(6, 20, 0)

    if hora_inicial < hora_agora < hora_final:
        rodar_programa = True
    
    date_b = Date.today()
    date = str(date_b).replace("-", "/")
    dateWSJ = str(date_b).replace("-", "")
    #Lembrar de definir o que você quer? [0] para rodar e [1] para o dia do mês
    return rodar_programa, date, dateWSJ




#Pegando as informacoes 

#Twitter

def get_twitter(pagina):
    lista = []
    lista_final = []
    for status in tweepy.Cursor(api.user_timeline, screen_name = pagina).items(200):
        lista.append(f"{status._json['text']} | https://twitter.com/i/web/status/{status._json['id_str']}")
    compara = ["London", "UK"]
    
    for selecionado in lista:
        if "front page" in selecionado:
            if "Just published"in selecionado:
                for bb in compara:
                    if bb in selecionado:
                        lista_final.append(selecionado)
    return lista_final


#NYT

def pega_manchete_ny(dia_pegar):
    #puxar da funcao do tempo
    from bs4 import BeautifulSoup as bs
    import requests

    ny_times = requests.get(f"https://www.nytimes.com/issue/todayspaper/{dia_pegar}/todays-new-york-times")
    bsOb = bs(ny_times.content, "html5lib")

    try:
        manchete = bsOb.find("ol", {"class":"story-menu"}).li.article.div.h2.text.strip()
    except AttributeError:
        pass
        manchete = []
    try: 
        desc = bsOb.find("ol", {"class":"story-menu"}).li.article.div.p.text.strip()
    except AttributeError:
        pass
        desc = []
        
    return manchete, desc


#WSJ

def pega_manchete_WSJ(dia_pegar):
    from bs4 import BeautifulSoup as bs
    import requests

    WSJ = requests.get(f"http://www.wsj.com/itp/{dia_pegar}/us")
    bsOb = bs(WSJ.content, "html5lib")
    try:
        manchete = bsOb.find("div", {"class":"contentwide nonSub"}).div.find("div", {"class":"newsContainer"}).h1.text.strip()
    except AttributeError:
        pass
        manchete = []
    try:    
        desc = bsOb.find("div", {"class":"contentwide nonSub"}).div.find("div", {"class":"newsContainer"}).p.text.strip()
    except AttributeError:
        pass
        desc = []

    return manchete, desc

#ElPais

def pega_manchete_ElPais(dia_pegar):
    from bs4 import BeautifulSoup as bs
    import requests
    link_elpais = f"https://elpais.com/hemeroteca/elpais/portadas/{dia_pegar}/"
    elpais = requests.get(link_elpais)
    bsOb = bs(elpais.content, "html5lib")
    Data = bsOb.find("div", {"class":"archivo_portadas"}).findAll("div")[1].p.text
    arquivo_El = []

    if Data == 'No hay portadas de EL PAÍS para esa fecha':
        arquivo_El = []
    else: 
        arquivo_El.append(f"Jornal do dia {dia_pegar} liberado | https://elpais.com/hemeroteca/elpais/portadas/{dia_pegar}")
    return arquivo_El



#Transformando o que retorna do WSJ e NY de string para lista. Assim consigo jogar para o Airtable

def arruma_manchete(manchete):
    manchete_list = manchete
    if isinstance(manchete, str):
        manchete_list = [manchete]
    return manchete_list



#importar a base com os links 

def csv_import(base_k, table_n):
    from airtable import Airtable
    base_key = base_k
    table_name = table_n
    airtable = Airtable(base_key, table_name, api_key=airtable_api)
    records = airtable.get_all()
    base_twitter = []
    base_ny = []
    base_WSJ = []
    base_ElPais = []
    for v in records:
        try:
            base_twitter.append(v['fields']['publicacao'])
        except KeyError:
            pass
        try:
            base_ny.append(v['fields']['NY'])
        except KeyError:
            pass
        try:
            base_WSJ.append(v['fields']['WSJ'])
        except KeyError:
            pass
        try:
            base_ElPais.append(v['fields']['ElPais'])
        except KeyError:
            pass
    #lembrar de jogar o resultado da fun em duas var. (base_twitter, base_ny = )

    return base_twitter, base_ny, base_WSJ, base_ElPais


#adicionar linha ao Airtable - Terei de ter um para a publicacao e um para NY

def adicionar_linha_twitter(novos_dados):
    airtable_destino_api_url = airtable_fonte_api_url
    headers = {"Authorization": f'Bearer {airtable_api}'}
    new_content = {"fields": {"publicacao": novos_dados}}
    s = requests.post(airtable_destino_api_url, json=new_content, headers=headers)

def adicionar_linha_NY(novos_dados):
    airtable_destino_api_url = airtable_fonte_api_url
    headers = {"Authorization": f'Bearer {airtable_api}'}
    new_content = {"fields": {"NY": novos_dados}}
    s = requests.post(airtable_destino_api_url, json=new_content, headers=headers)

def adicionar_linha_WSJ(novos_dados):
    airtable_destino_api_url = airtable_fonte_api_url
    headers = {"Authorization": f'Bearer {airtable_api}'}
    new_content = {"fields": {"WSJ": novos_dados}}
    s = requests.post(airtable_destino_api_url, json=new_content, headers=headers)

def adicionar_linha_ElPais(novos_dados):
    airtable_destino_api_url = airtable_fonte_api_url
    headers = {"Authorization": f'Bearer {airtable_api}'}
    new_content = {"fields": {"ElPais": novos_dados}}
    s = requests.post(airtable_destino_api_url, json=new_content, headers=headers)


#comparar se é novo ou não

def manchetes_novas(base_airtable, lista_final, destino):
    #Lembrando que a lista_compara agora é lista_final e a base_relatorio agora é base ny ou twitter
    novidade = []
    for item in lista_final:
        if item in base_airtable:
            pass
        else:
            novidade.append(item)
            if destino == "WSJ":
                adicionar_linha_WSJ(item)
            if destino == "NY":
                adicionar_linha_NY(item)
            if destino == "twitter":
                adicionar_linha_twitter(item)
            if destino == "ElPais":
                adicionar_linha_ElPais(item)
            base_airtable = csv_import(base_k, table_n)[0]
                
    return novidade




# PRECISO FAZER UMA FORMA DELE BUSCAR TUDO E DEPOIS MANDAR UM E-MAIL SÓ' atualizar o código

def enviar_email(novidade, jornal, desc = ""):
    import smtplib
    if novidade == []:
        pass
    else:
        subject = f'Manchete do {jornal} disponivel para o NewsPaper'
        msg = 'Subject:{}\n\nSegue manchete:\n\n\n'.format(subject)
        
        msg+= f"{novidade}\n\n{desc}\n\n"

        gmail_sender = 'cfc.jornalista@gmail.com'

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_acc, gmail_pass)

        para = os.environ.get('DESTINO_EMAIL')

        corpo = msg.encode('utf8')
        server.sendmail(gmail_sender, para.split(","), corpo)

        server.quit()



def main():
    rodar_programa = iniciar_procura()[0]
    if rodar_programa == True:
        
        #FT
        lista_final = get_twitter("FinancialTimes")
        base_twitter = csv_import(base_k, table_n)[0]
        novidade = manchetes_novas(base_twitter, lista_final, "twitter")
        enviar_email(novidade, "Financial Times")
        
        #NYT
        
        manchete, desc = pega_manchete_ny(iniciar_procura()[1])
        base_ny = csv_import(base_k, table_n)[1]
        manchete = arruma_manchete(manchete)
        novidade = manchetes_novas(base_ny, manchete, "NY")
        enviar_email(novidade, "NYT", desc)
        
        #WSJ
        
        manchete, desc = pega_manchete_WSJ(iniciar_procura()[2])
        base_WSJ = csv_import(base_k, table_n)[2]
        manchete = arruma_manchete(manchete)
        novidade = manchetes_novas(base_WSJ, manchete, "WSJ")
        enviar_email(novidade, "WSJ", desc)
        
        #ElPais
        arquivo_El = pega_manchete_ElPais(iniciar_procura()[1])
        base_ElPais = csv_import(base_k, table_n)[3]
        novidade = manchetes_novas(base_ElPais, arquivo_El, "ElPais")
        enviar_email(novidade, "El Pais")

if __name__ == '__main__':
    main()
