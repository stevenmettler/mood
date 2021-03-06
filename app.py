from flask import Flask, request, jsonify, url_for, g, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from datetime import date, timedelta
from functools import wraps
from scipy import stats
import os

#init
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'thisissecret'

#DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Init DB
db = SQLAlchemy(app)

#Init marshmallow
ma = Marshmallow(app)

#Class/Model
class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feeling = db.Column(db.String(64))
    user_id = db.Column(db.String(50))
    timestamp = db.Column(db.String(80))

    def __init__(self, feeling, user_id, timestamp):
        self.feeling = feeling
        self.user_id = user_id
        self.timestamp = timestamp

class User(db.Model):
    __tablename__= 'users'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    current_streak = db.Column(db.Integer)
    max_streak = db.Column(db.Integer)

    
    def __init__(self, public_id, name, password, admin, current_streak, max_streak):
        self.name = name
        self.password = password
        self.admin = admin
        self.public_id = public_id
        self.current_streak = current_streak
        self.max_streak = max_streak
    

#Schema
class MoodSchema(ma.Schema):
    class Meta:
        fields = ('id', 'feeling', 'timestamp')

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'public_id', 'name', 'password', 'admin', 'current_streak', 'max_streak')

#Init Schema
mood_schema = MoodSchema(strict=True)
moods_schema = MoodSchema(many=True, strict=True)
user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated



#create a mood
@app.route('/mood', methods=['POST', 'GET'])
@token_required
def add_mood(current_user):
    moods = Mood.query.filter_by(user_id = current_user.public_id)
    user = User.query.filter_by(public_id = current_user.public_id).first()
    all_names = User.query.all()

    streaks = []
    for name in all_names:
        streaks.append(name.max_streak)
    
    percentile = stats.percentileofscore(streaks, user.max_streak)

    output = []
    for mood in moods:
        mood_data = {}
        mood_data['feeling'] = mood.feeling
        mood_data['current_streak'] = user.current_streak
        if percentile >= 50.0:
            mood_data['streak_percentile'] = percentile
        output.append(mood_data)

    if request.method == 'POST':
        feeling = request.json['feeling']
        timestamp = datetime.datetime.utcnow()
        # timestamp = datetime.datetime(2020, 5, 4, 10, 10, 10, 123456)
        new_mood = Mood(feeling, current_user.public_id, timestamp)
        
        #base case, first submitted mood
        if len(output)== 0:
            user.current_streak = 1
            user.max_streak = 1
        else:
            last = moods.order_by(Mood.timestamp.desc()).first()
            last_time = datetime.datetime.strptime(last.timestamp, '%Y-%m-%d %H:%M:%S.%f')
            if (timestamp.date() - last_time.date()).days == 1:
                user.current_streak = user.current_streak + 1
                user.max_streak = max(user.max_streak, user.current_streak)
            elif (timestamp.date() - last_time.date()).days == 0:
                user.max_streak = max(user.max_streak, user.current_streak)
            else:
                user.max_streak = max(user.max_streak, user.current_streak)
                user.current_streak = 1

        
        db.session.add(new_mood)
        db.session.commit()

        return mood_schema.jsonify(new_mood)
    elif request.method == 'GET':

        return jsonify({'moods': output})

#get all users
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        user_data['current_streak'] = user.current_streak
        user_data['max_streak'] = user.max_streak
        output.append(user_data)

    return jsonify({'users': output})

#get a single user
@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    user = User.query.filter_by(public_id = public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    user_data['current_streak'] = user.current_streak
    user_data['max_streak'] = user.max_streak

    return jsonify({'user': user_data})

#create a new user
@app.route('/user', methods=['POST'])
# @token_required
# def create_user(current_user):
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), name = data['name'], password = hashed_password, admin = False, current_streak = 0, max_streak = 0)
    db.session.add(new_user)
    db.session.commit()


    return jsonify({'message': 'New user created!'})

#promote a user
@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})
    
    user.admin = True
    db.session.commit()

    return jsonify({'message': 'The user has been promoted!'})

#delete a user
@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted.'})


#login to server
@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
    
    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})
    
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
        



#run server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
