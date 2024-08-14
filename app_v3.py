from flask import Flask, request, jsonify
import gapi
from promo_utils import *
import pytz
import time
import os
import re

app = Flask(__name__)

BLANK = "",200

GKEY = "ougumc9nis0si9zhvprlzmycdq9if3uo"
APPNAME = "ReimaginaTestGupshup"
CREDS = (APPNAME, GKEY)

REFERENCIA1 = 'https://i.imgur.com/KoQ1Bm0.jpeg'
MARCAS_PARTICIPANTES = 'https://i.imgur.com/h96kOYf.jpeg'
DEPARTAMENTOS = 'https://i.imgur.com/Mc3U8uW.jpg'
IP = 'https://ambrosoli-reimagina.com'
IMAGES_DIR = 'images'

def stage_start(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['text']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor envía un mensaje de texto.")

    else:
       
        text = '*¡Hola, Te doy la bienvenida a la promoción Ambrosoli!*👋\\n\\nYo seré tu asistente virtual para que puedas participar y ganar.\\n\\n*¿Qué deseas hacer?*'
        gapi.send_simple_text(CREDS,bot_number,client_number, text)

        title = ""
        body = "Seleccione:"
        
        options = [ ("Participar",  "participar_btn"),
                    ("Consultas",  "consultas_btn")
                  ]    

        gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)

        update_stage(client_number, "primer_menu")
        return BLANK

    return BLANK




def stage_primer_menu(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['button_reply', 'list_reply']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor responde con un botón de la lista.")

    else:
        
        postback = data['payload']['payload']['postbackText']

        if postback == 'cerrar_btn':

            text = '*¡Gracias por Participar!*\\n\\n¡Anímate a participar nuevamente comprando productos Ambrosoli y ten más opciones de ganar!\\n\\n¡Que tengas un buen día!'
            gapi.send_simple_text(CREDS,bot_number, client_number, text)
            update_stage(client_number, 'start')

        if postback == 'participar_btn':
            
            accepted_tyc = user_registered(client_number)
            
            if not accepted_tyc:
                title = ""
                body = "Puedes participar desde el:\\n\\n*15 de julio hasta el 15 de septiembre*\\n\\nAhora, por favor, lee los términos, condiciones y autorización para el tratamiento de datos en el siguiente link:\\n\\n*https://promoambrosoli.com/tyc*\\n\\n*Tu aprobación se tomara en cuenta para todas tus participaciones.*\\n\\nSeleccione:"
                
                options = [ ("Acepto",  "aceptar_btn"),
                            ("No Acepto",  "denegar_btn")
                            ]    

                gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)
                update_stage(client_number, "accept_tyc") 
                return BLANK
            
            else:
                nombre = get_nombre(client_number)
                text = '*{}, favor toma una sola foto a la boleta de compra, recuerda que:*\\n\\nTienen que poderse leer claramente lo siguiente:\\n- Marcas Participantes\\n- Montos de compra.\\n- Nombre del Proveedor donde has comprado los productos.\\n- Fecha de compra.\\n\\nAdemás debe de ser una boleta impresa.\\nGuíate de la imagen de referencia.\\n\\n⚠️ *Recuerda que hay un monto mínimo de compra para participar en la promoción:*\\n\\n*BODEGUEROS:*\\n- Premio Semanal: 15 soles por boleta.\\n- Premio Mensual: Acumulado de 60 soles. (Mínimo 15 soles por boleta)\\n\\n*MAYORISTAS:*\\n- Premio Semanal: 750 soles por boleta.\\n- Premio Mensual: 1500 soles Acumulado durante el mes. (Mínimo 750 soles por boleta)\\n\\n📷*¡Es tu turno, esperamos la foto de tu boleta!*'.format(nombre)
                gapi.send_image(CREDS,bot_number, client_number, REFERENCIA1, text)
                update_stage(client_number, 'recibir_foto')
        
        if postback == 'consultas_btn':
            title = ""
            body = '¿Que consulta deseas hacer?'
            options_title = "MENU"
            
            options = [ ("Info. Sorteos","",  "info_btn"),
                        ("Ganadores","",  "ganadores_btn"),
                        ("Marcas Participantes","",  "marcas_btn"),
                        ("Otras Consultas", "", "otras_consultas_btn"),
                        ("Participar", "", "participar_btn"),
                        ]    

            gapi.send_list(CREDS, bot_number, client_number, title, body, options_title, options)
            update_stage(client_number, "primer_menu")

        if postback == 'info_btn':
            text = '*I) Duración de la promoción para Bodegueros y Mayoristas:*\\n\\n- Del 15 de julio hasta el 15 de septiembre\\n\\n*II) Detalle de Premios a entregar:*\\n\\nPara los bodegueros:\\n- 5 premios de S/ 500 soles, habiendo 5 ganadores en total cada semana siendo nueve semanas de vigencia de la promoción.\\n- 3 premios de S/ 5,000 soles, habiendo 3 ganadores en total cada mes de vigencia de la promoción.\\n\\nPara los mayoristas:\\n- 1 premio de S/ 500 soles, habiendo 1 ganador en total cada semana de vigencia de la promoción.\\n- 1 premio de S/ 5,000 soles, habiendo 1 ganador en total cada mes de vigencia de la promoción.\\n\\n*III) Requerimientos para participar:*\\n\\nPara Bodegueros:\\n- Para Premios semanales: boleta con al menos 15 soles de compra en marcas participantes.\\n- Para premio Mensual: Acumulado de 60 soles en marcas participantes. (cada boleta minimo debe ser de 15soles)\\n\\nPara Mayoristas:\\n- Para Premios semanales: boleta con al menos 780 soles de compra en marcas participantes.\\n- Para premio Mensual: Acumulado de 1500 soles en marcas participantes. (cada boleta minimo debe ser de 750 soles)\\n\\nPara conocer la fecha de los sorteos y marcas participantes visita los términos y condiciones en: https://promoambrosoli.com/tyc'
            gapi.send_simple_text(CREDS, bot_number, client_number, text)
            
            title = ""
            body = '¿Qué deseas hacer?\\n\\nSeleccione:'
            
            options = [
                        ("Participar",  "participar_btn"),
                        ("Consultas",  "consultas_btn"),
                        ("Nada por ahora",  "cerrar_btn"),
                        ]    

            gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)
            update_stage(client_number, "primer_menu") 
    
        if postback == 'ganadores_btn':
            text = 'Conoce la lista de ganadores en: https://promoambrosoli.com/ganadores'
            gapi.send_simple_text(CREDS, bot_number, client_number, text)
            title = ""
            body = '¿Qué deseas hacer?\\n\\nSeleccione:'
            
            options = [
                        ("Participar",  "participar_btn"),
                        ("Consultas",  "consultas_btn"),
                        ("Nada por ahora",  "cerrar_btn"),
                        ]    

            gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)
            update_stage(client_number, "primer_menu")

        if postback == 'marcas_btn':

            text = 'Estas son las marcas participantes en la promoción.'
            gapi.send_image(CREDS, bot_number, client_number, MARCAS_PARTICIPANTES, text)


            title = ""
            body = '¿Qué deseas hacer?\\n\\nSeleccione:'
            options = [
                        ("Participar",  "participar_btn"),
                        ("Consultas",  "consultas_btn"),
                        ("Nada por ahora",  "cerrar_btn"),
                        ]    

            gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)
            update_stage(client_number, "primer_menu") 

        if postback == 'otras_consultas_btn':
            text = '*Gracias por ponerte en contacto.*\\n\\nPara cualquier duda adicional referida a la promoción puedes escribir al siguiente correo:\\n\\n*clientes@molitalia.com.pe*'
            gapi.send_simple_text(CREDS, bot_number, client_number, text)
            title = ""
            body = '¿Qué deseas hacer?\\n\\nSeleccione:'
            
            options = [
                        ("Participar",  "participar_btn"),
                        ("Consultas",  "consultas_btn"),
                        ("Nada por ahora",  "cerrar_btn"),
                        ]    

            gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)
            update_stage(client_number, "primer_menu") 

        if postback == 'test_btn':
            gapi.send_image(CREDS,bot_number, client_number, DEPARTAMENTOS, "¿En qué ciudad compraste tus productos?\\n\\n*Escribe el número que corresponde a tu ciudad según la imagen.*")
            #gapi.enviar_imagen_gupshup(CREDS,bot_number,client_number, DEPARTAMENTOS, 'TEST')
            update_stage(client_number, "start")

        return BLANK


    return BLANK


def stage_accept_tyc(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['button_reply', 'list_reply']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor responde con un botón de la lista.")

    else:
        
        postback = data['payload']['payload']['postbackText']
        
        if postback == 'aceptar_btn':
            text = 'Por favor escribe tus nombres y apellidos.'
            gapi.send_simple_text(CREDS,bot_number,client_number,text)
            update_stage(client_number, "check_nombre")
            
        if postback == 'denegar_btn':
            text = 'Para participar, necesitas primero aceptar los términos y condiciones.\\n\\n*¡Vuelve a escribirnos cuando estés listo!*'
            gapi.send_simple_text(CREDS,bot_number,client_number,text)
            update_stage(client_number, "start")
            

        return BLANK


    return BLANK




def stage_check_nombre(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['text']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor escribe un nombre y apellidos válidos.\\n\\n(Recuerda que para participar tienes que usar tu nombre, *NO* la razón social.)")

    else:
        
        message = data['payload']['payload']['text']
        
        if not validar_nombre(message):
            gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor escribe un nombre y apellidos válidos.")
        
        else:
            gapi.send_simple_text(CREDS,bot_number, client_number, "Ahora, escribe tu número de DNI/CE.\\n\\n(Recuerda que para participar, tienes que usar tu DNI/CE, *NO* tu RUC)")
            collection = db['ambrosoli-promo-usuarios']
            resultado = collection.update_one(
            {"_id": client_number},
            {"$set": {"nombre": message.title()}}
            )
            update_stage(client_number, "check_dni")

        return BLANK


    return BLANK



def stage_check_dni(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['text']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor escribe un DNI/CE válido.")

    else:
        
        message = data['payload']['payload']['text']
        
        if not validar_dni(message):
            gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor escribe un DNI/CE válido.")
        
        else:

            gapi.send_image(CREDS,bot_number, client_number, DEPARTAMENTOS, "¿En qué ciudad compraste tus productos?\\n\\n*Escribe el número que corresponde a tu ciudad según la imagen.*")
            collection = db['ambrosoli-promo-usuarios']
            resultado = collection.update_one(
            {"_id": client_number},
            {"$set": {"dni": message.title()}}
            )
            update_stage(client_number, "check_departamento")

        return BLANK


    return BLANK


def stage_check_departamento(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['text']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor escribe un departamento válido.")

    else:
        
        message = data['payload']['payload']['text']
        
        if not validar_departamento(message):
            gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor escribe un departamento válido.")
        
        else:
            

            depa = obtener_departamento_estandarizado(message)
            collection = db['ambrosoli-promo-usuarios']
            resultado = collection.update_one(
            {"_id": client_number},
            {"$set": {"departamento": depa}}
            )
            region = get_region(depa)
            resultado = collection.update_one(
            {"_id": client_number},
            {"$set": {"region": region}}
            )


            title = ""
            body = 'Selecciona tu tipo de negocio.'
            
            options = [ ("Bodega", "bodega_btn"),
                        ("Mayorista",  "mayorista_btn")
                        ]    

            gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)
            

            update_stage(client_number, "check_negocio")

        return BLANK


    return BLANK



def stage_check_negocio(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['button_reply', 'list_reply']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor usa uno de los botones para seleccionar tu tipo de negocio.")

    else:
        
        postback = data['payload']['payload']['postbackText']
        tipo_negocio = None

        if postback == 'bodega_btn':
            tipo_negocio = 'BODEGA'
            collection = db['ambrosoli-promo-usuarios']
            resultado = collection.update_one(
            {"_id": client_number},
            {"$set": {"tipo_negocio": tipo_negocio}}
            )

        if postback == 'mayorista_btn':
            tipo_negocio = 'MAYORISTA'
            collection = db['ambrosoli-promo-usuarios']
            resultado = collection.update_one(
            {"_id": client_number},
            {"$set": {"tipo_negocio": tipo_negocio}}
            )

        nombre = get_nombre(client_number)
        dni = get_dni(client_number)
        departamento = get_departamento(client_number)
        body = '*¡Muy bien!*\\n\\nTus participaciones en esta promoción estarán asociadas con los siguientes datos.\\n\\nEn adelante ya no será necesario reingresarlos:\\n\\n*NOMBRE:* {}\\n*DNI/CÉDULA:* {}\\n*UBICACIÓN DE NEGOCIO:* {}\\n*TIPO DE NEGOCIO:* {}\\n\\nRecuerda que estos datos\\n\\n*NO SE PUEDEN CAMBIAR.*\\n\\nSerán validados y en caso no estar correctos tu participación será anulada.\\n\\n*¿Están correctos tus datos?*'.format(nombre,dni,departamento,tipo_negocio)
        
        title =''
        
        options = [ ("Sí, Correctos",  "correctos_btn"),
                    ("Corregir Datos",  "corregir_btn")
                    ]    

        gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)
        

        update_stage(client_number, "check_datos")

        return BLANK


    return BLANK




def stage_check_datos(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['button_reply', 'list_reply']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor usa uno de los botones para seleccionar una opción.")

    else:
        
        postback = data['payload']['payload']['postbackText']
        
        if postback == 'correctos_btn':
            update_register(client_number)

            nombre = get_nombre(client_number)
            text = '*{}, favor toma una sola foto a la boleta de compra, recuerda que:*\\n\\nTienen que poderse leer claramente lo siguiente:\\n- Marcas Participantes\\n- Montos de compra.\\n- Nombre del Proveedor donde has comprado los productos.\\n- Fecha de compra.\\n\\nAdemás debe de ser una boleta impresa.\\nGuíate de la imagen de referencia.\\n\\n⚠️*Recuerda que hay un monto mínimo de compra para participar en la promoción:*\\n\\n*BODEGUEROS:*\\n- Premio Semanal: 15 soles por boleta.\\n- Premio Mensual: Acumulado de 60 soles. (Mínimo 15 soles por boleta)\\n\\n*MAYORISTAS:*\\n- Premio Semanal: 750 soles por boleta.\\n- Premio Mensual: 1500 soles Acumulado durante el mes. (Mínimo 750 soles por boleta)\\n\\n📷*¡Es tu turno, esperamos la foto de tu boleta!*'.format(nombre)
            gapi.send_image(CREDS,bot_number, client_number, REFERENCIA1, text)
            update_stage(client_number, 'recibir_foto')

        if postback == 'corregir_btn':
            
            text = 'Por favor escribe tus nombres y apellidos'
            gapi.send_simple_text(CREDS,bot_number, client_number, text)

            update_stage(client_number, "check_nombre")

        return BLANK


    return BLANK




def stage_recibir_foto(client_number, bot_number, data):

    appname = data['app']
    message_type = data['type']
    post_type = data['payload']['type']

    if post_type not in ['image']:
        
        gapi.send_simple_text(CREDS,bot_number, client_number, "Por favor, envía una imagen")

    else:
        
        #DESCARGAR IMAGEN
        url = data['payload']['payload']['url']
        participaciones = get_participaciones(client_number) + 1
        id_part = client_number + '_' + str(participaciones)
        image_url = descargar_imagen(url, id_part + '.jpg', IP)

        usuario = get_user(client_number)
        ts = get_timestamp_peru()

        usuario['_id'] = id_part
        usuario['numero'] = client_number
        usuario['hora'] = ts
        usuario['week'] = get_week_number(ts)
        usuario['imagen'] = image_url

        del usuario['registrado']
        del usuario['participaciones']
        del usuario['stage']



        #POST SHEETDB
        participacion = {}

        participacion['ID'] = id_part
        participacion['nombre'] = usuario['nombre']
        participacion['numero'] = client_number
        participacion['dni'] = usuario['dni']
        participacion['region'] = usuario['region']
        participacion['departamento'] = usuario['departamento']
        participacion['negocio'] = usuario['tipo_negocio']
        participacion['semana'] = usuario['week']
        participacion['hora'] = ts
        participacion['imagen'] = image_url

        posturl = 'https://sheetdb.io/api/v1/9kq3wny9peqi8'        
        response = requests.post(posturl, json=participacion)

        # ACTUALIZAR PARTICIPACION
        aumentar_participacion(client_number)
        update_participaciones(client_number,participaciones)
        collection = db['ambrosoli-promo-participaciones']
        resultado = collection.insert_one(usuario)

        text = '*Felicitaciones, la boleta ha sido recibida.*\\n\\nEn caso resultes ganador del sorteo, revisaremos la boleta y de estar conforme nos comunicaremos contigo por WhatsApp desde el +51 908 838 585.'
        gapi.send_image(CREDS,bot_number, client_number,MARCAS_PARTICIPANTES, text)


        title = ''
        body = '¿Qué deseas hacer?'
        options = [ ("Participar",  "participar_btn"),
                    ("Consultas", "consultas_btn"),
                    ("Nada por ahora",  "cerrar_btn")
                    ]    

        gapi.send_buttons(CREDS, bot_number, client_number, title, body, options)
        
        update_stage(client_number,"primer_menu")

        return BLANK





    return BLANK


@app.route('/images/<filename>', methods=['GET'])
def serve_image(filename):
    # Asegúrate de que el nombre del archivo termine en .jpg
    if not filename.endswith('.jpg'):
        abort(404)  # No encontrado

    # Sirve el archivo de la carpeta 'imagenes', si existe
    if os.path.isfile(os.path.join(IMAGES_DIR, filename)):
        return send_from_directory(IMAGES_DIR, filename)
    else:
        abort(404)  # No encontrado


@app.route('/test/<date>', methods=['GET'])
def check_date(date):
    return jsonify({"week":get_week_number(date)})



@app.route('/receive_message', methods=['POST'])
def receive_message():

    data = request.json
    print("DATA",data)

    event_type = data['type']

    if event_type in ['user-event','message-event','billing-event']:
        print("BLANK")
        return BLANK

    
    post_type = data['payload']['type']
    if post_type in ['sandbox-start', 'enqueued','delivered','sent','read']:
        print("BLANK")
        return BLANK
    

    #print(data)
    client_number = data['payload']['sender']['phone']
    bot_number = "51908865790"

    #Revisar si el usuario existe y sacar su stage
    stage = get_stage(client_number)

    if stage == None: #Cliente no existe, toca registrar
        stage = insert_user(client_number)


    #Revisar mensaje es valido
    if post_type not in ['text','button_reply', 'list_reply','image','button_reply', 'list_reply','message']:
        gapi.send_simple_text(CREDS, bot_number, client_number, "Mensaje inválido")
        stage = get_stage(client_number)
        update_stage(client_number, stage)


    if stage == "start":
        stage_start(client_number, bot_number, data)
    elif stage == "primer_menu":
        stage_primer_menu(client_number, bot_number, data)     
    elif stage == "accept_tyc":
        stage_accept_tyc(client_number, bot_number, data) 
    elif stage == "check_nombre":
        stage_check_nombre(client_number, bot_number, data) 
    elif stage == "check_dni":
        stage_check_dni(client_number, bot_number, data) 
    elif stage == "check_departamento":
        stage_check_departamento(client_number, bot_number, data) 
    elif stage == "check_negocio":
        stage_check_negocio(client_number, bot_number, data)
    elif stage == "check_datos":
        stage_check_datos(client_number, bot_number, data) 
    elif stage == "recibir_foto":
        stage_recibir_foto(client_number, bot_number, data) 
    return BLANK

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
