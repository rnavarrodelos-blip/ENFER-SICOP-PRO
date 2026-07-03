from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import Base


def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente.")


def get_session():
    """Retorna una nueva sesión de base de datos"""
    Session = sessionmaker(bind=engine)
    return Session()
