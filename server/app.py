#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User, ArticlesSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [ArticlesSchema().dump(article) for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = ArticlesSchema.dump(article)

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
    def post(self):
        # Step 1: Get the username from the request
        username = request.get_json()['username']
        
        # Step 1: Find the user in the database by username
        user = User.query.filter(User.username == username).first()
        
        # Step 2: Set the session with the user's ID
        session['user_id'] = user.id
        
        # Step 3: Return the user as JSON with 200 status code
        return UserSchema().dump(user), 200


class Logout(Resource):
    def delete(self):
        # Step 2: Remove the user_id from the session
        session['user_id'] = None
        
        # Step 3: Return no data with 204 status code
        return {}, 204


class CheckSession(Resource):
    def get(self):
        # Step 2: Get the user_id from the session
        user_id = session.get('user_id')
        
        # Step 3: Check if user_id exists in session
        if user_id:
            # Find the user by the ID stored in session
            user = User.query.filter(User.id == user_id).first()
            # Return the user as JSON with 200 status code
            return UserSchema().dump(user), 200
        else:
            # Return no data with 401 status code
            return {}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
