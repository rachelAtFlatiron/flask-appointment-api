#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api
import datetime
from models import db, Doctor, Patient, Appointment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# flask-restful
# DO NOT NAME FLASK-RESTFUL CLASSES SAME AS MODEL CLASSES
# OR YOU WILL BE OVERWRITING YOUR MODEL CLASS 
class AllDoctors(Resource):
    def get(self):
         docs = Doctor.query.all()
         docs_list = [doc.to_dict(only=('id', 'name', 'specialty')) for doc in docs]
         return make_response(docs_list, 200)
    def post(self):
        try:
            # get data 
            data = request.get_json()
            # create new instance
            new_doc = Doctor(name=data.get('name'), specialty=data.get('specialty'))
            # add new instance to db 
            db.session.add(new_doc)
            db.session.commit()
        except Exception as e: 
            # e is an instance of an Error, convert it to a string
            return make_response({"message": str(e)}, 422)

        #return make_response
        return make_response(new_doc.to_dict(rules=('-appointments', )), 201)
    
api.add_resource(AllDoctors, '/doctors')

class OneDoctor(Resource):
    def get(self, id):
        doc = Doctor.query.filter_by(id=id).first()
        if(not doc):
            return make_response({"message": f"doctor {id} not found"}, 404)
        return make_response(doc.to_dict(), 200)
api.add_resource(OneDoctor, '/doctors/<int:id>')

class OnePatient(Resource):
    # TODO: update q.to_dict() to include doctors relationship
    def get(self, id):
        q = Patient.query.filter_by(id=id).first()
        if(not q):
            return make_response({f'patient {id} not found'}, 404)
        return make_response(q.to_dict(only=('doctors.id', 'doctors.name', 'doctors.specialty', 'id', 'name')), 200)
    
    def patch(self, id):
        try:
            # get instance
            q = Patient.query.filter_by(id=id).first()
            if(not q):
                return make_response({f'patient {id} not found'}, 404)
            # get all the data 
            data = request.get_json()
            # update attributes
            for field in data:
                setattr(q, field, data.get(field))
            # add/commit
            db.session.add(q)
            db.session.commit()
        except Exception as e:
            return make_response({"message": e}, 422)
        # return json
        return make_response(q.to_dict(only=('id', 'name')), 200)
api.add_resource(OnePatient, '/patients/<int:id>')

class AllAppointments(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_appt = Appointment(doctor_id=data.get("doctor_id"), patient_id=data.get("patient_id"), day=data.get("day"))
            db.session.add(new_appt)
            db.session.commit()
            return make_response(new_appt.to_dict(rules=('-doctor_id', '-patient_id')), 201)
        except Exception as e:
            return make_response(str(e), 422)
api.add_resource(AllAppointments, '/appointments')

class OneAppointment(Resource):
    def delete(self, id):
        q = Appointment.query.filter_by(id=id).first()
        if(not q):
            return make_response({'message': f'Appointment {id} not found'}, 404)
        db.session.delete(q)
        db.session.commit()
        return make_response({}, 204)
api.add_resource(OneAppointment, '/appointments/<int:id>')


@app.get("/")
def index():
    return "doctor/patient"





if __name__ == "__main__":
    app.run(port=5555, debug=True)
