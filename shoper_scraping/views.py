from django.shortcuts import render, HttpResponse, redirect
from django.http import FileResponse
from django.utils.timezone import get_current_timezone
from django.utils import timezone
from shoper_scraping.models import *
from unidecode import unidecode
from datetime import datetime
import pandas as pd
import requests, json, csv

def index(request):
    return render(request, 'index.html')

### Exportação do Banco de Dados
def assortment(request):
    produtos = Produto.objects.all()
    name = []
    sku = []
    department = []
    category = []
    url = []
    image = []
    price_to = []
    discount = []
    available = []
    stock_qty = []
    store = []
    created_at = []
    hour = []

    for produto in produtos:
        print(produto.name)
        oferta = Oferta.objects.filter(produto=produto, loja__ehPrincipal=True)

        url_string = 'https://programada.shopper.com.br/shop-cn/' + produto.url
        available_string = 'S'
        if produto.stock_qty <= 0:
            available_string = 'N'
        name.append(produto.name)
        sku.append(produto.sku)
        department.append(produto.subdepartamento.departamento.name)
        category.append(produto.subdepartamento.name)
        url.append(url_string)
        image.append(produto.image)
        price_to.append(oferta[0].price)
        discount.append(oferta[0].savingPercentage)
        available.append(available_string)
        stock_qty.append(produto.stock_qty)
        store.append(oferta[0].loja.name)
        created_at.append(oferta[0].data_captura.date().strftime('%Y-%m-%d'))
        hour.append(oferta[0].data_captura.time().strftime('%H:%M:%S'))
        
    data = {
        'name': name,             # Nome do produto
        'sku': sku,               # Código interno do produto
        'department': department, # Departamento
        'category': category,     # Categoria
        'url': url,               # URL do produto
        'image': image,           # Imagem do produto
        'price_to': price_to,     # Preço por
        'discount': discount,     # Desconto do produto
        'available': available,   # S = Produto disponível e N = Produto indisponível
        'stock_qty': stock_qty,   # Qtde de estoque do produto
        'store': store,           # Loja principal
        'created_at': created_at, # Data da captura
        'hour': hour              # Hora da captura
    }
    df = pd.DataFrame(data)
    df.to_csv('assortment.csv', sep=';', float_format='%.2f', encoding='iso-8859-1', index=False)
    
    response = FileResponse(open('assortment.csv', 'rb'))
    return response

def seller(request):
    produtos = Produto.objects.all()
    name = []
    sku = []
    department = []
    category = []
    seller_store = []
    seller_player = []
    price_store = []
    price_player = []
    discount_store = []
    available = []
    stock_qty = []
    url = []
    image = []
    created_at = []
    hour = []

    for produto in produtos:
        ofertas = Oferta.objects.filter(produto=produto)
        oferta_principal = ofertas.filter(loja__ehPrincipal=True)[0]
        for oferta in ofertas:
            if oferta == oferta_principal:
                continue
            print(f'{oferta.loja.name} - {produto.name}: {oferta.price}')
            url_string = 'https://programada.shopper.com.br/shop-cn/' + produto.url
            available_string = 'S'
            if produto.stock_qty <= 0:
                available_string = 'N'
            name.append(produto.name)
            sku.append(produto.sku)
            department.append(produto.subdepartamento.departamento.name)
            category.append(produto.subdepartamento.name)
            seller_store.append(oferta_principal.loja.name)
            seller_player.append(oferta.loja.name)
            price_store.append(oferta_principal.price)
            price_player.append(oferta.price)
            discount_store.append(oferta_principal.savingPercentage)
            available.append(available_string)
            stock_qty.append(produto.stock_qty)
            url.append(url_string)
            image.append(produto.image)
            created_at.append(oferta.data_captura.date().strftime('%Y-%m-%d'))
            hour.append(oferta.data_captura.time().strftime('%H:%M:%S'))

    data = {
        'name': name,                       # Nome do produto
        'sku': sku,                         # Código interno do produto
        'department': department,           # Departamento
        'category': category,               # Categoria
        'seller_store': seller_store,       # Loja Principal
        'seller_player': seller_player,     # Vendedor
        'price_store': price_store,         # Preço da Loja principal
        'price_player': price_player,       # Preço do vendedor
        'discount_store': discount_store,   # Desconto do produto
        'available': available,             # S = Produto Disponível e N = Produto Indisponível
        'stock_qty': stock_qty,             # Qtde de Estoque do produto
        'url': url,                         # URL do produto
        'image': image,                     # Imagem do produto
        'created_at': created_at,           # Data da captura
        'hour': hour                        # Hora da captura
    }
    df = pd.DataFrame(data)
    df.to_csv('seller.csv', sep=';', float_format='%.2f', encoding='iso-8859-1', index=False)
    
    response = FileResponse(open('seller.csv', 'rb'))
    return response

### Importação ao Banco de Dados
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
    print('Obtendo chaves necessárias para autenticação')
    csrf_token = get_csrf_token(s)
    autentica(email, senha, csrf_token, s)
    user_token = get_user_token(s)

    departamento = get_departamento('Alimentos', user_token, s)
    try:
        subdepartamentos = get_subdepartamentos_from_departamento(departamento['id'], user_token, s)    # recebe também os produtos de cada subdepartamento
    except TypeError:
        print(f'Não foi possível conectar ao {host}')
        return redirect('index')
    print('Autenticação concluída com sucesso.')

    departamento_obj, departamento_created = Departamento.objects.get_or_create(
        codigo = departamento['id'],
        defaults = {
            'name': departamento['name'],
            'url': departamento['url']
        }
    )
    if departamento_created:
        print(f'Departamento {departamento_obj.name} cadastrado com sucesso.')

    for subdepartamento in subdepartamentos:
        subdepartamento_obj, subdepartamento_created = SubDepartamento.objects.get_or_create(
            codigo = subdepartamento['id'],
            departamento = departamento_obj,
            defaults = {
                'name': subdepartamento['name'],
                'url': subdepartamento['url']
            }
        )
        if subdepartamento_created:
            print(f'Subdepartamento {subdepartamento_obj.name} cadastrado.')

        produtos = subdepartamento['products']
        for produto in produtos:
            produto_obj, produto_created = Produto.objects.get_or_create(
                sku = produto['id'],
                subdepartamento = subdepartamento_obj,
                defaults = {
                    'name': produto['name'],
                    'url': produto['url'],
                    'image': produto['image'],
                    'stock_qty': produto['maxCartQuantity'],
                }
            )
            if produto_created:
                print(f'Produto {produto_obj.name} cadastrado.')

            loja_obj, loja_created = Loja.objects.get_or_create(
                name = 'Shopper',
                defaults = {
                    'ehPrincipal': True
                }
            )
            if loja_created:
                print(f'Loja {loja_obj.name} cadastrada.')

            oferta_obj, oferta_created = Oferta.objects.update_or_create(
                produto = produto_obj,
                loja = loja_obj,
                defaults = {
                    'data_captura': datetime.now(tz=get_current_timezone()),
                    'price': formata_preco(produto['price']),
                    'savingPercentage': produto['savingPercentage']
                }
            )
            if oferta_created:
                print(f'Oferta {oferta_obj.price} - {oferta_obj.produto.name} cadastrada.')
            else:
                print(f'Oferta {oferta_obj.price} - {oferta_obj.produto.name} atualizada.')

            ofertas = produto['merchants']
            for oferta in ofertas:
                loja_obj, loja_created = Loja.objects.get_or_create(
                    name = oferta['name'],
                    defaults = {
                        'ehPrincipal': False
                    }
                )
                if loja_created:
                    print(f'Loja {loja_obj.name} cadastrada.')

                oferta_obj, oferta_created = Oferta.objects.update_or_create(
                    produto = produto_obj,
                    loja = loja_obj,
                    defaults = {
                        'data_captura': datetime.now(tz=get_current_timezone()),
                        'price': formata_preco(oferta['price']),
                    }
                )
                if oferta_created:
                    print(f'Oferta {oferta_obj.price} - {oferta_obj.produto.name} cadastrada.')
                else:
                    print(f'Oferta {oferta_obj.price} - {oferta_obj.produto.name} atualizada.')
    return redirect('index')

def get_csrf_token(session):
    """
    Obtém o CSRFToken para autenticação
    """
    url = f'{scheme}://{host}/shpprtkn'
    try:
        req = session.get(url)
    except:
        return ''
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

    try:
        return session.post(url, headers=headers, data=data, cookies=cookies)
    except:
        return ''

def get_user_token(session):
    """
    Obtém o Token de usuário para autenticação
    """
    url = f'{scheme}://{host}/shop/is-client/?deviceUUID=66d3d4b7-6ae4-46b5-b498-75868413a151'
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }
    try:
        req = session.get(url, headers=headers)
    except:
        return ''
    return json.loads(req.text)['userToken']

def get_departamento(nome, user_token, session):
    """
    Retorna os departamentos disponíveis
    """
    host_api = f'siteapi.{host}'
    url = f'{scheme}://siteapi.{host}/catalog/departments'

    headers = {
        'Authorization': f'Bearer {user_token}',
    }

    try:
        req = session.get(url, headers=headers)
    except:
        return ''
    departamentos = json.loads(req.text)['departments']

    for departamento in departamentos:
        if departamento['name'] == nome:
            return departamento

    return ''

def get_subdepartamentos_from_departamento(departamento_id, user_token, session):
    """
    Retorna os subdepartamentos (categorias) e todos os seus produtos
    """
    all = 9999
    url = f'{scheme}://siteapi.{host}/catalog/departments/{departamento_id}?size={all}'
    headers = {
    'Authorization': f'Bearer {user_token}',
    }
    try:
        req = session.get(url, headers=headers)
    except:
        return ''
    return json.loads(req.text)['subdepartments']

def formata_preco(valor):
    return unidecode(valor[3:].replace(',','.'))