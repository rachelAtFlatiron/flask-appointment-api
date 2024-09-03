from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
import string, datetime

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)
db = SQLAlchemy(metadata=metadata)


class Patient(db.Model, SerializerMixin):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    appointments = db.relationship('Appointment', back_populates='patient')
    doctors = association_proxy('appointments', 'doctor')

    serialize_rules = ('-appointments.patient', )
    def __repr__(self):
        return f'<Patient {self.id} {self.name}>'

class Appointment(db.Model, SerializerMixin):

    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String, nullable=False)

    #foreign keys 
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))

    doctor = db.relationship('Doctor', back_populates='appointments')
    patient = db.relationship('Patient', back_populates='appointments')

    @validates("day")
    def validate_day(self, key, user_input):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if(user_input not in days):
            raise ValueError('day must be Mon-Fri')
        return user_input
    
    serialize_rules = ('-doctor.appointments', '-patient.appointments')

    def __repr__(self):

        return f'<Appointment {self.id} {self.day}>'

class Doctor(db.Model, SerializerMixin):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)
    specialty = db.Column(db.String, nullable=False)

    appointments = db.relationship('Appointment', back_populates='doctor')
    patients = association_proxy('appointments', 'patient')
    @validates("name")
    def validate_name(self, key, user_input):
        if(user_input[0:3]=='Dr.'):
            return user_input 
        raise ValueError('name must start with Dr.')
    
    serialize_rules=('-appointments.doctor',)
    
    def __repr__(self):
        return f'<Doctor {self.id} {self.name} {self.specialty}>'