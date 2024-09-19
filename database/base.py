import os
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine, ForeignKey

# Загрузка переменных окружения из файла .env
load_dotenv()
DSN = os.getenv('DSN')

# Создание базового класса для декларативного стиля
Base = declarative_base()

# Создание двигателя и сессии для работы с базой данных
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)


class Users(Base):
    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    gender = sq.Column(sq.String)
    city = sq.Column(sq.String)

    # Определение отношений
    matches = relationship("Matches",
                           back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorites",
                             back_populates="user", cascade="all, delete-orphan")
    blacklist = relationship("BlackList",
                             back_populates="user", cascade="all, delete-orphan")


class Matches(Base):
    __tablename__ = "matches"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    matched_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)
    photo_url_1 = sq.Column(sq.String)
    photo_url_2 = sq.Column(sq.String)
    photo_url_3 = sq.Column(sq.String)

    # Определение отношений
    user = relationship("Users", back_populates="matches")


class Favorites(Base):
    __tablename__ = "favorites"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    favorite_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)

    # Определение отношений
    user = relationship("Users", back_populates="favorites")


class BlackList(Base):
    __tablename__ = "blacklist"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    blocked_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)

    # Определение отношений
    user = relationship("Users", back_populates="blacklist")


def add_to_blacklist(user_id: int, blocked_vk_id: int, first_name: str, last_name: str, session: Session) -> None:
    existing_blacklist_entry = (
        session.query(BlackList).filter_by(user_id=user_id, blocked_vk_id=blocked_vk_id).first())

    if existing_blacklist_entry:
        return

    new_blacklist_entry = BlackList(
        user_id=user_id,
        blocked_vk_id=blocked_vk_id,
        first_name=first_name,
        last_name=last_name
    )

    session.add(new_blacklist_entry)
    session.commit()
    print(f"Пользователь {first_name} {last_name} добавлен в черный список.")


def create_tables() -> None:
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы")


if __name__ == "__main__":
    create_tables()

# def drop_tables_with_cascade(engine):
#     with engine.connect() as conn:
#         # Начало транзакции
#         trans = conn.begin()
#         try:
#             # Удаление таблиц с каскадом
#             conn.execute(text("DROP TABLE IF EXISTS blacklist CASCADE;"))
#             conn.execute(text("DROP TABLE IF EXISTS favorites CASCADE;"))
#             conn.execute(text("DROP TABLE IF EXISTS matches CASCADE;"))
#             conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
#             conn.execute(text("DROP TABLE IF EXISTS user_words CASCADE;"))
#             conn.execute(text("DROP TABLE IF EXISTS words CASCADE;"))
#             # Подтверждение изменений
#             trans.commit()
#             print("Таблицы удалены.")
#         except Exception as e:
#             # Откат транзакции в случае ошибки
#             trans.rollback()
#             print(f"Ошибка при удалении таблиц: {e}")
#
# def create_tables():
#     drop_tables_with_cascade(engine)
#     # Base.metadata.create_all(engine)
#
# if __name__ == "__main__":
#     create_tables()
