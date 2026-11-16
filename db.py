# Conexiones a los 3 motores de base de datos
import pymysql
from pymongo import MongoClient
import redis

# 1) MySQL (relacional): usuarios, sitios, paginas, objetivos
def conectar_mysql():
    return pymysql.connect(
        host="localhost", port=3307,
        user="root", password="root123",
        database="analytics",
        cursorclass=pymysql.cursors.DictCursor,  # regresa filas como diccionarios
        autocommit=True,
        charset="utf8mb4",
    )

# 2) MongoDB (NoSQL documental): eventos de los visitantes
cliente_mongo = MongoClient("mongodb://localhost:27018", serverSelectionTimeoutMS=3000)
mongo = cliente_mongo["analytics"]

# 3) Redis (clave-valor): sesiones y contadores en vivo
r = redis.Redis(host="localhost", port=6380, decode_responses=True)
