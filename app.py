from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        """
        Обработка GET-запроса на:
            - http://127.0.0.1:5000/movies/ - выводит список всех фильмов
            - http://127.0.0.1:5000/movies/?director_id=2 - выводит список фильмов с указанным режиссёром
            - http://127.0.0.1:5000/movies/?genre_id=2 - выводит список фильмов с указанным жанром
            - http://127.0.0.1:5000/movies/?director_id=2&genre_id=4 - выводит список фильмов с указанными режиссёром и
                жанром
        """
        #TODO Вопрос: обязательно ли использовать сериализацию для обработки запроса? Мне не удалось найти способ
        # вывести данные в строгом порядке (id, title, description.....) порядок постоянно меняется. Единственное
        # решение к которому я пришёл, это - формирование списка с помощью создания словаря (пример закомментирован),
        # но для этого нет необходимости использовать сериализацию.
        # .
        # Также формирование списка словарей позволяет
        # выводить значения имени из таблиц "director" и "genre", что невозможно при сериализации (я не нашёл способ).
        # .
        # Помимо этого, мне не удаётся найти решение вывода ASCII в браузере. Т.е. в случае когда "return" возвращает
        # только информацию, отображение происходит корректно. Когда же добавляется машинный код (например 200), то
        # настройки для языка перестают работать. Все мозги сломал.
        # .
        # В этом блоке использовал для request if/else. Полагаю для CBV есть более удобные инструменты. Прошу
        # подсказать способ более оптимального решения.

        movies = movies_schema.dump(Movie.query.all())
        # movies = Movie.query.all()
        # result = []
        # for movie in movies:
        #     dict = {
        #         'id': movie.id,
        #         'title': movie.title,
        #         'description': movie.description,
        #         'trailer': movie.trailer,
        #         'year': movie.year,
        #         'rating': movie.rating,
        #         'genre_id': Genre.query.get(movie.genre_id).name,
        #         'director_id': Director.query.get(movie.director_id).name
        #         }
        #     result.append(dict)
        # return result, 200
        print()
        # result = []
        # for movie in movies:
        #     dict = {
        #         'id': movie['id'],
        #         'title': movie['title'],
        #         'description': movie['description'],
        #         'trailer': movie['trailer'],
        #         'year': movie['year'],
        #         'rating': movie['rating'],
        #         'genre_id': movie['genre_id'],
        #         'director_id': movie['director_id']
        #         }
        #     result.append(dict)

        dir_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')

        if dir_id or genre_id:
            result = []
            for movie in movies:
                if dir_id and genre_id:
                    if dir_id == str(movie['director_id']) and genre_id == str(movie['genre_id']):
                        result.append(movie)
                elif dir_id:
                    if dir_id == str(movie['director_id']):
                        result.append(movie)
                elif genre_id:
                    if genre_id == str(movie['genre_id']):
                        result.append(movie)
            if len(result) == 0:
                return f'director_if - {dir_id}, and genre_id - {genre_id} not found', 404
            return result, 200

        return movies, 200


@movie_ns.route('/<int:mid>')
class MoviesView(Resource):
    def get(self, mid):
        """
        Обработка GET-запроса на адрес http://127.0.0.1:5000/movies/1 - выводит данные о фильме с указанным id.
        """
        movie = movie_schema.dump(Movie.query.get(mid))
        # result = {
        #     'id': movie['id'],
        #     'title': movie['title'],
        #     'description': movie['description'],
        #     'trailer': movie['trailer'],
        #     'year': movie['year'],
        #     'rating': movie['rating'],
        #     'genre_id': movie['genre_id'],
        #     'director_id': movie['director_id']
        # }
        return movie, 200


@director_ns.route('/')
class DirectorsView(Resource):
    def post(self):
        """
        Обработка POST-запроса на адрес http://127.0.0.1:5000/directors/ - добавляет запись в таблицу director.
        """
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return '', 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def put(self, did):
        """
        Обработка PUT-запроса на адрес http://127.0.0.1:5000/directors/1 - обновляет запись с указанным id
        в таблице director.
        """
        req_json = request.json
        director = Director.query.get(did)
        director.name = req_json["name"]
        db.session.add(director)
        db.session.commit()
        db.session.close()
        return '', 201

    def delete(self, did):
        """
        Обработка DELETE-запроса на адрес http://127.0.0.1:5000/directors/1 - удаляет запись с указанным id
        в таблице director.
        """
        director = Director.query.get(did)
        db.session.delete(director)
        db.session.commit()
        db.session.close()
        return '', 204


@genre_ns.route('/')
class GenresView(Resource):
    def post(self):
        """
        Обработка POST-запроса на адрес http://127.0.0.1:5000/genres/ - добавляет запись в таблицу genre.
        """
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return '', 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def put(self, gid):
        """
        Обработка PUT-запроса на адрес http://127.0.0.1:5000/genres/1 - обновляет запись с указанным id
        в таблице genre.
        """
        req_json = request.json
        genre = Genre.query.get(gid)
        genre.name = req_json["name"]
        db.session.add(genre)
        db.session.commit()
        db.session.close()
        return '', 201

    def delete(self, gid):
        """
        Обработка DELETE-запроса на адрес http://127.0.0.1:5000/genres/1 - удаляет запись с указанным id
        в таблице genre.
        """
        genre = Genre.query.get(gid)
        db.session.delete(genre)
        db.session.commit()
        db.session.close()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
