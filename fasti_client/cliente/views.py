import json
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings


@csrf_exempt
def supabase_parse_response(response): 
    """
    Parsea la respuesta desde Supabase en JSON entendible por Python

    Args:
        response (_type_): _description_
    """
    return json.loads(response.text[1:-1])


@csrf_exempt
def hello_world(request):
    return HttpResponse('Hello world')


@csrf_exempt
def perfil(request, id: int):
    """
    Maneja las operaciones sobre el perfil de un cliente

    Args:
        request (HttpRequest): request de tipo
        id (int): ID del cliente
    """

    # obtiene el perfil
    if request.method == 'GET':
        return get_perfil(request, id)
    
    # actualiza el perfil
    elif request.method == 'PUT':
        return put_perfil(request, id)
    
    # borra la cuenta
    elif request.method == 'DELETE':
        return del_cliente(request, id)
    
    # crea la cuenta
    elif request.method == 'POST':
        return post_cliente(request, id)
    
    # bad request
    else:
        return JsonResponse(status=400)
    

@csrf_exempt
def get_perfil(request, id: int):
    """
    Obtiene nombre y celular del cliente

    Args:
        request (HttpRequest): GET del perfil
        id (int): ID del cliente
    """

    url = settings.URL_DB + 'Usuarios?celular=eq.' + str(id)

    cabeceras = {
        'apikey' : settings.APIKEY,
        'Authorization' : 'Bearer ' + settings.APIKEY
    }

    response = requests.get(url, headers=cabeceras)

    return JsonResponse(supabase_parse_response(response))


@csrf_exempt
def put_perfil(request, id: int):
    """
    Actualiza el perfil con un nuevo nombre

    Args:
        request (HttpRequest): PUT del perfil
        id (int): ID del cliente
    """
    
    url = settings.URL_DB + 'Usuarios?celular=eq.' + str(id)

    # extrae el body del request
    json_data = json.loads(request.body)
    nuevo_nombre = json_data.get('nombre')

    cabeceras = {
        "apikey" : settings.APIKEY,        
        "Authorization" : "Bearer " + settings.APIKEY,
        "Content-Type" : "application/json",
        "Prefer" : "return=minimal"
    }

    data = {
        "nombre" : nuevo_nombre
    }

    response = requests.patch(url, headers=cabeceras, json=data)

    return JsonResponse({}, status=response.status_code)


@csrf_exempt
def post_cliente(request, id: int):
    """
    Crea la cuenta de un cliente

    Args:
        request (HttpRequest): DELETE del perfil
        id (int): ID del cliente
    """
    
    url_usuarios = settings.URL_DB + 'Usuarios'
    url_clientes = settings.URL_DB + 'Clientes'

    cabeceras = {
        "apikey" : settings.APIKEY,        
        "Authorization" : "Bearer " + settings.APIKEY,
        "Content-Type" : "application/json",
        "Prefer" : "return=minimal"
    }

    json_data = json.loads(request.body)

    # crea el usuario
    data_usuarios = {
        "celular": str(json_data.get("celular")),
        "nombre" : str(json_data.get("nombre")),
        "clave": str(json_data.get("clave"))
    }

    data_clientes = {
        "celular": str(json_data.get("celular"))
    }

    response_usuarios = requests.post(url_usuarios, headers=cabeceras, json=data_usuarios)
    print(response_usuarios.status_code)
    
    if response_usuarios.status_code == 201:
        response_clientes = requests.post(url_clientes, headers=cabeceras, json=data_clientes)
    else:
        response_clientes = JsonResponse({}, status=response_usuarios.status_code)

    return JsonResponse({}, status=response_clientes.status_code)


@csrf_exempt
def del_cliente(request, id: int):
    """
    Borra la cuenta

    Args:
        request (HttpRequest): DELETE del perfil
        id (int): ID del cliente
    """
    
    url_clientes = settings.URL_DB + 'Clientes?celular=eq.' + str(id)
    url_usuarios = settings.URL_DB + 'Usuarios?celular=eq.' + str(id)

    cabeceras = {
        "apikey" : settings.APIKEY,        
        "Authorization" : "Bearer " + settings.APIKEY
    }

    data = {}

    response_clientes = requests.delete(url_clientes, headers=cabeceras)

    if response_clientes.status_code == 204:
        response_usuarios = requests.delete(url_usuarios, headers=cabeceras)
    else:
        response_usuarios = JsonResponse({}, status=response_clientes.status_code)
        

    return JsonResponse({}, status=response_usuarios.status_code)