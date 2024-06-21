import requests
import sys
import time
from os import system
from PIL import Image
import shutil

def usuario(link : str):
    ingresar = None
    if not ingresar:
        ingresar =  input('\nDesea acceder? (presionar cualquier letra para crear nuevo usuario, enter para ingresar) \n')
        
    user_input = input('\nIngrese el nombre de Usuario: \n')
    pass_input = input('\nIngrese contraseña: \n')

    while ingresar:
        create_payload = '{"user": "'+user_input+'", "password": "'+pass_input+'"}'
        create = requests.post(link + '/nuevo-usuario',
                               headers={'Content-Type': 'application/json',
                                        'accept': 'application/json'},
                                data=create_payload)
        if create.status_code == 201:
            print('\n\n\n Usuario Creado.')
            ingresar = None
        elif create.status_code == 409:
            print(f'\n\n{create.json()}')
            user_input = input('\nIngrese otro nombre de Usuario: \n')
            pass_input = input('\nIngrese contraseña: \n')
        else:
            print('\n\n\n Ha ocurrido un error. El programa se cerrará')
            time.sleep(3)
            sys.exit()

    while not ingresar:   
        payload = f"grant_type=&username={user_input}&password={pass_input}&client_id=&client_secret="
        log = requests.post(link + '/login',
                        headers={'Content-Type': 'application/x-www-form-urlencoded',
                                'accept': 'application/json'},
                        data=payload)
        if log.status_code == 200:
            print('\n\nIngreso exitoso. Acceso a la API durante 60 minutos.\n')
            ingresar = 1
        else:
            print(f'\n\n{log.json()}')
            user_input = input('\nIngrese el nombre de Usuario: \n')
            pass_input = input('\nIngrese contraseña: \n')
    
    headers = {'Authorization': log.json()['token_type'].title() + ' ' + log.json()['access_token'],
               'accept' : 'application/json'}
    return headers


def diccionario_autores(sesion : requests.Session, link):
    for autor in sesion.get(link+'/diccionario-autores').json():
        print(autor)

def diccionario_libros(sesion : requests.Session, link):
    for libro in sesion.get(link+'/diccionario-libros').json():
        print(libro)

def busqueda(sesion : requests.Session, link, tipo):
    query = input('\nIngrese el nombre buscado:\n\n')
    for encontrado in sesion.get(link+f'/busqueda-{tipo}/{query}').json():
        print('\n')
        for item, value in encontrado.items():
            print(f'{item}: {value}')
    return
   
def busqueda_autor(sesion : requests.Session, link):
    return busqueda(sesion, link, 'autor')
    
def busqueda_libro(sesion : requests.Session, link):
    return busqueda(sesion, link, 'libro')                         
    
def busqueda_imagen(sesion : requests.Session, link):
    query = input('\nIngrese el nombre buscado:\n\n')
    response = sesion.get(link+f'/busqueda-imagen/{query}', stream=True)
    with open('img.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    img = Image.open('img.png')
    img.show()


def main():
    post_headers={'Content-Type': 'application/json'}

    ip = '127.0.0.1'#input('Ingrese la ip del servidor: \n')
    puerto = '8000'#input('\nIngrese el puerto al que accede: \n')
    link = f'http://{ip}:{puerto}'

    headers = usuario(link)
    sesion = requests.Session()
    sesion.headers.update(headers)

    diccionario_libros(sesion, link)
    busqueda(sesion, link, 'autor')
    time.sleep(5)


if __name__ == "__main__":
    main()