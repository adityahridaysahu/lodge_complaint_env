from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import codecs
import base64

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user_database.db"
db = SQLAlchemy(app)


class UserModel(db.Model):
    phone_no = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    admin_stat = db.Column(db.Integer, nullable=False)
    comp_num = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User(phone_no = {phone_no}, username = {username}, admin_stat = {admin_stat}, comp_num = {comp_num})"


db.create_all()

user_put_args = reqparse.RequestParser()
user_put_args.add_argument(
    "username", type=str, help="A Username is Required!", required=True
)
user_put_args.add_argument(
    "admin_stat", type=int, help="Admin Status is Required!", required=True
)
user_put_args.add_argument(
    "comp_num", type=int, help="Number of Complaints is Required!", required=True
)


user_update_args = reqparse.RequestParser()
user_update_args.add_argument(
    "username", type=str, help="A Username is Required!", required=False
)
user_update_args.add_argument(
    "admin_stat", type=int, help="Admin Status is Required!", required=False
)
user_update_args.add_argument(
    "comp_num", type=int, help="Number of Complaints is Required!", required=False
)


resource_fields = {
    "phone_no": fields.Integer,
    "username": fields.String,
    "admin_stat": fields.Integer,
    "comp_num": fields.Integer,
}


class User(Resource):
    @marshal_with(resource_fields)
    def get(self, phone_no):
        result = UserModel.query.filter_by(phone_no=phone_no).first()
        if not result:
            abort(404, message="Incorrect Credentials!")

        return result

    @marshal_with(resource_fields)
    def put(self, phone_no):
        args = user_put_args.parse_args()
        result = UserModel.query.filter_by(phone_no=phone_no).first()
        if result:
            abort(409, message="A user with this phone number already exists!")

        user = UserModel(
            phone_no=phone_no,
            username=args["username"],
            admin_stat=args["admin_stat"],
            comp_num=args["comp_num"],
        )
        db.session.add(user)
        db.session.commit()
        return user, 201

    @marshal_with(resource_fields)
    def patch(self, phone_no):
        args = user_update_args.parse_args()
        result = UserModel.query.filter_by(phone_no=phone_no).first()
        if not result:
            abort(404, message="No user with that phone number found!")

        temp = result.comp_num
        temp = temp + 1
        result.comp_num = temp
        db.session.commit()


api.add_resource(User, "/user/<int:phone_no>")

if __name__ == "__main__":
    app.run(debug=True)
