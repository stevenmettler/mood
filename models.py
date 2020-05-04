from mood import db, ma
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