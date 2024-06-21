from fastapi import FastAPI, status, Response, Depends
import pandas as pd
import re
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Union
import modelos
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
# Iniciamos fastapi y cargamos el json de los datos
app = FastAPI()

#users = pd.DataFrame(columns = ['User', 'Password'])
#users.to_json('users.json')
# Use este regex para eliminar \n que aparecian al final de los links
# dbooks['link'] = dbooks['link'].str.replace('\\n', '', regex=True)

# Separo la columna que contiene los link de donde tengo guardada la imagen
#books_images = dbooks[['title','imageLink']].copy()
#books_images.to_json('booksimagepath.json')
#dbooks.drop(columns='imageLink', inplace=True)
#dbooks.to_json('books.json')

@app.post('/nuevo-usuario', status_code=status.HTTP_201_CREATED, tags = ['Autenticacion'])
def nuevo_usuario(usuario : modelos.Usuario, response : Response):
    dbooks, books_images, users = modelos.load_data()

    if usuario.user in users['User'].unique(): # Checkea si existe en la ''''base de datos'''''
        response.status_code = status.HTTP_409_CONFLICT
        return('Nombre de usuario en uso')
    
    users.loc[len(users)] = [usuario.user, modelos.Hash.bcrypt(usuario.password)] # Bcrypt es una funcion hash 
    users.to_json('users.json')

    return(f'Usuario {usuario.user} creado')

@app.post('/login', tags = ['Autenticacion'])
def login(response : Response, log_credential: OAuth2PasswordRequestForm = Depends()):
    dbooks, books_images, users = modelos.load_data()
    user_found = users[users['User'] == log_credential.username]
    
    if user_found.empty:
        response.status_code = status.HTTP_404_NOT_FOUND
        return('Usuario o contraseña incorrecta')
    
    hashedpass = user_found['Password'].values[0]
    if not modelos.Hash.autenticar(log_credential.password, hashedpass): # checkea si la contraseña dada coincide con la encriptada
        response.status_code = status.HTTP_404_NOT_FOUND
        return('Usuario o contraseña incorrecta')
    
    access_token = modelos.create_access_token(data={"sub": log_credential.username}, expires_delta = None)
    return modelos.Token(access_token=access_token, token_type="bearer")
    

@app.get('/diccionario-autores', tags = ['Lista'])
def diccionario_autores(current_user : modelos.Usuario = Depends(modelos.get_current_user)):
    dbooks, books_images, users = modelos.load_data()
    # Retorna los autores ordenados alfabeticamente
    return(sorted(dbooks['author'].unique()))

@app.get('/diccionario-libros', tags = ['Lista'])
def diccionario_autores(current_user : modelos.Usuario = Depends(modelos.get_current_user)):
    dbooks, books_images, users = modelos.load_data()
    # Retorna los títulos de los libros ordenados alfabeticamente
    return(sorted(dbooks['title'].unique()))

@app.get('/busqueda-autor/{autor}', tags = ['Busqueda'])
def busqueda_autor(autor : str, response : Response,
                   current_user : modelos.Usuario = Depends(modelos.get_current_user)):
    dbooks, books_images, users = modelos.load_data()
    # Dado un autor (no es case sensitive y se puede separar nombre con espacios o _) devuelve todos los libros suyos
    autor = re.sub('%20', ' ', autor)
    autor = re.sub('_', ' ', autor)
    autor = autor.lower()
    
    query = dbooks[dbooks['author'].str.lower() == autor]
    if query.empty :
        response.status_code = status.HTTP_404_NOT_FOUND
        return('Autor no encontrado, podes ver una lista ordenada en /diccionario-autores')
    else:       
        return query.to_dict(orient="records")
    
@app.get('/busqueda-libro/{libro}', tags = ['Busqueda'])
def busqueda_libro(libro : str, response : Response,
                   current_user : modelos.Usuario = Depends(modelos.get_current_user)):
    dbooks, books_images, users = modelos.load_data()
    # Dado un titulo, devuelve los datos de este. No es case-sensitive y se puede separar con espacios o _
    libro = re.sub('%20', ' ', libro)
    libro = re.sub('_', ' ', libro)
    libro = libro.lower()
    
    query = dbooks[dbooks['title'].str.lower() == libro]
    if query.empty :
        response.status_code = status.HTTP_404_NOT_FOUND
        return('Libro no encontrado, podes ver una lista ordenada en /diccionario-libros')
    else:      
        return query.to_dict(orient="records")

@app.get('/busqueda-imagen/{titulo}', tags = ['Busqueda'])
def busqueda_imagen(titulo : str, response : Response,
                    current_user : modelos.Usuario = Depends(modelos.get_current_user)):
    dbooks, books_images, users = modelos.load_data()
    # Dado un título, devuelve la imagen 
    path = books_images[books_images['title'] ==  titulo.title() ]['imageLink']
    if path.empty :
        response.status_code = status.HTTP_404_NOT_FOUND
        return('No existe imagen en la base de datos')
    file = open(path.values[0], mode="rb")
    return StreamingResponse(file, media_type="image/png")

@app.put('/actualizar-link/{libro}', status_code=status.HTTP_202_ACCEPTED, tags = ['Modificacion de Datos']) 
def actualizar_link(libro : str, path : str, response : Response, idioma : str = 'es',
                    current_user : modelos.Usuario = Depends(modelos.get_current_user)):
    dbooks, books_images, users = modelos.load_data()
    # Dado un título, idioma del link (ej: ingles = en) y el subdirectorio, actualiza la lista
    libro = re.sub('%20', ' ', libro)
    libro = re.sub('_', ' ', libro)
    libro = libro.lower()

    if libro not in [x.lower() for x in dbooks['title'].unique()]:
        response.status_code = status.HTTP_404_NOT_FOUND
        return('No encontramos el título en la base de datos')

    link = f'https://{idioma}.wikipedia.org/wiki/{path}'
    dbooks.loc[dbooks['title'].str.lower() == libro  , 'link'] = link

    dbooks.to_json('books.json')

    return(f'Link de {libro.title()} actualizado a: {link}')


@app.delete("/eliminar-libro", status_code=status.HTTP_202_ACCEPTED, tags = ['Modificacion de Datos'])
def eliminar_libro(libro: str, response : Response,
                   current_user : modelos.Usuario = Depends(modelos.get_current_user)):
    dbooks, books_images, users = modelos.load_data()
    libro = re.sub('%20', ' ', libro)
    libro = re.sub('_', ' ', libro)
    libro = libro.lower()
    query = dbooks[dbooks['title'].str.lower() == libro].index
    if query.empty:
        response.status_code = status.HTTP_404_NOT_FOUND
        return('No se ha encontrado el libro en la base de datos')
    
    dbooks = dbooks.drop(index = query)
    books_images =  books_images.drop(index = books_images[books_images["title"].str.lower() == libro].index)
    dbooks.to_json("books.json")
    books_images.to_json("booksimagepath.json")
    return(f"{libro.title()} ha sido eliminado correctamente de la base de datos")



@app.post('/nuevo-libro', status_code=status.HTTP_201_CREATED,tags = ['Modificacion de Datos'])
def nuevo_libro(libro : modelos.Libro, response : Response,
                current_user : modelos.Usuario = Depends(modelos.get_current_user)):
    
    dbooks, books_images, users = modelos.load_data()

    if libro.title.title() not in dbooks['title'].unique():
        dbooks.loc[len(dbooks)] = [libro.author.title(),
                                libro.country.title(),
                                libro.language.title(),
                                libro.link,
                                libro.pages,
                                libro.title.title(),
                                libro.year
                                ]
        books_images.loc[len(books_images)] = [libro.title.title(),libro.imageLink]	
        books_images.to_json('bookimagepath.json')
        dbooks.to_json('books.json')
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return('El título se encuentra en la base de datos.')

    return(f'Se ha insertado {libro.title.title()} a la lista.')