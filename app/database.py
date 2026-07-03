from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///enfer_sicop.db"

engine = create_engine(
    DATABASE_URL,
    echo=False
)
