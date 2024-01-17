#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import Author, Publisher, Book
from flask_restful import Api, Resource

from models import db  # import your models here!

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.get("/")
def index():
    return "Hello world"


class AuthorsById(Resource):
    def get_authors_by_id(self, id):
        author = Author.query.filter_by(id=id).first()
        if author is None:
            return make_response({"error": "Author not found"}, 404)
        return make_response(author.to_dict(), 200)

    def delete(self, id):
        author = Author.query.filter_by(id=id).first()
        if author:
            db.session.delete(author)
            db.session.commit()
            return make_response({}, 204)
        return make_response({"error": "Author not found"}, 404)


api.add_resource(AuthorsById, "/authors/<int:id>")


class Books(Resource):
    def get_books(self):
        books = [book.to_dict() for book in Book.query.all()]
        return make_response(books, 200)

    def post(self):
        data = request.get_json()
        new_book = Book()
        author = Author.query.get(data.get("author_id"))
        publisher = Publisher.query.get(data.get("publisher_id"))
        if not author or not publisher:
            return make_response({"errors": ["validation errors"]}, 400)
        try:
            new_book.title = data.get("title")
            new_book.page_count = data.get("page_count")
            new_book.author_id = data.get("author_id")
            new_book.publisher_id = data.get("publisher_id")
            db.session.add(new_book)
            db.session.commit()
            return make_response(new_book.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Books, "/books")


class PublishersById(Resource):
    def get_publishers_by_id(self, id):
        publisher = Publisher.query.filter_by(id=id).first()
        if publisher is None:
            return make_response({"error": "Publisher not found"}, 404)
        return make_response(
            publisher.to_dict(
                only=(
                    "id",
                    "name",
                    "founding_year",
                    "authors",
                )
            ),
            200,
        )


api.add_resource(PublishersById, "/publishers/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
