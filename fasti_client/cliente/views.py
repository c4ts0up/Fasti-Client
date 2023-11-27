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

    url = settings.URL_DB + 'Usuarios?celular=eq.' + str(id) + '&select=celular,nombre'

    cabeceras = {
        'apikey' : settings.APIKEY,
        'Authorization' : 'Bearer ' + settings.APIKEY
    }

    response = requests.get(url, headers=cabeceras)
    print(response.text)

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


@csrf_exempt
def get_turno_espera(request, id: int):
    """
    Obtiene toda la información para la pantalla de turno de espera

    Args:
        request (HttpRequest): request con body vacío 
        id (int): ID de la persona a consultar
    """
    try:
        url_usuarios = settings.URL_DB + "Usuarios?celular=eq." + str(id)
        url_clientes = settings.URL_DB + "Clientes?celular=eq." + str(id)

        cabeceras = {
            "apikey" : settings.APIKEY,
            "Authorization" : 'Bearer ' + settings.APIKEY,
            "Content-Type" : "application/json",
            "Prefer" : "return=minimal"
        }

        # consulta usuario y cliente
        response_usuario = requests.get(url_usuarios, headers=cabeceras)
        response_cliente = requests.get(url_clientes, headers=cabeceras)

        # carga las respuestas
        # 1 elemento -> [0]
        data_usuario = json.loads(response_usuario.text)[0]
        data_cliente = json.loads(response_cliente.text)[0]

        # consulta fila
        url_fila = settings.URL_DB + "Filas?id=eq." + str(data_cliente.get("fila"))
        response_fila = requests.get(url_fila, headers=cabeceras)
        data_fila = json.loads(response_fila.text)[0]

        tiempoEspera = get_tiempo_espera(
            data_fila.get("tiempoAcumulado"), 
            data_fila.get("turnosResueltos"),
            data_fila.get("turnoActual"),
            data_cliente.get("turno")
        )
        
        # organiza respuesta
        payload = {
            "turnoCliente" : data_cliente.get("turno"),
            "tiempoEspera" : tiempoEspera,
            "horaTurno" : data_cliente.get("horaTurno"),
            "idFila" : data_cliente.get("fila"),
            "turnoActual": data_fila.get("turnoActual"),
            "nombreCliente" : data_usuario.get("nombre")
        }

        return JsonResponse(payload, status=200)
    except:
        return JsonResponse({}, status=500)


def get_tiempo_espera(tAcc: int, res: int, act: int, cli: int) -> int:
    """
    Retorna la estimación de tiempo de espera para el cliente

    Args:
        tAcc (int): tiempo acumulado de espera de los turnos resueltos
        res (int): # turnos resueltos / atendidos / cancelados
        act (int): # turno actual en la fila
        cli (int): # turno del cliente

    Returns:
        int: estimación de tiempo de espera para que el cliente pase
    """

    if res == 0:
        return 0
    else:
        return int(tAcc/res * (cli - act))


