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
        'password': hash_password('1234'), 'habilitado': True},
        {'id': 2, 'nombre': 'patricio canales',
        'password': hash_password('1234'), 'habilitado': True},
        {'id': 3, 'nombre': 'cristian rojas',
        'password': hash_password('1234'), 'habilitado': True},
        {'id': 4, 'nombre': 'diego carrera',
        'password': hash_password('1234'), 'habilitado': True}]

def crear_etiquetas():
    global etiquetas
    global pk_etiquetas
    etiquetas = [
        {'id': 1, 'categoria_id': 1, 'nombre': 'pronormoblasto',
        'ejemplo': 'pronormoblasto.png', 'descripcion': 'precursor'},
        {'id': 2, 'categoria_id': 1, 'nombre': 'normoblasto basófilo',
        'ejemplo': 'normoblasto_basofilo.png', 'descripcion': 'Precursor'},
        {'id': 3, 'categoria_id': 1, 'nombre': 'normoblasto policromático',
        'ejemplo': 'normoblasto_policromatico.png', 'descripcion': 'Precursor'},
        {'id': 4, 'categoria_id': 1, 'nombre': 'normoblasto ortocromático',
        'ejemplo': 'normoblasto_ortocromatico.png', 'descripcion': 'Precursor'},
        {'id': 5, 'categoria_id': 1, 'nombre': 'eritrocito policromático',
        'ejemplo': 'eritrocito_policromático.png', 'descripcion': 'Periférico'},
        {'id': 6, 'categoria_id': 1, 'nombre': 'eritrocito',
        'ejemplo': 'eritrocito.png', 'descripcion': 'Periférico'},
        {'id': 7, 'categoria_id': 4, 'nombre': 'normocito',
        'ejemplo': 'normocito.png', 'descripcion': 'Variación tamaño: MCV 80-100 fL'},
        {'id': 8, 'categoria_id': 4, 'nombre': 'macrocito',
        'ejemplo': 'macrocito.png', 'descripcion': 'Variación tamaño: MCV > 100fL'},
        {'id': 9, 'categoria_id': 5, 'nombre': 'eritrocito hipocromatico',
        'ejemplo': 'eritrocito_hipocromatico.png', 'descripcion': 'La zona central de palidez del eritrocito debe ser mayor de un tercio de el diámetro de la célula'},
        {'id': 10, 'categoria_id': 5, 'nombre': 'eritrocito dicromatico',
        'ejemplo': 'eritrocito_dicromatico.png', 'descripcion': 'Población de eritrocitos. (Se muestran dos poblaciones de glóbulos rojos: una normocrómica y una hipocrómica).'},
        {'id': 11, 'categoria_id': 6, 'nombre': 'eritrocito normocromatico',
        'ejemplo': 'eritrocito_normocromatico.png', 'descripcion': 'MCHC 32-36 g/dL or 32 %-36 %.'},
        {'id': 12, 'categoria_id': 6, 'nombre': 'acantocito',
        'ejemplo': 'acantocito.png', 'descripcion': 'Variación de forma: Eritrocito con proyecciones espaciadas irregularmente que varían en ancho, largo y número; generalmente denso, sin palidez central'},
        {'id': 13, 'categoria_id': 7, 'nombre': 'esquistocito',
        'ejemplo': 'esquistocito.png', 'descripcion': 'Variación de forma: Eritrocitos fragmentados; puede haber muchos tamaños y formas en un frotis; a menudo muestran extremidades puntiagudas'},
        {'id': 14, 'categoria_id': 7, 'nombre': 'ecinocito',
        'ejemplo': 'ecinocito.png', 'descripcion': 'Variación de forma: Eritrocito con proyecciones cortas, uniformemente espaciadas, generalmente con palidez central'},
        {'id': 15, 'categoria_id': 8, 'nombre': 'esferocito',
        'ejemplo': 'esferocito.png', 'descripcion': 'Variación de color: Más oscuro que RBC normal ;Variación de forma:Redondo; sin zona central de palidez'},
        {'id': 16, 'categoria_id': 8, 'nombre': 'codocito',
        'ejemplo': 'codocito.png', 'descripcion': 'Variación de forma: Ojo de buey; concentración central de hemoglobina rodeada por un área incolora con anillo periférico de hemoglobina que se asemeja al ojo de buey; puede tener forma de campana o copa.'},
        {'id': 17, 'categoria_id': 4, 'nombre': 'drepanocito',
        'ejemplo': 'drepanocito.png', 'descripcion': 'Variación de forma: Celda alargada con punta en cada extremo; puede ser curvo o en forma de S'},
        {'id': 18, 'categoria_id': 4, 'nombre': 'eritrocito policromatico',
        'ejemplo': 'eritrocito_policromatico.png', 'descripcion': 'Precursor'},
        {'id': 19, 'categoria_id': 5, 'nombre': 'microcito',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'}
        ]

def crear_categorias():
    global categorias
    global pk_categorias
    categorias = [
        {'id': 1, 'nombre': 'Eritrocito', 'dependencia_id' : None, 'alteracion' : False,
        'descripcion': 'Glóbulo rojo', 'ejemplo': 'globulo_rojo.png'},
        {'id': 2, 'nombre': 'Leucocito', 'dependencia_id' : None, 'alteracion' : False,
        'descripcion': 'Glóbulo Blanco', 'ejemplo': 'globulo_blanco.png'},
        {'id': 3, 'nombre': 'Plaquetas', 'dependencia_id': None, 'alteracion' : False,
        'descripcion': 'Plaquetas', 'ejemplo': 'plaquetas.png'},
        {'id': 4, 'nombre': 'Color', 'dependencia_id' : 1, 'alteracion' : True,
        'descripcion': 'Deformación de color', 'ejemplo': 'deformacion_color.png'},
        {'id': 5, 'nombre': 'Forma', 'dependencia_id' : 1, 'alteracion' : True,
        'descripcion': 'Deformación de forma', 'ejemplo': 'deformacion_forma.png'},
        {'id': 6, 'nombre': 'Núcleo', 'dependencia_id' : 2, 'alteracion' : True,
        'descripcion': 'Deformación de núcleo', 'ejemplo': 'deformacion_nucleo.png'},
        {'id': 7, 'nombre': 'Citoplasma', 'dependencia_id' : 2, 'alteracion' : True,
        'descripcion': 'Deformación de Citoplasma', 'ejemplo': 'deformacion_citoplasma.png'},
        {'id': 8, 'nombre': 'Tamaño', 'dependencia_id' : 3, 'alteracion' : True,
        'descripcion': 'Deformación de Tamaño', 'ejemplo': 'tamaño.png'}
    ]

def cargar_muestras(path_to_file):
    global usuarios
    global muestras
    global pk_muestra
    global celulas
    global pk_celula

    imagen = cv2.imread(path_to_file)
    name = path_to_file[-12:]
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
    tabla = Table('categoria', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), categorias)
    tabla = Table('celula', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), celulas)
    tabla = Table('etiqueta', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), etiquetas)
    # tabla = Table('respuesta', MetaData(), autoload=True, autoload_with=conexion.engine)
    # conexion.execute(tabla.insert(), respuestas)
    conexion.execute('COMMIT;')
    
    tablas = ('usuario', 'muestra', 'categoria', 'etiqueta')
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
    
    
