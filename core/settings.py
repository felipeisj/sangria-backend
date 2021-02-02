import os


DEBUG = True

DBUSER = "postgres"
DBPASS = "asd31222"
DBNAME = "sangria"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_URI = 'postgresql://{}:{}@localhost:5432/{}'.format(
    DBUSER, DBPASS, DBNAME)