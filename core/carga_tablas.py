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
        'password': hash_password('1234'), 'habilitado': True, 'academico': True},
        {'id': 2, 'nombre': 'patricio canales',
        'password': hash_password('1234'), 'habilitado': True, 'academico': False},
        {'id': 3, 'nombre': 'cristian rojas',
        'password': hash_password('1234'), 'habilitado': True, 'academico': False},
        {'id': 4, 'nombre': 'diego carrera',
        'password': hash_password('1234'), 'habilitado': True, 'academico': False}]

def crear_etiquetas():
    global etiquetas
    global pk_etiquetas
    etiquetas = [
        # línea eritrocito
        {'id': 1, 'categoria_id': 1, 'nombre': 'Pronormoblasto',
        'ejemplo': 'pronormoblasto.png', 'descripcion': 'precursor'},
        {'id': 2, 'categoria_id': 1, 'nombre': 'Normoblasto basófilo',
        'ejemplo': 'normoblasto_basofilo.png', 'descripcion': 'Precursor'},
        {'id': 3, 'categoria_id': 1, 'nombre': 'Normoblasto policromático',
        'ejemplo': 'normoblasto_policromatico.png', 'descripcion': 'Precursor'},
        {'id': 4, 'categoria_id': 1, 'nombre': 'Normoblasto ortocromático',
        'ejemplo': 'normoblasto_ortocromatico.png', 'descripcion': 'Precursor'},
        {'id': 5, 'categoria_id': 1, 'nombre': 'Eritrocito policromático',
        'ejemplo': 'eritrocito_policromatico.png', 'descripcion': 'Periférico'},
        {'id': 6, 'categoria_id': 1, 'nombre': 'Eritrocito',
        'ejemplo': 'eritrocito.png', 'descripcion': 'Periférico'},
        # línea leucocito
        # Mieloblasto y Promielocito: primeros dos precursores granulocitos (neutrofilo eosinofilo y basofilo)
        {'id': 7, 'categoria_id': 9, 'nombre': 'Mieloblasto',
        'ejemplo': 'mieloblasto.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 8, 'categoria_id': 9, 'nombre': 'Promielocito',
        'ejemplo': 'promielocito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # Neutrofilo
        {'id': 9, 'categoria_id': 9, 'nombre': 'Mielocito Neutrófilo',
        'ejemplo': 'mielocito_neutrofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 10, 'categoria_id': 9, 'nombre': 'MetaMielocito Neutrófilo',
        'ejemplo': 'meta-mielocito_neutrofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 11, 'categoria_id': 9, 'nombre': 'Banda Neutrófilo',
        'ejemplo': 'banda_neutrofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 12, 'categoria_id': 9, 'nombre': 'Neutrófilo Segmentado',
        'ejemplo': 'neutrofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # Eosinófilo
        {'id': 13, 'categoria_id': 10, 'nombre': 'Mielocito Eosinofílico',
        'ejemplo': 'mielocito_eosinofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 14, 'categoria_id': 10, 'nombre': 'Metamielocito Eosinofílico',
        'ejemplo': 'meta-mielocito_eosinofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 15, 'categoria_id': 10, 'nombre': 'Banda Eosinofílico',
        'ejemplo': 'banda_eosinofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 16, 'categoria_id': 10, 'nombre': 'Eosinófilo',
        'ejemplo': 'eosinofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # Basófilo #metamielocito y banda igual a neutrofilo
        {'id': 17, 'categoria_id': 11, 'nombre': 'Mielocito Basofílico',
        'ejemplo': 'mielocito_basofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 18, 'categoria_id': 11, 'nombre': 'MetaMielocito basofílico',
        'ejemplo': 'meta-mielocito_neutrofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 19, 'categoria_id': 11, 'nombre': 'Banda Basofílico',
        'ejemplo': 'banda_neutrofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 20, 'categoria_id': 11, 'nombre': 'Basófilo',
        'ejemplo': 'basofilo.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # maduración Monocito
        {'id': 21, 'categoria_id': 13, 'nombre': 'Monoblasto',
        'ejemplo': 'monoblasto.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 22, 'categoria_id': 13, 'nombre': 'Promonocito',
        'ejemplo': 'promonocito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 23, 'categoria_id': 13, 'nombre': 'Monocito',
        'ejemplo': 'monocito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 24, 'categoria_id': 13, 'nombre': 'Macrófago',
        'ejemplo': 'macrofago.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # maduración Linfocitos
        {'id': 25, 'categoria_id': 12, 'nombre': 'Linfoide Progenitor Común',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # Linfocitos B
        {'id': 26, 'categoria_id': 12, 'nombre': 'Pre B',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 27, 'categoria_id': 12, 'nombre': 'Linfoblasto B',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 28, 'categoria_id': 12, 'nombre': 'ProLinfocito B',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 29, 'categoria_id': 12, 'nombre': 'Linfocito B',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 30, 'categoria_id': 12, 'nombre': 'Célula Plasmática',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # Linfocitos T
        {'id': 31, 'categoria_id': 12, 'nombre': 'Pre T',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 32, 'categoria_id': 12, 'nombre': 'Linfoblasto T',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 33, 'categoria_id': 12, 'nombre': 'ProLinfocito T',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 34, 'categoria_id': 12, 'nombre': 'Linfocito T',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # línea Plaquetas
        {'id': 35, 'categoria_id': 3, 'nombre': 'Megacarioblasto MK-I',
        'ejemplo': 'megacarioblasto.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 36, 'categoria_id': 3, 'nombre': 'Promegacariocito MK-II',
        'ejemplo': 'promegacariocito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 37, 'categoria_id': 3, 'nombre': 'Megacariocito MK-III',
        'ejemplo': 'megacariocito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 38, 'categoria_id': 3, 'nombre': 'Plaqueta',
        'ejemplo': 'plaqueta.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        ############################################################################33
        ###             Alteraciones 
        ###                Células
        #########################################################################
        ###  Alteraciones eritrocitos   ###
        # Alteración de color
        {'id': 39, 'categoria_id': 4, 'nombre': 'eritrocito hipocromático',
        'ejemplo': 'eritrocito_hipocromatico.png', 'descripcion': 'La zona central de palidez del eritrocito debe ser mayor de un tercio de el diámetro de la célula'},
        {'id': 40, 'categoria_id': 4, 'nombre': 'eritrocito hipercromático',
        'ejemplo': 'eritrocito_hipocromatico.png', 'descripcion': 'Manchados, carecen de palidez interior'},
        # Alteración de tamaño
        {'id': 41, 'categoria_id': 6, 'nombre': 'normocito',
        'ejemplo': 'normocito.png', 'descripcion': 'Variación tamaño: MCV 80-100 fL'},
        {'id': 42, 'categoria_id': 6, 'nombre': 'macrocito',
        'ejemplo': 'macrocito.png', 'descripcion': 'Variación tamaño: MCV > 100fL'},
        {'id': 43, 'categoria_id': 6, 'nombre': 'microcito',
        'ejemplo': 'microcito.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        # Alteración de forma     
        {'id': 44, 'categoria_id': 4, 'nombre': 'acantocito',
        'ejemplo': 'acantocito.png', 'descripcion': 'Variación de forma: Eritrocito con proyecciones espaciadas irregularmente que varían en ancho, largo y número; generalmente denso, sin palidez central'},
        {'id': 45, 'categoria_id': 4, 'nombre': 'esquistocito',
        'ejemplo': 'esquistocito.png', 'descripcion': 'Variación de forma: Eritrocitos fragmentados; puede haber muchos tamaños y formas en un frotis; a menudo muestran extremidades puntiagudas'},
        {'id': 46, 'categoria_id': 4, 'nombre': 'ecinocito',
        'ejemplo': 'ecinocito.png', 'descripcion': 'Variación de forma: Eritrocito con proyecciones cortas, uniformemente espaciadas, generalmente con palidez central'},
        {'id': 47, 'categoria_id': 5, 'nombre': 'esferocito',
        'ejemplo': 'esferocito.png', 'descripcion': 'Variación de color: Más oscuro que RBC normal ;Variación de forma:Redondo; sin zona central de palidez'},
        {'id': 48, 'categoria_id': 5, 'nombre': 'codocito',
        'ejemplo': 'codocito.png', 'descripcion': 'Variación de forma: Ojo de buey; concentración central de hemoglobina rodeada por un área incolora con anillo periférico de hemoglobina que se asemeja al ojo de buey; puede tener forma de campana o copa.'},
        {'id': 49, 'categoria_id': 5, 'nombre': 'drepanocito',
        'ejemplo': 'drepanocito.png', 'descripcion': 'Variación de forma: Celda alargada con punta en cada extremo; puede ser curvo o en forma de S'},
        # Eritrocito normal
        # {'id': 11, 'categoria_id': 4, 'nombre': 'eritrocito normocrómico',
        # 'ejemplo': 'eritrocito_normocromatico.png', 'descripcion': 'MCHC 32-36 g/dL or 32 %-36 %.'},

        # Se presentan ambas alteraciones de color normocromaticos e hipocromáticos
        # {'id': 10, 'categoria_id': 4, 'nombre': 'eritrocito dicromatico',
        # 'ejemplo': 'eritrocito_dicromatico.png', 'descripcion': 'Población de eritrocitos. (Se muestran dos poblaciones de glóbulos rojos: una normocrómica y una hipocrómica).'},

        
        # Alteraciones Leucocitos
        {'id': 50, 'categoria_id': 7, 'nombre': 'Hiposegmentación de Neutrófilos',
        'ejemplo': 'hiposegmentacion_neutrofilos.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 51, 'categoria_id': 7, 'nombre': 'Hipersegmentación de Neutrófilos',
        'ejemplo': 'hipersegmentacion_neutrofilos.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 52, 'categoria_id': 8, 'nombre': 'Vacuolación',
        'ejemplo': 'vacuolacion.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 53, 'categoria_id': 8, 'nombre': 'Cuerpo de Döhle',
        'ejemplo': 'cuerpo_dohle.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 54, 'categoria_id': 7, 'nombre': 'Granulación Tóxica',
        'ejemplo': 'granulacion_toxica.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 55, 'categoria_id': 8, 'nombre': 'Hipogranulación/Agranulación',
        'ejemplo': 'hipogranulacion.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 56, 'categoria_id': 8, 'nombre': 'Linfocitos Reactivos',
        'ejemplo': 'linfocitos_reactivos.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        
        # Alteraciones plaquetas
        {'id': 57, 'categoria_id': 14, 'nombre': 'Plaqueta grande',
        'ejemplo': 'plaqueta_gigante.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},
        {'id': 58, 'categoria_id': 14, 'nombre': 'Plaqueta gigante',
        'ejemplo': 'plaqueta_gigante.png', 'descripcion': 'Variación tamaño: MCV < 80fL'},

        # Irreconocible
        {'id': 59, 'categoria_id': 15, 'nombre': 'Irreconocible',
        'ejemplo': 'irreconocible.jpg', 'descripcion': 'Variación tamaño: MCV < 80fL'},
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
        {'id': 6, 'nombre': 'Tamaño', 'dependencia_id' : 1, 'alteracion' : True,
        'descripcion': 'Deformación de Tamaño', 'ejemplo': 'tamaño.png'},
        {'id': 7, 'nombre': 'Núcleo', 'dependencia_id' : 2, 'alteracion' : True,
        'descripcion': 'Deformación de núcleo', 'ejemplo': 'deformacion_nucleo.png'},
        {'id': 8, 'nombre': 'Citoplasma', 'dependencia_id' : 2, 'alteracion' : True,
        'descripcion': 'Deformación de Citoplasma', 'ejemplo': 'deformacion_citoplasma.png'},
        
        {'id': 9, 'nombre': 'Categoría Neutrófilo', 'dependencia_id' : 2, 'alteracion' : False,
        'descripcion': 'Sub categoría Leucocito', 'ejemplo': 'tamaño.png'},
        {'id': 10, 'nombre': 'Categoría Eosinófilo', 'dependencia_id' : 2, 'alteracion' : False,
        'descripcion': 'Sub categoría Leucocito', 'ejemplo': 'tamaño.png'},
        {'id': 11, 'nombre': 'Categoría Basófilo', 'dependencia_id' : 2, 'alteracion' : False,
        'descripcion': 'Sub categoría Leucocito', 'ejemplo': 'tamaño.png'},
        {'id': 12, 'nombre': 'categoría Linfocito', 'dependencia_id' : 2, 'alteracion' : False,
        'descripcion': 'Sub categoría Leucocito', 'ejemplo': 'tamaño.png'},
        {'id': 13, 'nombre': 'Categoría Monocito', 'dependencia_id' : 2, 'alteracion' : False,
        'descripcion': 'Sub categoría Leucocito', 'ejemplo': 'tamaño.png'},
        {'id': 14, 'nombre': 'Tamaño Plaquetas', 'dependencia_id' : 3, 'alteracion' : True,
        'descripcion': 'Deformación de Citoplasma', 'ejemplo': 'deformacion_citoplasma.png'},
        {'id': 15, 'nombre': 'No reconocible', 'dependencia_id' : None, 'alteracion' : False,
        'descripcion': 'Cèlula no reconocible', 'ejemplo': ''}
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
    crear_usuarios()
    
    for ruta in glob.glob("./dataset/*.JPG"):
        muestra_id = cargar_muestras(ruta)
        separa_cells(ruta, muestra_id)
    
    crear_etiquetas()
    crear_categorias()
    transacciones(conexion)