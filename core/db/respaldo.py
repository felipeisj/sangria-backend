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
from core.db.separator import separar
from sqlalchemy.engine import create_engine
from sqlalchemy import Table, MetaData

muestras = list()
pk_muestra = 0
celulas = list()
pk_celula = 0
'''
Leer imagen
Crear carpeta celulas


'''
def carga_img():
    connection = conexion_bd('localhost','postgres', 'asd31222', 'sangria')
    img = cv2.imread("50HD0037.JPG")
    for img in glob.glob("./dataset/*.JPG"):
        name = img[-12:]
        #print(name)
        #datetime.date.today
        connection.execute("INSERT INTO muestra(path) values('"+name+"');")
        separa_cells
    connection.execute('COMMIT;')

def separa_cells():
    #connection = conexion_bd('localhost','postgres', 'asd31222', 'sangria')
    k = 0
    print("Hola")
    for img in glob.glob("./generated/M_%d/*.jpg"%k):
        name = img[-12:]
        print(name)
        #connection.execute("INSERT INTO celula(muestra_id, path) values(2, '"+name+"');")
        k += 1
    #connection.execute('COMMIT;')

def conexion_bd(host, user, passwd, db):
    engine = create_engine('postgresql://{}:{}@{}:5432/{}'.format(
        user, passwd, host, db))
    return engine

def vacuum(conexion):
    conexion.execute("VACUUM FULL")

def encontrar_pk(arreglo, key, valor):
    return next((item for item in arreglo if item[key] == valor), False)

if __name__ == "__main__":

    #carga_img()
    separa_cells()
    #crear_usuarios()
    #leer_proyectos("../docs/proyectos_adjudicados_2020.xlsx")
    #fake_data()
    #transacciones(conexion)