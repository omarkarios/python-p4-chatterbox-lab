from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Requirement: ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return make_response([m.to_dict() for m in messages], 200)

    elif request.method == 'POST':
        # Retrieve input as a dictionary with request.get_json()
        data = request.get_json()
        
        try:
            new_msg = Message(
                username=data.get('username'),
                body=data.get('body')
            )
            db.session.add(new_msg)
            db.session.commit()
            return make_response(new_msg.to_dict(), 201)
        except Exception as e:
            return make_response({"errors": [str(e)]}, 400)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    
    if not message:
        return make_response({"error": "Message not found"}, 404)

    if request.method == 'PATCH':
        data = request.get_json()
        # Updates the body of the message using params
        if 'body' in data:
            message.body = data.get('body')
            db.session.commit()
            return make_response(message.to_dict(), 200)
        return make_response({"errors": ["Missing body content"]}, 400)

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response({}, 204)

if __name__ == '__main__':
    app.run(port=5555, debug=True)