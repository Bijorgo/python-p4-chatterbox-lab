from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

#GET
@app.get("/")
def index():
    respnose_dict = { "message" : "Hello, World! Welcome to Messages."}
    return make_response( respnose_dict, 200)

#GET
# returns an array of all messages as JSON, ordered by created_at in ascending order.
@app.get('/messages')
def messages():
    respnse_dict_list = ([message.to_dict() for message in Message.query.all()])

    response = make_response(
        respnse_dict_list,
        200
    )
    return response

#GET by id
@app.get('/messages/<int:id>')
def messages_by_id(id):
    message = db.session.get(Message, id)
    if message:
        response_dict = message.to_dict()
        return make_response(response_dict, 200)
    else:
        resonse_dict = { "error" : "ID not found"}
        return make_response(response_dict, 404)
  
#POST
# creates a new message with a body and username from params, and returns the newly created post as JSON.
# FOR LATER: REVIEW THIS PART
# This part took forever to fix: remove the default fields. Still doesn't really make sense to me
@app.post('/messages')
def new_message():
    new_message = request.json
    required_fields = ["body", "username"]

    if not all(field in new_message for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400  # Bad request

    try:
        # Create new message and remove created_at/updated_at from the request
        message = Message(
            body=new_message["body"],
            username=new_message["username"]
        )
        db.session.add(message)
        db.session.commit()
        # Return the created message
        response_dict = message.to_dict()
        return make_response(response_dict, 201)  # Created
    except Exception as exc:
        response_dict = {"error": str(exc)}
        return make_response(response_dict, 400)  # Bad request

#PATCH
# updates the body of the message using params, and returns the updated message as JSON.
@app.patch('/messages/<int:id>')
def update_messages_by_id(id):
    existing_message = db.session.get(Message, id)
    if existing_message:
        try:
            updated_message = request.json
            for key in updated_message:
                setattr(existing_message, key, updated_message[key])
            db.session.add(existing_message)
            db.session.commit()
            response_dict = db.session.get(Message, id).to_dict()
            return make_response(response_dict, 200)
        except Exception as exc:
            response_dict = {"error": str(exc)}
            return make_response(response_dict, 400)  # Bad request
    else:
        response_dict = { "error" : "ID was not found" }
        return make_response(response_dict, 404)# ID not found


#DELETE
# deletes the message from the database.
@app.delete('/messages/<int:id>')
def delete_messages_by_id(id):
    existing_message = db.session.get(Message, id)
    if existing_message:
        try:
            db.session.delete(existing_message)
            db.session.commit()
            return make_response('', 204) # No Content, sucess
        except Exception as exc:
            response_dict = { "error" : "ID was not found" }
            return make_response(response_dict, 404)# ID not found
    return ''

if __name__ == '__main__':
    app.run(port=5555)
