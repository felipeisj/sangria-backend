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


def cargar_muestras(path_to_file):
    global usuarios
    global muestras
    global pk_muestra
    global celulas
    global pk_celula

    imagen = cv2.imread(path_to_file)
    name = path_to_file[-12:]
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
            celulas.append({
                'id': pk_celula,
                'path': ruta,
                'muestra_id': id_muestra
            })




def transacciones(conexion):
    global usuarios
    global muestras


    tabla = Table('usuario', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), usuarios)
    tabla = Table('muestra', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), muestras)
    tabla = Table('celula', MetaData(), autoload=True, autoload_with=conexion.engine)
    conexion.execute(tabla.insert(), celulas)
    #tabla = Table('etiqueta', MetaData(), autoload=True, autoload_with=conexion.engine)
    #conexion.execute(tabla.insert(), etiquetas)



    conexion.execute('COMMIT;')
    
    tablas = ('usuario', 'muestra')
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
    transacciones(conexion)
    
    
