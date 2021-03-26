# README #

### Objetivo de sangria ###

Algoritmo que analiza imágenes de muestras de sangre e identifica la cantidad de glóbulos rojos, los separa para procesarlos de forma unitaria, define si cada glóbulo rojo es normal, esquistocito o esferocitos (deformes) y entrega el número total de estos indicadores en la muestra, además de indicar los casos en que el algoritmo no fue capaz de determinar un resultado.
* Version: 0.0.1
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### Configuración del entorno de desarrollo ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact

crrojasperez@gmail.com

### Instalación

* Clonar proyecto desde git.
* Crear entorno virtual en python siguiente las instrucciones del sitio oficial: **https://pypi.org/project/virtualenv/**
* Acceder al entorno virtual dentro del proyecto.
* Versiones a tomar en cuenta: Python 3.6.9, versíon de librería PyJWT==1.7.1 (en caso de que no sea ésta, ejecutar **pip install PyJWT==1.7.1**)
* Ejecutar comando en consola **pip install -r requirements.txt**
* Descargar imágenes y descomprimir en carpeta **core**.
* Crear base de datos llamada **sangria**.
* Ejecutar **entry.py** en carpeta raíz para crear tablas y bajar servidor.
* Ejecutar **carga_tablas.py** en carpeta **/core**.
* Volver a ejecutar **entry.py** en carpeta raíz para poner el servidor a funcionar.