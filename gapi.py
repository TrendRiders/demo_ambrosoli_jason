import requests
import json

def send_simple_text(creds, bot_number, client_number, text):

    appname = creds[0]
    key = creds[1]

    url = "https://api.gupshup.io/wa/api/v1/msg"

    payload = {
        "source": bot_number,
        "destination": client_number,
        "src.name": appname,
        "message": "{\"context\":{\"msgId\":\"string\"},\"text\":\"" + text + "\",\"type\":\"text\",\"previewUrl\":false}"
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "apikey" : key
    }

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)

def send_image(creds, bot_number, client_number, image_link, caption):
    appname = creds[0]
    key = creds[1]

    url = "https://api.gupshup.io/wa/api/v1/msg"

    print(image_link)

    msg =  '{"type":"image","caption":"' + caption + '","originalUrl":"' + image_link + '","previewUrl":""}'
    
    print(msg)
    payload = {
        "source": bot_number, 
        "destination": client_number,
        "src.name": appname,
        "message": msg
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "apikey" : key

    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 202:
        print('Imagen enviada con éxito.')
    else:
        print(f'Error al enviar la imagen: {response.status_code}')
        print(response.text)




def send_list(creds, bot_number, client_number, list_title, list_body, options_title, options):
    appname = creds[0]
    key = creds[1]

    
    url = "https://api.gupshup.io/wa/api/v1/msg"

    base = '[{"options":['
    for option in options:
        
        title = option[0]
        description = option[1]
        postback = option[2]

        base = base + '{"type":"text","title":"' + title + '","description":"' + description + '","postbackText":"' + postback + '","encodeText":true}'

        if option != options[len(options)-1]:
            base = base + ','
    
    base = base + ']'


    msg =  '{"type":"list","title":"'+ list_title + '","body":"' + list_body +'","msgid":"IDENTIFIER_ID","globalButtons":[{"type":"text","title":"'+ options_title + '"}],"items": '+ base +'}]}'

    payload = {
        "message": msg ,
        "source": bot_number,
        "destination": client_number,
        "src.name": appname
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "apikey" : key

    }

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)



def send_buttons(creds, bot_number, client_number, buttons_title, buttons_body, options):
    appname = creds[0]
    key = creds[1]

    
    url = "https://api.gupshup.io/wa/api/v1/msg"

    base = '"options":['
    for option in options:
        
        title = option[0]
        postback = option[1]

        base = base + '{"type":"text","title":"' + title + '","postbackText":"' + postback + '"}'

        if option != options[len(options)-1]:
            base = base + ','
    
    base = base + ']'


    msg =  '{"type":"quick_reply","msgid":"", "content":{"type":"text", "header":"'+ buttons_title +'","text":"'+buttons_body+'","caption":"" }, '+base+' }'

    payload = {
        "message": msg ,
        "source": bot_number,
        "destination": client_number,
        "src.name": appname
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "apikey" : key

    }

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)



        
   


