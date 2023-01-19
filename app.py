from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/postgres'
db = SQLAlchemy(app)



class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(), nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    username = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



@app.route('/', methods=['GET'])
def index():
    return '''
        <h3>GET <a href="/messages">/messages</a></h3>
        <h3>POST /messages {message : string}</h3>
        <h3>POST /messages/id/like {username : string}</h3>
        <h3>DELETE /messages/id/dislike {username : string}</h3>
        <h3>GET /messages/id </h3>
    ''', 200


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    message = Messages(message=data['message'])
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Successfully created a new message'}), 201

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Messages.query.order_by(Messages.created_at.desc()).all()
    return jsonify([{
        "id" : message.id,
        "message" : message.message,
        "likes" : message.likes_count
    } for message in messages]), 200



@app.route('/messages/<message_id>', methods=['GET'])
def get_message(message_id):
    message = Messages.query.get(message_id)
    if message:
        return jsonify({ 'id' : message.id, 'message': message.message, 'likes_count': message.likes_count}), 200
    return jsonify({'error': 'Message not found with that id'}), 404



@app.route('/messages/<message_id>/like', methods=['POST'])
def add_like_message(message_id):
    data = request.get_json()
    like = Likes(message_id=message_id, username=data['username'])
    db.session.add(like)
    db.session.commit()
    return jsonify({'message': 'Successfully liked message'}), 201



@app.route('/messages/<message_id>/dislike', methods=['DELETE'])
def remove_like_message(message_id):
    data = request.get_json()
    like = Likes.query.filter_by(message_id=message_id, username=data['username']).delete()
    db.session.commit()
    return jsonify({'message': 'Successfully removed like'}), 201


if __name__ == '__main__':
    app.run(debug=True)

