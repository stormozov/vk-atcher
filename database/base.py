import os
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine, ForeignKey, text


load_dotenv()
DSN = os.getenv('DSN')

Base = declarative_base()

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
    photo_id_1 = sq.Column(sq.String)
    photo_id_2 = sq.Column(sq.String)
    photo_id_3 = sq.Column(sq.String)

    user = relationship("Users", back_populates="matches")


class Favorites(Base):
    __tablename__ = "favorites"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    favorite_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)

    user = relationship("Users", back_populates="favorites")


class BlackList(Base):
    __tablename__ = "blacklist"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    blocked_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)

    user = relationship("Users", back_populates="blacklist")



def create_tables() -> None:
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы")


if __name__ == "__main__":
    create_tables()
#
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
