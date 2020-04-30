from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

#init
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
basedir = os.path.abspath(os.path.dirname(__file__))

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

    def __init__(self, feeling):
        self.feeling = feeling

#Schema
class MoodSchema(ma.Schema):
    class Meta:
        fields = ('id', 'feeling')

#Init Schema
mood_schema = MoodSchema(strict=True)
moods_schema = MoodSchema(many=True, strict=True)

#create a mood
@app.route('/mood', methods=['POST'])
def add_mood():
    feeling = request.json['feeling']

    new_mood = Mood(feeling)

    db.session.add(new_mood)
    db.session.commit()

    return mood_schema.jsonify(new_mood)

#run server
if __name__ == '__main__':
    app.run(debug=True)
