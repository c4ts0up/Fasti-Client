import datetime
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
def entrar_fila(request, id: str):
    """
    Entra a la fila con el ID dado

    Args:
        request (HttpRequest): request de la fila
        id (str): ID de la fila
    """

    url_fila = settings.URL_DB + "Filas?id=eq." + id

    cabeceras = {
        "apikey" : settings.APIKEY,        
        "Authorization" : "Bearer " + settings.APIKEY,
        "Content-Type" : "application/json",
        "Prefer" : "return=minimal"
    }

    request_json = json.loads(request.body)
    celular_cliente = request_json.get("celular")

    # consigue la fila actual
    response = requests.get(url, headers=cabeceras)
    fila_json = supabase_parse_response(response)

    data_fila = {
        "turnoActual": fila_json.get("turnoActual") + 1,
        "turnosOtorgados": fila_json.get("turnosOtorgados") + 1
    }

    # actualiza la fila actual
    response = requests.patch(url_fila, headers=cabeceras, json=data_fila)

    if response.status_code != 204:
        return JsonResponse({}, status=204)
    

    # actualiza al cliente actual
    url_cliente = settings.URL_DB + "Cliente?celular=eq." + celular_cliente

    data_cliente = {
        "fila" : id,
        "turno" : data_fila.get("turnoActual"),
        "hora_turno" : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    response = requests.patch(url_cliente, headers=cabeceras, json=data_cliente)

    return JsonResponse({}, status=response.status_code)
