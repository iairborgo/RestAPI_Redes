from fastapi import FastAPI, status, Response
import pandas as pd
import re
from PIL import Image
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

# Iniciamos fastapi y cargamos el json de los datos
app = FastAPI()

dbooks = pd.read_json('books.json')
books_images = pd.read_json('booksimagepath.json')

# Use este regex para eliminar \n que aparecian al final de los links
# dbooks['link'] = dbooks['link'].str.replace('\\n', '', regex=True)

# Separo la columna que contiene los link de donde tengo guardada la imagen
#books_images = dbooks[['title','imageLink']].copy()
#books_images.to_json('booksimagepath.json')
#dbooks.drop(columns='imageLink', inplace=True)
#dbooks.to_json('books.json')

@app.get('/diccionario-autores')
def diccionario_autores():
    # Retorna los autores ordenados alfabeticamente
    return(sorted(dbooks['author'].unique()))

@app.get('/diccionario-libros')
def diccionario_autores():
    # Retorna los títulos de los libros ordenados alfabeticamente
    return(sorted(dbooks['title'].unique()))

@app.get('/busqueda-autor/{autor}')
def busqueda_autor(autor : str, response : Response):
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
    
@app.get('/busqueda-libro/{libro}')
def busqueda_autor(libro : str, response : Response):
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

@app.get('/busqueda-imagen/{titulo}')
def busqueda_imagen(titulo : str, response : Response):

    # Dado un título, devuelve la imagen 
    path = books_images[books_images['title'] ==  titulo ]['imageLink']
    if path.empty :
        response.status_code = status.HTTP_404_NOT_FOUND
        return('No existe imagen en la base de datos')
    file = open(path.values[0], mode="rb")
    return StreamingResponse(file, media_type="image/png")

@app.put('/actualizar-link/{libro}', status_code=status.HTTP_202_ACCEPTED) 
def actualizar_link(libro : str, path : str, response : Response, idioma : str = 'es'):
    # Dado un título, idioma del link (ej: ingles = en) y el subdirectorio, actualiza la lista
    libro = re.sub('%20', ' ', libro)
    libro = re.sub('_', ' ', libro)
    libro = libro.lower()

    if libro not in [x.lower()for x in dbooks['title'].unique()]:
        response.status_code = status.HTTP_404_NOT_FOUND
        return('No encontramos el título en la base de datos')

    link = f'https://{idioma}.wikipedia.org/wiki/{path}'
    dbooks.loc[dbooks['title'].str.lower() == libro  , 'link'] = link

    dbooks.to_json('books.json')

    return(f'Link de {libro.title()} actualizado a: {link}')

class Libro(BaseModel):
    author: Optional[str] = 'Unknown'
    country: str
    imageLink: Optional[str] = None
    language: str
    link: str
    pages: int
    title: str
    year: int

@app.post('/nuevo-libro', status_code=status.HTTP_201_CREATED)
def nuevo_libro(libro : Libro, response : Response):
    try:
        dbooks.loc[len(dbooks)] = [libro.author.title(),
                                libro.country.title(),
                                libro.language.title(),
                                libro.link,
                                libro.pages,
                                libro.title.title(),
                                libro.year
                                ]
	books_images.loc[len(books_images) = [libro.title.title(),libro.imageLink]	

        dbooks.to_json('books.json')
    except:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return('Ha ocurrido un error, intentar de nuevo revisando los parámetros')

    return(f'Se ha insertado {libro.title.title()} a la lista.')

@app.delete("/eliminar-libro, status_code=status.HTTP_202_ACCEPTED)
def eliminar_libro(titulo: str, response : Response):
	dbooks = dbooks.drop(dbooks[dbooks["title"] == titulo])
	books_images =  books_images.drop(dbooks[dbooks["title"] == titulo])
	dbooks.to_json("books.json")
	books_images.to_json("bookimagepath.json")
	return(f"{titulo} ha sido eliminado correctamente de la base de datos")
