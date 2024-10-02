from sqlalchemy import text
from base import DSN,engine,sessionmaker,Base

def drop_tables_with_cascade(engine):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text("DROP TABLE IF EXISTS blacklist CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS favorites CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS matches CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS user_words CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS words CASCADE;"))
            trans.commit()
            print("Таблицы удалены.")
        except Exception as e:
            # Откат транзакции в случае ошибки
            trans.rollback()
            print(f"Ошибка при удалении таблиц: {e}")

def create_tables():
    drop_tables_with_cascade(engine)
    Base.metadata.create_all(engine)
    print("Таблицы созданы.")

if __name__ == "__main__":
    create_tables()
