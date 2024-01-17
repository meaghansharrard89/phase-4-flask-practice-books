from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Author(db.Model, SerializerMixin):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pen_name = db.Column(db.String)

    # Add relationship

    books = db.relationship(
        "Book", back_populates="author", cascade="all, delete-orphan"
    )
    publishers = association_proxy("books", "publisher")

    # Add serialization rules

    serialize_rules = ("-books.author",)


class Publisher(db.Model, SerializerMixin):
    __tablename__ = "publishers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer, nullable=False)

    # Add relationship

    books = db.relationship(
        "Book", back_populates="publisher", cascade="all, delete-orphan"
    )
    authors = association_proxy("books", "author")

    # Add serialization rules

    serialize_rules = ("-books.publisher",)

    # Add validations

    @validates("founding_year")
    def validate_founding_year(self, key, value):
        if 2023 >= value >= 1600:
            return value
        else:
            raise ValueError("Founding year must be between 1600 and 2023")


class Book(db.Model, SerializerMixin):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    page_count = db.Column(db.Integer, nullable=False)

    # Foreign keys

    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    publisher_id = db.Column(db.Integer, db.ForeignKey("publishers.id"))

    # Add relationship

    author = db.relationship("Author", back_populates="books")
    publisher = db.relationship("Publisher", back_populates="books")

    # Add serialization rules

    serialize_rules = (
        "-author.books",
        "-publisher.books",
    )

    # Add validations

    @validates("page_count")
    def validate_pages(self, key, value):
        if value > 0:
            return value
        else:
            raise ValueError("Page count must be greater than 0")
