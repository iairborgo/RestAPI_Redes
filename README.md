# Proyecto de Redes de Datos: Rest API Cliente y Servidor

## Descripción General

El objetivo de este trabajo práctico es desarrollar un servidor y un cliente Rest API, trabajando con FastAPI principalmente.

Se utilizó una base de datos de los 100 mejores libros de ficción de la historia
El dispositivo encargado de funcionar como servidor tiene bases de datos guardadas en archivos json, junto a distintos métodos para modificarlas.
Por la parte de cliente, se le pide la IP para conectar con el servidor y provee una interfaz fácil de utilizar para que el usuario pueda realizar las request que quiera.

## Estructura del Proyecto

### Servidor (main.py)

El servidor modifica los datos utilizando Pandas y contiene las siguientes funcionalidades:

- Registro y autenticación de usuarios, dandole tokens de acceso JWT. Sus contraseñas son encriptadas con el algoritmo bcrypt
- Almacenamiento de datos en un archivo JSON sobre los libros, la ruta en la que se encuentra las imagenes jpg en el servidor y una carpeta con imágenes
- Endpoints para realizar operaciones CRUD sobre las películas.

### Cliente (cliente.py)

El cliente está implementado utilizando requests y permite interactuar con el servidor a través de una serie de opciones en un menú:
- Al ingresar pide ip de acceso (Podemos pasar este hardcode utilizando una ip en un servidor DNS)
- Consultar libros por título o escritor.
- Consultar la imágen de portada.
- Agregar una nuevo libro.
- Actualizar el link de wikipedia de algún libro existente.
- Eliminar una película.
 
