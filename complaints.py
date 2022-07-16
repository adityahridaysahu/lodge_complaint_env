from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import codecs
import base64
import requests

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///complaints_database.db"
db = SQLAlchemy(app)
BASE = "http://127.0.0.1:5000/"


class ComplaintModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    img = db.Column(db.Binary, unique=True, nullable=False)
    location = db.Column(db.String(18), nullable=False)
    creator_phone = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f"Complaint(Complaint_ID = {id}, Complaint_Category = {category}, Complaint_Title = {subject}, Description = {description}, Complaint_Image = {img}, Complaint_Location = {location}, Creation_Timestamp = {date}, Creator_Phone = {creator_phone}, Complaint_Status = {status})"


db.create_all()

complaint_put_args = reqparse.RequestParser()
complaint_put_args.add_argument(
    "subject", type=str, help="A Complaint Subject is Required!", required=True
)
complaint_put_args.add_argument(
    "description", type=str, help="A Complaint Description is Required!", required=True
)
complaint_put_args.add_argument(
    "date", type=str, help="Creation date of the complaint", required=True
)
complaint_put_args.add_argument(
    "category", type=str, help="Category of the complaint", required=True
)
complaint_put_args.add_argument(
    "location", type=str, help="Location of the complaint", required=True
)
complaint_put_args.add_argument("img", type=str, help="img string", required=True)
complaint_put_args.add_argument(
    "creator_phone", type=int, help="Creator Phone", required=True
)
complaint_put_args.add_argument(
    "status", type=str, help="Status of the complaint", required=True
)


resource_fields = {
    "id": fields.Integer,
    "subject": fields.String,
    "description": fields.String,
    "date": fields.String,
    "category": fields.String,
    "location": fields.String,
    "creator_phone": fields.Integer,
    "status": fields.String,
    "img": fields.String,
}


class Complaint(Resource):
    @marshal_with(resource_fields)
    def get(self, complaint_id):
        result = ComplaintModel.query.filter_by(id=complaint_id).first()
        if not result:
            abort(404, message="Could not find any complaint with that id")

        return result

    @marshal_with(resource_fields)
    def put(self, complaint_id):
        args = complaint_put_args.parse_args()
        result = ComplaintModel.query.filter_by(id=complaint_id).first()
        if result:
            abort(409, message="That complaint ID is already taken...")

        byteData = codecs.encode(args["img"], "UTF-8")
        imgData = base64.decodebytes(byteData)

        complaint = ComplaintModel(
            id=complaint_id,
            subject=args["subject"],
            description=args["description"],
            date=args["date"],
            category=args["category"],
            img=imgData,
            location=args["location"],
            creator_phone=args["creator_phone"],
            status=args["status"],
        )
        db.session.add(complaint)
        db.session.commit()
        return complaint, 201


class getComp(Resource):
    @marshal_with(resource_fields)
    def get(self, creator_phone):
        result = ComplaintModel.query.filter_by(creator_phone=creator_phone).first()
        if not result:
            abort(404, message="No complaint lodged with that phone number")

        return result


class getCompByNum(Resource):
    @marshal_with(resource_fields)
    def get(self, num, creator_phone):
        target_id = str(creator_phone) + str(num)
        result = ComplaintModel.query.filter_by(id=int(target_id)).first()
        if not result:
            abort(404, message="There's no such complaint with that index by this user")

        return result


api.add_resource(Complaint, "/complaint/<int:complaint_id>")
api.add_resource(getComp, "/getComplaints/<int:creator_phone>")
api.add_resource(getCompByNum, "/getCompByNum/<int:creator_phone>/<int:num>")

if __name__ == "__main__":
    app.run(debug=True)
