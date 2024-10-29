import sqlalchemy

from .db_session import SqlAlchemyBase


class TextOfBook(SqlAlchemyBase):
    __tablename__ = "text_of_book"

    book_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
