##APP Joao

import tweepy
import requests


#Arquivos com senhas

import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


#Airtable keys

airtable_api = os.environ.get('AIRTABLE_KEY')
base_k = os.environ.get('BASE')


#MailGun keys

mailgun_acc = os.environ.get('MAILGUN_ACC')
mailgun_pass = os.environ.get('MAILGUN_KEY')


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
    hora_inicial = Time(3, 30, 0)
    hora_final = Time(7, 20, 0)

    if hora_inicial < hora_agora < hora_final:
        rodar_programa = True

    date_b = Date.today()
    date = str(date_b).replace("-", "/")
    dateWSJ = str(date_b).replace("-", "")
    #Lembrar de definir o que você quer? [0] para rodar e [1] para o dia do mês
    return rodar_programa, date, dateWSJ



#Pegando as informacoes


#Zero Hora

def get_zero_hora():
    from bs4 import BeautifulSoup as bs
    import requests

    zero_hora = requests.get("https://gauchazh.clicrbs.com.br")
    bsOb = bs(zero_hora.content, "html5lib")
    try:
        data = bsOb.find("div", {"class":"latest-edition is-out-pad"}).a.img.get("alt")
    except AttributeError:
        pass
    try:
        link = bsOb.find("div", {"class":"latest-edition is-out-pad"}).a.img.get("src").replace("//", "https://")
    except AttributeError:
        pass
    return f"{data} | {link}"


# Jornal do Comércio

def get_jornal_do_comercio(data):
    data = data.replace("/", ",")
    from bs4 import BeautifulSoup as bs
    import requests

    jc = requests.get(f"http://jconlineinteratividade.ne10.uol.com.br/capa-do-dia/{data},0,1,index.html")
    bsOb = bs(jc.content, "html5lib")
    try:
        if bsOb.find("div", {"class":"imagem bordaimg imagemcapa"}).h3.text.strip() == 'Capa não encontrada.':
            link = []
            return link
    except AttributeError:
        link = bsOb.find("div", {"class":"imagem bordaimg imagemcapa"}).a.img.get("src")
        return f'{data.replace(",", "/")} | {link}'


# A Tarde

def get_a_tarde():
    from bs4 import BeautifulSoup as bs
    import requests

    a_tarde = requests.get("http://edicaodigital.atarde.uol.com.br")
    bsOb = bs(a_tarde.content, "html5lib")
    Data = bsOb.find("section", {"class":"capa"}).find("img").get("alt")
    link = bsOb.find("section", {"class":"capa"}).find("img").get("src")
    return f"{Data} | {link}"



# Diário Catarinense

def get_DC():
    from bs4 import BeautifulSoup as bs
    import requests

    diario_catarinense = requests.get("http://dc.clicrbs.com.br/sc/")
    bsOb = bs(diario_catarinense.content, "lxml")

    try:
        link_capa = bsOb.find("div", {"class":"sc-htpNat Column FNnSZ"}).find('img').get('src')
    except AttributeError:
        pass
        link_capa = []
    return link_capa



#Twitter

def get_twitter(pagina):
    lista = []
    lista_final = []
    for status in tweepy.Cursor(api.user_timeline, screen_name = pagina).items(200):
        lista.append(f"{status._json['text']} | https://twitter.com/i/web/status/{status._json['id_str']}")
    compara = ["London", "UK"]

    for selecionado in lista:
        if "front page" in selecionado:
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
    bsOb = bs(ny_times.content, "lxml")

    try:
        manchete = bsOb.find("ol", {"class":"css-1i4ie59 ekkqrpp2"}).li.div.h2.text.strip()
    except:
        pass
        manchete = []
    try:
        desc = bsOb.find("ol", {"class":"css-1i4ie59 ekkqrpp2"}).li.div.p.text.strip()
    except:
        pass
        desc = []

    return manchete, desc


#WSJ

def pega_manchete_WSJ(dia_pegar):
    from bs4 import BeautifulSoup as bs
    import requests

    WSJ = requests.get(f"http://www.wsj.com/itp/{dia_pegar}/frontpage")
    bsOb = bs(WSJ.content, "lxml")
    try:
        manchete = bsOb.find("div", {"class":"headlineSummary topStory LS-imageFormat-D leadStory-itp"}).find('h1').text.strip()
    except:
        pass
        manchete = []
    try:
        desc = bsOb.find("div", {"class":"headlineSummary topStory LS-imageFormat-D leadStory-itp"}).find('p').text.strip()
    except:
        pass
        desc = []

    return manchete, desc


#Le Monde


def get_Lemonde(data):
    url = f"https://www.lemonde.fr/journalelectronique/donnees/libre/{data}/index.html"
    lemonde = requests.get(url)
    if lemonde.status_code == 404:
        return []
    elif lemonde.status_code == 200:
        return url, data


#Sueddeutsche

def get_Sueddeutsche(data):
    data = data.replace("/", "-")
    url = f"https://zeitung.sueddeutsche.de/szdigital/public/issues/list?from={data}&productId=sz&to={data}"
    Sueddeutsche = requests.get(url).json()
    if Sueddeutsche['issuesForProductsMap'] == {}:
        return []
    else:
        url = f'https://zeitung.sueddeutsche.de/szdigital/public/issue/previewimage?size=l&issueId={data}&targetVersion=6&productId=sz'
        return url, data


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



#Pegando a base do airtable

def base_airtable_import(base_k, table_n):
    from airtable import Airtable
    airtable = Airtable(base_k, table_n, api_key=airtable_api)
    records = airtable.get_all()
    table = []
    for v in records:
        try:
            table.append(v['fields']['Name'])
        except KeyError:
            pass
    return table



#adicionar linha ao Airtable

def base_airtable_inserir(base_k, table_n, novos_dados):
    from airtable import Airtable
    airtable = Airtable(base_k, table_n, api_key=airtable_api)
    data = {'Name': novos_dados}
    airtable.insert(data)



#comparar se é novo ou não e inserir na tabela

def manchetes_novas(base_airtable, lista_final, destino):
    novidade = []
    for item in lista_final:
        if item in base_airtable:
            pass
        else:
            novidade.append(item)
            base_airtable_inserir(base_k, destino, item)
            base_airtable = base_airtable_import(base_k, destino)
    return novidade




# PRECISO FAZER UMA FORMA DELE BUSCAR TUDO E DEPOIS MANDAR UM E-MAIL SÓ' atualizar o código

def enviar_email(mensagem_email, assunto):
    import pendulum
    data = pendulum.today()

    import smtplib

    pega_assunto = ""

    for jornal in range(len(assunto)):
        if jornal == 0:
            pega_assunto += assunto[jornal]
        elif 0 < jornal < len(assunto)-1:
            pega_assunto += f", {assunto[jornal]}"
        elif jornal == len(assunto)-1:
            pega_assunto += f" e {assunto[jornal]}"


    subject = f'Manchetes NewsPaper: {pega_assunto}'
    msg = 'Subject:{}\n\nSeguem manchetes:\n\n\n'.format(subject)

    msg+= f"{mensagem_email}\n\n\n\n\nProjeto João\nAgência Estado / O Estado de S.Paulo\n\n"

    mailgun_sender = 'noreply@cristianfavaro.com.br'

    server = smtplib.SMTP_SSL('smtp.mailgun.org', 465)
    server.login(mailgun_acc, mailgun_pass)

    para = os.environ.get('DESTINO_EMAIL')

    corpo = msg.encode('utf8')
    server.sendmail(mailgun_sender, para.split(","), corpo)

    server.quit()


def main():

	import ronda_concorentes

	ronda_concorentes.main()


    rodar_programa = iniciar_procura()[0]

    if rodar_programa == True:

        assunto = []
        Manchetes_email = ""

        #FT
        lista_final = get_twitter("FinancialTimes")
        base_twitter = base_airtable_import(base_k, "FT")
        novidade = manchetes_novas(base_twitter, lista_final, "FT")
        if novidade == []:
            pass
        else:
            Manchetes_email += f"-- Manchete do Financial Times:\n\n{novidade[0]}\n\n\n"
            assunto.append("Financial Times")

        #NYT
        manchete, desc = pega_manchete_ny(iniciar_procura()[1])
        base_ny = base_airtable_import(base_k, "NYT")
        manchete = arruma_manchete(manchete)
        novidade = manchetes_novas(base_ny, manchete, "NYT")
        if novidade == []:
            pass
        else:
            Manchetes_email += f"-- Manchete do NYT:\n\n{novidade[0]}\n\n{desc}\n\n\n"
            assunto.append("NYT")

        #WSJ
        manchete, desc = pega_manchete_WSJ(iniciar_procura()[2])
        base_WSJ = base_airtable_import(base_k, "WSJ")
        manchete = arruma_manchete(manchete)
        novidade = manchetes_novas(base_WSJ, manchete, "WSJ")
        if novidade == []:
            pass
        else:
            Manchetes_email += f"-- Manchete do WSJ:\n\n{novidade[0]}\n\n{desc}\n\n\n"
            assunto.append("WSJ")


        #ElPais
        arquivo_El = pega_manchete_ElPais(iniciar_procura()[1])
        base_ElPais = base_airtable_import(base_k, "ElPais")
        novidade = manchetes_novas(base_ElPais, arquivo_El, "ElPais")
        if novidade == []:
            pass
        else:
            Manchetes_email += f"-- Manchete do El Pais:\n\n{novidade[0]}\n\n\n"
            assunto.append("El Pais")

        # Jornal do Comércio
        manchete = get_jornal_do_comercio(iniciar_procura()[1])
        base_JC = base_airtable_import(base_k, "JC")
        manchete = arruma_manchete(manchete)
        novidade = manchetes_novas(base_JC, manchete, "JC")
        if novidade == []:
            pass
        else:
            Manchetes_email += f"-- Manchete do JC:\n\n{novidade[0]}\n\n\n"
            assunto.append("JC")


        # A Tarde
        manchete = get_a_tarde()
        base_ATarde = base_airtable_import(base_k, "ATarde")
        manchete = arruma_manchete(manchete)
        novidade = manchetes_novas(base_ATarde, manchete, "ATarde")
        if novidade == []:
            pass
        else:
            Manchetes_email += f"-- Manchete do A Tarde:\n\n{novidade[0]}\n\n\n"
            assunto.append("A Tarde")

        # Diário Catarinense
        manchete = get_DC()
        base_DC = base_airtable_import(base_k, "DC")
        manchete = arruma_manchete(manchete)
        novidade = manchetes_novas(base_DC, manchete, "DC")
        if novidade == []:
            pass
        else:
            Manchetes_email += f"-- Manchete do DC:\n\n{novidade[0]}\n\n\n"
            assunto.append("DC")


        #Le Monde
        manchete = get_Lemonde(iniciar_procura()[2])
        base_Lemonde = base_airtable_import(base_k, "Lemonde")
        mancheteLink = arruma_manchete(manchete[0])
        mancheteData = arruma_manchete(manchete[1])
        novidade = manchetes_novas(base_Lemonde, mancheteData, "Lemonde")

        if novidade == []:
            pass
        else:
            Manchetes_email += f"-- Manchete do Le Monde:\n\n{mancheteLink[0]}\n\n\n"
            assunto.append("Le Monde")

        #Sueddeutsche
        manchete = get_Sueddeutsche(iniciar_procura()[1])
        base_Sueddeutsche = base_airtable_import(base_k, "Sueddeutsche")
        try:
            mancheteLink = arruma_manchete(manchete[0])

            mancheteData = arruma_manchete(manchete[1])
            novidade = manchetes_novas(base_Sueddeutsche, mancheteData, "Sueddeutsche")
            if novidade == []:
                pass
            else:
                pagina_site = f"https://zeitung.sueddeutsche.de/webapp/access/sz/{mancheteData[0]}"
                Manchetes_email += f"-- Manchete do Sueddeutsche:\n\n{pagina_site}\n\n\n"
                assunto.append("Sueddeutsche")


        except IndexError:
            pass

        if Manchetes_email != [] and assunto != []:
            enviar_email(Manchetes_email, assunto)
        else:
            pass



if __name__ == '__main__':
    main()
