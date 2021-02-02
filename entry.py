from main import app
from core import settings
from core.db.config import session, engine, Base


def init_db():
    """
    CREATE USER user_sspuach WITH PASSWORD 'sspuach11235813';
    CREATE DATABASE sspuach;
    GRANT ALL PRIVILEGES ON DATABASE sspuach to user_sspuach;
    CREATE EXTENSION unaccent;
    """
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    app.run(debug=settings.DEBUG)