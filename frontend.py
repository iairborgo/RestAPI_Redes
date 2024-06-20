import requests
import sys
import time
from os import system

def usuario(link):
    ingresar = None
    if not ingresar:
        ingresar =  input('Desea acceder? (presionar cualquier letra para crear nuevo usuario, enter para ingresar) \n')
        
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
            print('\n\nIngreso exitoso. Acceso a la API durante 60 minutos.')
        else:
            print(f'\n\n{log.json()}')
    
    headers = {'Authorization': log.json()['token_type'].title() + ' ' + log.json()['access_token'],
               'accept' : 'application/json'}
    return headers


def main():
    post_headers={'Content-Type': 'application/json'}

    ip = input('Ingrese la ip del servidor: \n')
    puerto = input('\nIngrese el puerto al que accede: \n')
    link = f'http://{ip}:{puerto}'

    headers = usuario()

    sesion = requests.Session()
    sesion.headers.update(headers)


if __name__ == "__main__":
    main()