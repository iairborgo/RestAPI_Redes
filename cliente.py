import requests
import sys
import time
from os import system
from PIL import Image
import shutil
import re
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
    print('\n\n')

def diccionario_libros(sesion : requests.Session, link):
    for libro in sesion.get(link+'/diccionario-libros').json():
        print(libro)
    print('\n\n')

def busqueda(sesion : requests.Session, link, tipo):
    query = input('\nIngrese el nombre buscado:\n\n')
    for encontrado in sesion.get(link+f'/busqueda-{tipo}/{query}').json():
        print('\n')
        for item, value in encontrado.items():
            print(f'{item}: {value}')
    print('\n\n')
   
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
    print('\n\n')

def actualizar_link(sesion : requests.Session, link):
    libro = input('\nIngrese el nombre del libro al que va a realizar la modificacion:\n')
    path = input('Ingrese el subdirectorio de la wiki (ej https://es.wikipedia.org/wiki/Ficciones ingreso Ficciones):\n')
    idioma = input('Ingrese idioma de la wiki (si es en español puede tocar enter).\n')
    idioma = f'?idioma={idioma}' if idioma else ''
    response = sesion.put(link+f'/actualizar-link/{libro}?path={path}{idioma}')
    print(f'\n{response.json()}\n')

def nuevo_libro(sesion : requests.Session, link):
    post_headers={'Content-Type': 'application/json'}
    print('Para ingresar libro a la base de datos se requiere que ingrese los siguientes campos:\n')
    autor = input('Autor (Unknown si desconoce):                         ').title()
    pais = input('Pais de origen:                                       ').title()
    lengua = input('Lenguaje escrito:                                     ').title()
    wiki = input('Link Wikipedia:                                       ')
    paginas = input('Cantidad de páginas:                                  ')
    titulo = input('Nombre del libro:                                     ').title()
    anio = input('Año de lanzamiento:                                   ')

    payload = ('{"author": "'+autor+
               '","country": "'+pais+
               '","language": "'+lengua+
               '","link": "'+wiki+
               '","pages": '+paginas+
               ',\"title":"'+titulo+
               '","year": '+anio+'}')
    response = sesion.post(link + '/nuevo-libro', data = payload, headers=post_headers)
    print(f'\n{response.json()}\n')

def eliminar_libro(sesion : requests.Session, link):
    libro = input('\nIngrese el nombre del libro que quiere eliminar:\n')
    response = sesion.delete(link+f'/eliminar-libro?libro={libro}')
    print(f'\n{response.json()}\n')

def salir(sesion, link):
    system('cls')
    print("Adios")
    time.sleep(1)
    sys.exit()

def display_menu(menu):
    print('\n')
    for k, function in menu.items():
        print(k, re.sub('_', ' ',function.__name__).capitalize())
    print('\n')

def main():
    ip = input('Ingrese la ip del servidor: \n')
    puerto = input('\nIngrese el puerto al que accede: \n')
    link = f'http://{ip}:{puerto}'

    headers = usuario(link)
    sesion = requests.Session()
    sesion.headers.update(headers)
    functions_names = [diccionario_autores, diccionario_libros,
                       busqueda_autor, busqueda_libro, busqueda_imagen,
                       actualizar_link, eliminar_libro, nuevo_libro,
                       salir]
    menu_items = dict(enumerate(functions_names, start = 1))
    while True:
        display_menu(menu_items)
        select = int(input('Ingresa el numero de la llamada que quiere realizar:        '))
        selected = menu_items[select]
        selected(sesion, link)


if __name__ == "__main__":
    main()