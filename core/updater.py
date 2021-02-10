import numpy as np
import flask
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import os
import glob
import json
import hashlib
import datetime
import random
import xlrd
from db.separator import separar
from sqlalchemy.engine import create_engine
from sqlalchemy import Table, MetaData

muestras = list()
pk_muestra = 0

celulas = list()
pk_celula = 0

usuarios = list()
pk_usuario = 0

etiquetas = list()
pk_etiqueta = 0

categorias = list()
pk_categoria = 0


def conexion_bd(host, user, passwd, db):
    engine = create_engine('postgresql://{}:{}@{}:5432/{}'.format(
        user, passwd, host, db))
    return engine


def vacuum(conexion):
    conexion.execute("VACUUM FULL")


def encontrar_pk(arreglo, key, valor):
    return next((item for item in arreglo if item[key] == valor), False)

def hash_password(password):
    STATIC_SALT = u"".join(chr(c) for c in [
        33, 37, 121, 113, 108, 117, 118, 33, 101, 56, 94, 43,
        49, 103, 113, 56, 120, 41, 54, 36, 41, 56, 95, 41, 95])
    return hashlib.sha512(
        (STATIC_SALT + password).encode('utf-8')).hexdigest()

def crear_usuarios():
    global usuarios
    global pk_usuario
    usuarios = [
        {'id': 1, 'nombre': 'felipe salazar',
        'password': hash_password('1234')},
        {'id': 2, 'nombre': 'patricio canales',
        'password': hash_password('1234')},
        {'id': 3, 'nombre': 'cristian rojas',
        'password': hash_password('1234')},
        {'id': 4, 'nombre': 'diego carrera',
        'password': hash_password('1234')},]

def crear_etiquetas():
    global etiquetas
    global pk_etiquetas
    etiquetas = [
        {'id': 1, 'nombre': 'pronormoblasto',
        'ejemplo': '/muestras/pronormoblasto', 'descripcion': 'precursor'},
        {'id': 2, 'nombre': 'normoblasto basófilo',
        'ejemplo': '/muestras/normoblasto basófilo', 'descripcion': 'Precursor'},
        {'id': 3, 'nombre': 'normoblasto policromático',
        'ejemplo': '/muestras/normoblasto ortoromatico', 'descripcion': 'Precursor'},
        {'id': 4, 'nombre': 'eritrocito policromatico',
        'ejemplo': '/muestras/eritrocito policromatico', 'descripcion': 'Precursor'},
        {'id': 5, 'nombre': 'eritrocito',
        'ejemplo': '/muestras/eritrocito', 'descripcion': 'Periférico'},
        {'id': 6, 'nombre': 'microcito',
        'ejemplo': '/muestras/microcito', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 7, 'nombre': 'normocito',
        'ejemplo': '/muestras/normocito', 'descripcion': 'Variación tamaño: MCV 80-100 fL'},
        {'id': 8, 'nombre': 'macrocito',
        'ejemplo': '/muestras/macrocito', 'descripcion': 'Variación tamaño: MCV > 100fL'},
        {'id': 9, 'nombre': 'eritrocito hipocromatico',
        'ejemplo': '/muestras/eritrocito hipocromatico', 'descripcion': 'La zona central de palidez del eritrocito debe ser mayor de un tercio de el diámetro de la célula'},
        {'id': 10, 'nombre': 'eritrocito dicromatico',
        'ejemplo': '/muestras/eritrocito dicromatico', 'descripcion': 'Población de eritrocitos. (Se muestran dos poblaciones de glóbulos rojos: una normocrómica y una hipocrómica).'},
        {'id': 11, 'nombre': 'eritrocito policromatico',
        'ejemplo': '/muestras/eritrocito policromatico', 'descripcion': 'RNA retenido en glóbulos rojos'},
        {'id': 12, 'nombre': 'eritrocito normocromatico',
        'ejemplo': '/muestras/eritrocito normocromatico', 'descripcion': 'MCHC 32-36 g/dL or 32 %-36 %.'},
        {'id': 13, 'nombre': 'acantocito',
        'ejemplo': '/muestras/acantocito', 'descripcion': 'Variación de forma: Eritrocito con proyecciones espaciadas irregularmente que varían en ancho, largo y número; generalmente denso, sin palidez central'},
        {'id': 14, 'nombre': 'esquistocito',
        'ejemplo': '/muestras/esquistocito', 'descripcion': 'Variación de forma: Eritrocitos fragmentados; puede haber muchos tamaños y formas en un frotis; a menudo muestran extremidades puntiagudas'},
        {'id': 15, 'nombre': 'ecinocito',
        'ejemplo': '/muestras/ecinocito', 'descripcion': 'Variación de forma: Eritrocito con proyecciones cortas, uniformemente espaciadas, generalmente con palidez central'},
        {'id': 16, 'nombre': 'esferocito',
        'ejemplo': '/muestras/esferocito', 'descripcion': 'Variación de color: Más oscuro que RBC normal ;Variación de forma:Redondo; sin zona central de palidez'},
        {'id': 17, 'nombre': 'codocito',
        'ejemplo': '/muestras/codocito', 'descripcion': 'Variación de forma: Ojo de buey; concentración central de hemoglobina rodeada por un área incolora con anillo periférico de hemoglobina que se asemeja al ojo de buey; puede tener forma de campana o copa.'},
        {'id': 18, 'nombre': 'drepanocito',
        'ejemplo': '/muestras/drepanocito', 'descripcion': 'Variación de forma: Celda alargada con punta en cada extremo; puede ser curvo o en forma de S'},]

def crear_categorias():
    global categorias
    global pk_categorias
    categorias = [
        {'id': 1, 'nombre': 'megacariocito',
        'descripcion': 'Progenitor RBC', 'ejemplo': '/muestras/megacariocito'},
    ]

def cargar_muestras(path_to_file):
    global usuarios
    global muestras
    global pk_muestra
    global celulas
    global pk_celula

    imagen = cv2.imread(path_to_file)
    name = path_to_file[-12:]
    print(name)
    # muestras
    print(name)
    if not any(f['path'] == name for f in muestras):
        pk_muestra += 1
        usuario = random.choice(usuarios)
        muestras.append({
            'id': pk_muestra,
            'path': name,
            'usuario_id': usuario['id']
        })
    return pk_muestra

   
    
def separa_cells(url, id_muestra):
    global usuarios
    global muestras
    global pk_muestra
    global celulas
    global pk_celula
    #muestra = encontrar_pk(muestras, 'id', 1)
    ruta = url[-12:]
    nombre_celulas = separar(url)
    for nombre_celula in nombre_celulas:
        if not any(f['path'] == nombre_celula for f in celulas):
            pk_celula += 1
            print(pk_celula)
            nombre_celula = nombre_celula[24:]
            celulas.append({
                'id': pk_celula,
                'nombre': nombre_celula,
                'path': ruta,
                'muestra_id': id_muestra
            })




def transacciones(conexion):
    global usuarios
    global muestras
    global etiquetas
    global categorias


    tabla = Table('usuario', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), usuarios)
    tabla = Table('muestra', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), muestras)
    tabla = Table('celula', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), celulas)
    tabla = Table('etiqueta', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), etiquetas)
    tabla = Table('categoria', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), categorias)



    conexion.execute('COMMIT;')
    
    tablas = ('usuario', 'muestra', 'etiqueta', 'categoria')
    for t in tablas:
        conexion.execute(
            "SELECT setval('{0}_id_seq', COALESCE((SELECT MAX(id)+1 FROM {0}), 1), true);".format(t))
    conexion.execute('COMMIT;')


if __name__ == "__main__":

    conexion = conexion_bd('localhost','postgres', 'asd31222', 'sangria')
    ruta = "./dataset/50HD0037.JPG"
    crear_usuarios()
    muestra_id = cargar_muestras(ruta)
    separa_cells(ruta, muestra_id)
    crear_etiquetas()
    crear_categorias()
    transacciones(conexion)
    
    
