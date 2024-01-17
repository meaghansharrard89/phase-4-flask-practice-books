#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Author, Publisher, Book

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
    def get(self, id):
        author = Author.query.filter(Author.id == id).first()
        if author is None:
            return make_response({"error": "Author not found"}, 404)
        return make_response(author.to_dict(), 200)

    def delete(self, id):
        try:
            author = Author.query.filter(Author.id == id).first()
            for book in author.books:
                db.session.delete(book)
            db.session.delete(author)
            db.session.commit()
            return make_response({}, 204)
        except:
            return make_response({"error": "Author not found"}, 404)


api.add_resource(AuthorsById, "/authors/<int:id>")


class Books(Resource):
    def get(self):
        books = Book.query.all()
        books_to_dict = [book.to_dict() for book in books]
        return make_response(jsonify(books_to_dict), 200)

    def post(self):
        try:
            new_book = Book(
                name=request.json["name"],
                page_count=request.json["page_count"],
                author_namer=request.json["author_name"],
                publisher_name=request.json["publisher_name"],
            )
            db.session.add(new_book)
            db.session.commit()
            return (
                new_book.to_dict(only=("id", "name", "page_count", "publisher_name")),
                201,
            )
        except:
            return {"error": "400: Validation error"}, 400


api.add_resource(Books, "/books")


class PublishersById(Resource):
    def get(self, id):
        publisher = Publisher.query.filter(Publisher.id == id).first()
        if publisher is None:
            return make_response({"error": "Publisher not found"}, 404)
        return make_response(publisher.to_dict(), 200)


api.add_resource(PublishersById, "/publishers/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
