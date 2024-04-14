from flask import request, session, jsonify
from flask_restful import Resource

from config import app, db, api
from models import User

class ClearSession(Resource):

    def delete(self):
        session.clear()  # Clear all session data
        return {}, 204

class Signup(Resource):
    
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        
        # Check if username and password are provided
        if not username or not password:
            return {'error': 'Username and password are required'}, 400
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {'error': 'Username already exists'}, 409
        
        # Create a new user
        user = User(username=username)
        user.set_password(password)  # Set password hash
        db.session.add(user)
        db.session.commit()
        
        # Save user ID in session
        session['user_id'] = user.id
        
        return user.to_dict(), 201

class CheckSession(Resource):
    
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {}, 204

class Login(Resource):
    
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    
    def delete(self):
        session.pop('user_id', None)  # Remove user ID from session
        return {}, 204

api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
