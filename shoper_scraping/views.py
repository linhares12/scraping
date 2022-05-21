from django.shortcuts import render, HttpResponse
from datetime import datetime
import requests, json

# Create your views here.

def index(request):
    return HttpResponse("teste")

def atualiza_precos(request):
    """
    Consulta os preços e atualiza no banco de dados
    """
    # Definição de base das urls
    global scheme, host
    scheme = 'https'
    host = 'shopper.com.br'

    # Usuário e senha para autenticação
    email = 'breno.pinheiro@ymail.com'
    senha = 'teste123'

    # requisições para consulta de produtos
    s = requests.Session()
    csrf_token = get_csrf_token(s)
    autentica(email, senha, csrf_token, s)
    user_token = get_user_token(s)

    departamento = get_departamento('Alimentos', user_token, s)
    subdepartamentos = get_subdepartamentos_from_departamento(departamento['id'], user_token, s)    # recebe também os produtos de cada departamento

    for subdepartamento in subdepartamentos:
        print(subdepartamento['name'])
    
    
def get_csrf_token(session):
    """
    Obtém o CSRFToken para autenticação
    """
    url = f'{scheme}://{host}/shpprtkn'
    req = session.get(url)
    return req.cookies['csrftoken']

def autentica(email, senha, csrf_token, session):
    """
    Realiza a autenticação no site
    """
    url = f'{scheme}://{host}/login'

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrf_token,
        'Referer': f'{scheme}://landing.{host}/',
    }

    cookies = {
        "csrftoken": csrf_token,
    }

    data = {
        'email': email,
        'senha': senha,
    }

    return session.post(url, headers=headers, data=data, cookies=cookies)

def get_user_token(session):
    url = f'{scheme}://{host}/shop/is-client/?deviceUUID=66d3d4b7-6ae4-46b5-b498-75868413a151'
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }
    req = session.get(url, headers=headers)
    return json.loads(req.text)['userToken']

def get_departamento(nome, user_token, session):
    host_api = f'siteapi.{host}'
    url = f'{scheme}://siteapi.{host}/catalog/departments'

    headers = {
        'Authorization': f'Bearer {user_token}',
    }

    req = session.get(url, headers=headers)
    departamentos = json.loads(req.text)['departments']

    for departamento in departamentos:
        if departamento['name'] == nome:
            return departamento

    return ''

def get_subdepartamentos_from_departamento(departamento_id, user_token, session):
    all = 9999
    url = f'{scheme}://siteapi.{host}/catalog/departments/{departamento_id}?size={all}'
    headers = {
    'Authorization': f'Bearer {user_token}',
    }
    req = session.get(url, headers=headers)
    return json.loads(req.text)['subdepartments']
