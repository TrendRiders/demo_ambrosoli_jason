from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import time
import os
import pymongo
import http.client
import ssl
import unicodedata
from datetime import datetime, timedelta, timezone
import pytz
import re
from pymongo import MongoClient
from bson.objectid import ObjectId  # Importa ObjectId
from http.server import BaseHTTPRequestHandler, HTTPServer


#MONGO CREDENTIALS
mongo_user = 'Molitalia'
mongo_pwd = 'kg6Ui75GhtdHTESy45ygKUgo78IghTY54s'
server_ip = '34.125.134.86:27017'
auth_db = 'admin'
client = MongoClient('mongodb://{}:{}@{}/?authSource={}'.format(mongo_user,mongo_pwd,server_ip,auth_db))
db = client['moli-codigos']  


departamentos = [
    "Amazonas", "Ancash", "Apurimac", "Arequipa", "Ayacucho", "Cajamarca",
    "Callao", "Cusco", "Huancavelica", "Huanuco", "Ica", "Junin", 
    "La Libertad", "Lambayeque", "Lima", "Loreto", "Madre de Dios", 
    "Moquegua", "Pasco", "Piura", "Puno", "San Martin", "Tumbes", "Tacna", 
     "Ucayali"
]

departamentos_dict = {str(i).zfill(2): dept for i, dept in enumerate(departamentos, start=1)}

departamentos_dict.update({str(i): dept for i, dept in enumerate(departamentos, start=1)})



def get_region(departamento):

    LIMA = {"lima", "callao", "15", "7"}
    ORIENTE = {"amazonas", "loreto", "san martin", "pasco", "tumbes", "1", "16", "22", "19", "23"}
    CENTRO = {"junin", "ica", "ancash", "huancavelica", "huanuco", "ucayali", "12", "11", "2", "9", "10", "25"}
    SUR = {"cusco", "arequipa", "tacna", "madre de dios", "ayacucho", "puno", "apurimac", "moquegua", "8", "4", "24", "17", "5", "21", "3", "18"}
    NORTE = {"cajamarca", "la libertad", "piura", "lambayeque", "6", "13", "20", "14"}

    departamento = departamento.lower()
    
    if departamento in LIMA:
        return "LIMA"
    elif departamento in ORIENTE:
        return "ORIENTE"
    elif departamento in CENTRO:
        return "CENTRO"
    elif departamento in SUR:
        return "SUR"
    elif departamento in NORTE:
        return "NORTE"
    

def register(numero, dni, departamento): 
    collection = db['ambrosoli-promo-usuarios-registrados']
    documento = {
        "_id" : numero,
        "dni": dni,
        "codigo": codigo
    }
    try:
        resultado = collection.insert_one(documento)
        print(f"Documento insertado con el _id: {resultado.inserted_id}")
        return jsonify({}),201
    except Exception as e:
        print(f"Error al insertar el documento: {e}")
        return jsonify({'msj':'error al insertar'}),204


def get_week_number(timestamp):
    start_date = datetime(2024, 7, 15)
    
    timestamp_date = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    delta_days = (timestamp_date - start_date).days
    
    week_number = delta_days // 7 + 1
    
    return week_number

def get_timestamp_peru():
    # Define la zona horaria UTC-5
    utc_minus_5 = timezone(timedelta(hours=-5))
    # Obtén la hora actual en la zona horaria UTC-5
    now_peru = datetime.now(utc_minus_5)
    # Convierte a formato ISO 8601 con milisegundos en la zona horaria UTC-5
    timestamp = now_peru.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return timestamp


def validar_nombre(s):
    if re.search(r'\d', s):
        return False
    
    palabras = s.split()
    num_palabras = len(palabras)
    
    if num_palabras < 2 or num_palabras > 6:
        return False
    
    return True

def validar_dni(s):
    return s.isdigit() and len(s) in [8, 9]


def estandarizar_texto(texto):
    # Eliminar acentos
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Capitalizar palabras
    texto = texto.title()
    return texto

def obtener_departamento_estandarizado(texto):
    texto_estandarizado = estandarizar_texto(texto)
    
    # Validar por nombre del departamento
    if texto_estandarizado in departamentos:
        return texto_estandarizado
    
    # Validar por número del departamento
    if texto_estandarizado in departamentos_dict:
        return estandarizar_texto(departamentos_dict[texto_estandarizado])
    
    return None

def validar_departamento(texto):
    texto_estandarizado = estandarizar_texto(texto)
    print('TEXT:',texto_estandarizado)
    # Validar por nombre del departamento
    if texto_estandarizado in departamentos:
        return True
    
    # Validar por número del departamento
    if texto_estandarizado in departamentos_dict:
        return True
    
    return False



def get_stage(numero): #Retorna string de stage o None
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': numero})
    if resultado == None:
        return None
    else:
        return resultado['stage']

def user_registered(client_number): #verificar si ya se registró (si aceptó TyC)
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': client_number})
    
    if resultado['registrado'] == False:
        return False
    else:
        return True

def get_user(numero): #Retorna string de stage o None
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': numero})
    return resultado

def get_stage(numero): #Retorna string de stage o None
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': numero})
    if resultado == None:
        return None
    else:
        return resultado['stage']



def descargar_imagen(url, nombre_archivo, ip,  carpeta='images'):
    # Crear la carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # Ruta completa donde se guardará la imagen
    ruta_completa = os.path.join(carpeta, nombre_archivo)

    # Descargar la imagen
    response = requests.get(url)
    if response.status_code == 200:
        with open(ruta_completa, 'wb') as f:
            f.write(response.content)
        print(f'Imagen guardada en {ruta_completa}')
        return ip + '/' + carpeta + '/' + nombre_archivo
    else:
        print('Error al descargar la imagen:', response.status_code)
        return None


def get_curr_code(numero): #Retorna string de stage o None
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': numero})
    if resultado == None:
        return None
    else:
        return resultado['curr_code']

def get_dni(numero): #Retorna string de dni o None
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': numero})
    if resultado == None:
        return None
    else:
        return resultado['dni']

def get_departamento(numero): #Retorna string de dni o None
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': numero})
    if resultado == None:
        return None
    else:
        return resultado['departamento']

def get_nombre(numero): #Retorna string de nombre o None
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': numero})
    if resultado == None:
        return None
    else:
        return resultado['nombre']

def get_participaciones(numero): #Retorna string de nombre o None
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one({'_id': numero})
    if resultado == None:
        return None
    else:
        return resultado['participaciones']

def insert_user(numero): #Inserta el nuevo usuario
    collection = db['ambrosoli-promo-usuarios']
    documento = {
        "_id" : numero,
        "stage": "start",
        "registrado" : False,
        "participaciones" : 0
    }
    try:
        resultado = collection.insert_one(documento)
        return "start"
    except Exception as e:
        return None

def update_stage(numero, stage): #Actualiza el stage de un usuario y devuelve el nuevo documento
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one_and_update(
    {"_id": numero},  
    {"$set": {"stage": stage}},
    return_document=pymongo.ReturnDocument.AFTER  
    )

    if resultado == None:
        return jsonify({})
    else:
        return jsonify(resultado)

def update_participaciones(numero, participaciones): #Actualiza el stage de un usuario y devuelve el nuevo documento
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one_and_update(
    {"_id": numero},  
    {"$set": {"participaciones": participaciones}},
    return_document=pymongo.ReturnDocument.AFTER  
    )

    if resultado == None:
        return jsonify({})
    else:
        return jsonify(resultado)

def update_register(numero): #Actualiza el stage de un usuario y devuelve el nuevo documento
    collection = db['ambrosoli-promo-usuarios']
    resultado = collection.find_one_and_update(
    {"_id": numero},  
    {"$set": {"registrado": True}},
    return_document=pymongo.ReturnDocument.AFTER  
    )
    if resultado == None:
        return jsonify({})
    else:
        return jsonify(resultado)



def verificar_participacion(cliente_id):
    # Obtener la fecha actual sin horas, minutos ni segundos
    collection = db['ambrosoli-promo-participaciones-diarias']
    fecha_actual = datetime.now().date()
    fecha_actual_str = fecha_actual.isoformat()

    # Buscar la participación del cliente en la base de datos
    participacion = collection.find_one({"_id": cliente_id})

    if participacion:
        ultima_fecha = participacion['ultima_fecha']
        conteo = participacion['conteo']
        
        if ultima_fecha == fecha_actual_str:
            # Si la fecha de la última participación es hoy, incrementar el conteo
            if conteo >= 3:
                return False
            else:
                return True
        else:
            # Si la fecha de la última participación no es hoy, reiniciar el conteo y actualizar la fecha
            collection.update_one(
                {"_id": cliente_id},
                {"$set": {"conteo": 0, "ultima_fecha": fecha_actual_str}}
            )
            return True
    else:
        # Si no existe un registro de participación para el cliente, crear uno nuevo
        collection.insert_one({
            "_id": cliente_id,
            "conteo": 0,
            "ultima_fecha": fecha_actual_str
        })
        return True


def aumentar_participacion(cliente_id):
    # Obtener la fecha actual sin horas, minutos ni segundos
    collection = db['ambrosoli-promo-participaciones-diarias']
    
    collection.update_one(
                    {"_id": cliente_id},
                    {"$inc": {"conteo": 1}}
                )

    return