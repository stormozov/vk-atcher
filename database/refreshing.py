from sqlalchemy import text

from base import Base, engine


def drop_tables_with_cascade(engine) -> None:
    """Удаляет таблицы из базы данных с помощью CASCADE."""
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
            print("Таблицы удалены.")  # Вывод отладочной информации
        except Exception as e:
            trans.rollback()  # Откат транзакции в случае ошибки
            print(f"Ошибка при удалении таблиц: {e}")  # Вывод отладочной инфо


def create_tables() -> None:
    """Создает таблицы в базе данных."""
    drop_tables_with_cascade(engine)  # Удаление таблиц с помощью CASCADE
    Base.metadata.create_all(engine)  # Создание таблиц в базе данных
    print("Таблицы созданы.")  # Вывод отладочной информации


if __name__ == "__main__":
    create_tables()
