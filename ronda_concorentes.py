import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import ast
import json
import tweepy

#Arquivos com senhas

import os

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())



def Twitter_TT(id_tt):
    consumer_key = os.environ.get('CONSUMER_KEY2')
    consumer_secret = os.environ.get('CONSUMER_SECRET2')
    acces_token = os.environ.get('ACCES_TOKEN2')
    acces_token_secret = os.environ.get('ACCES_TOKEN_SECRET2')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(acces_token, acces_token_secret)
    api = tweepy.API(auth)

    trends = api.trends_place(id_tt)

    params = {
        'data': json.dumps(trends),
        'location': int(trends[0]['locations'][0]['woeid']),
    }

    r = requests.post('https://broadsearch.cristianfavaro.com.br/twitter/', params)
    return r



def OGlobo():
    url = "https://oglobo.globo.com/api/v1/ultimas-noticias/ece_frontpage/conteudo.json"
    url_requ = requests.get(url).json()
    data = url_requ[0]['conteudos']

    base = pd.DataFrame(data)[['titulo', 'subTitulo', 'id', 'secao', 'publicadoEm', 'url']]

    for i in range(len(base)):

        editoria = base.iloc[i]['secao']['nome']
        if editoria == 'Brasil':
            codigo = 2
        elif editoria == 'Economia':
            codigo = 1
        elif editoria == 'Esportes':
            pass
        elif editoria == 'Rio Show':
            pass
        elif editoria == 'Cultura':
            pass
        elif editoria == 'Lauro Jardim':
            codigo = 4
        else:
            codigo = 3
        try:
            payload = {
                'token': 'hduiashdiuncaiouudsahfoisdiafmsch@@@@@',
                'titulo': base.iloc[i]['titulo'],
                'editoria': codigo,
                'portal': 3,
                'texto_completo': base.iloc[i]['subTitulo'],
                'link': base.iloc[i]['url'],
                'manchete': False,
            }

            r = requests.get('https://cristianfavaro.com.br/broadsearch/post-area', params=payload)
            print(r)

        except NameError:
            pass
    return base



def posta(titulo, codigo, linha_fina, link, portal, manchete=False):
    import requests

    payload = {
        'token': 'hduiashdiuncaiouudsahfoisdiafmsch@@@@@',
        'titulo': titulo,
        'editoria': codigo,
        'portal': portal,
        'texto_completo': linha_fina,
        'link': link,
        'manchete': manchete,
    }

    r = requests.get('https://cristianfavaro.com.br/broadsearch/post-area', params=payload)

def pega_site_folha():

    import requests
    from bs4 import BeautifulSoup as bs

    url = "https://www1.folha.uol.com.br/ultimas-noticias/"
    url_requ = requests.get(url)
    bsObj = bs(url_requ.text, "html5lib")
    data = bsObj.find("main", {'id':'conteudo'})
    reportagensBrutas = data.findAll('li', {'class':['c-headline c-headline--newslist', 'c-main-headline c-main-headline--horizontal']})

    for item in reportagensBrutas:
        titulo = item.find('h2', {'class':['c-main-headline__title', 'c-headline__title']}).text
        try:
            editoria = item.find('h3', {'class':'c-headline__kicker c-kicker'}).text.strip()
        except AttributeError:
            editoria = 'Mercado'
        try:
            linha_fina = item.find('p', {'class':['c-main-headline__standfirst', 'c-headline__standfirst']}).text.strip()
        except AttributeError:
            linha_fina = ''

        link = item.find('div', {'class':['c-main-headline__content', 'c-headline__content', 'c-main-headline__wrapper']}).a['href']

        if editoria == 'Mercado':
            codigo = 1
            posta(titulo, codigo, linha_fina, link, portal=2)

        elif any(editoria in s for s in ['Lava Jato', 'Governo Bolsonaro', 'Poder']):
            codigo = 2
            posta(titulo, codigo, linha_fina, link, portal=2)

        elif editoria == 'Mundo':
            codigo = 5
            posta(titulo, codigo, linha_fina, link, portal=2)

        elif any(editoria in s for s in ['Copa América', 'Celebridades', 'Educação', 'Esporte', 'Música']):
            codigo = 'a'
            pass
            print('ignorado ' + editoria)

    return reportagensBrutas


def pega_site_Valor():

    import requests
    from bs4 import BeautifulSoup as bs

    url = 'https://www.valor.com.br'
    url_dados = requests.get(url)

    bsobj = bs(url_dados.text, 'html5lib')
    templates = bsobj.findAll('div', {'class':'template'})
    grids = bsobj.findAll('div', {'class':['grid', 'grid2 right']})

    for i, item in enumerate(grids):
        if i == 0:
            titulo = item.find('div', {'class':'teaser-title'}).a.text.strip()
            link = item.find('div', {'class':'teaser-title'}).a.get('href')
            try:
                editoria = item.find('div', {'class':'teaser-date'}).a.text.strip()
            except AttributeError:
                editoria = "Empresas"
            try:
                linha_fina = item.find('div', {'class':'teaser'}).text.strip()
            except AttributeError:
                linha_fina = ''

            if editoria == "Empresas":
                codigo = 1

            elif any(editoria in s for s in ['Brasil', 'Política']):
                codigo = 2

            else:
                codigo = 1

            posta(titulo, codigo, linha_fina, link, 4, manchete=True)


        else:
            titulo = item.find('div', {'class':'teaser-title'}).a.text.strip()
            link = item.find('div', {'class':'teaser-title'}).a.get('href')
            try:
                editoria = item.find('div', {'class':'teaser-date'}).a.text.strip()
            except AttributeError:
                editoria = "Empresas"

            try:
                linha_fina = item.find('div', {'class':'teaser'}).text.strip()
            except AttributeError:
                linha_fina = ''

            if editoria == "Empresas":
                codigo = 1

            elif any(editoria in s for s in ['Brasil', 'Política']):
                codigo = 2

            else:
                codigo = 1

            posta(titulo, codigo, linha_fina, link, 4)
            print(codigo, editoria)
    return grids



def pega_site_g1():
    import requests
    from bs4 import BeautifulSoup as bs

    url = 'https://g1.globo.com'
    url_dados = requests.get(url)
    bsobj = bs(url_dados.text, 'html5lib')

    reportagens = bsobj.findAll('div', {'class':'feed-post-body'})

    for i, item in enumerate(reportagens):
        if i == 0:

            titulo = item.find('div', {'class':'feed-post-body-title'}).text.strip()

            try:
                linha_fina = item.find('div', {'class':'feed-post-body-resumo'}).text.strip()
            except AttributeError:
                linha_fina = ''

            try:
                editoria = item.find('span', {'class':'feed-post-metadata-section'}).text.strip()
            except AttributeError:
                editoria = 'Economia'

            link = item.find('div', {'class':'feed-post-body-title'}).a.get('href')

            if any(editoria in s for s in ['Política', 'São Paulo', 'Rio de Janeiro']):
                codigo = 2
                posta(titulo, codigo, linha_fina, link, portal=5, manchete=True)

                print(codigo, editoria, titulo)

            elif editoria == 'Economia':
                codigo = 1
                posta(titulo, codigo, linha_fina, link, portal=5, manchete=True)
                print(codigo, editoria, titulo)

            elif any(editoria in s for s in ['Mundo', 'Internacional']):
                codigo = 5
                posta(titulo, codigo, linha_fina, link, portal=5, manchete=True)
                print(codigo, editoria, titulo)

        else:

            titulo = item.find('div', {'class':'feed-post-body-title'}).text.strip()

            try:
                linha_fina = item.find('div', {'class':'feed-post-body-resumo'}).text.strip()
            except AttributeError:
                linha_fina = ''

            try:
                editoria = item.find('span', {'class':'feed-post-metadata-section'}).text.strip()
            except AttributeError:
                editoria = 'Economia'

            link = item.find('div', {'class':'feed-post-body-title'}).a.get('href')

            if any(editoria in s for s in ['Política', 'São Paulo', 'Rio de Janeiro']):
                codigo = 2
                posta(titulo, codigo, linha_fina, link, portal=5)

                print(codigo, editoria, titulo)

            elif editoria == 'Economia':
                codigo = 1
                posta(titulo, codigo, linha_fina, link, portal=5)
                print(codigo, editoria, titulo)

            elif any(editoria in s for s in ['Mundo', 'Internacional']):
                codigo = 5
                posta(titulo, codigo, linha_fina, link, portal=5)
                print(codigo, editoria, titulo)

def main():
    Twitter_TT(1)
    Twitter_TT(23424768)

if __name__ == '__main__':
    main()
