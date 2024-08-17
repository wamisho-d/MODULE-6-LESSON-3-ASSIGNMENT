# Question 1 Task 1: Setting Up Flask with Flask-SQLAlchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@localhost/fitness_center_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Define the Member model
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    join_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Member {self.name}>'

# Define the WorkoutSession model
class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    type = db.Column(db.String(50), nullable=False)

    member = db.relationship('Member', backref=db.backref('workout_sessions', lazy=True))

    def __repr__(self):
        return f'<WorkoutSession {self.type} for {self.duration} minutes>'

if __name__ == '__main__':
    app.run(debug=True)


# Qustion 1 Task 2: Implementing CRUD Operations for Members Using ORM
# Create the Flask application and configure the database:
from falsk import Flask, request, jsonify
from falsk_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Define the Member model:

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

db.create_all()

#Create the CRUD routes:

# Create a new member
@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    if not data or not 'name' in data or not 'email' in data:
        return jsonify({'error': 'Bad Request', 'message': 'Name and email are required'}), 400
    
    new_member = Member(name=data['name'], email=data['email'])
    try:
        db.session.add(new_member)
        db.session.commit()
        return jsonify(new_member.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

# Retrieve all members
@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members]), 200

# Retrieve a single member by ID
@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get_or_404(id)
    return jsonify(member.to_dict()), 200

# Update a member
@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    member = Member.query.get_or_404(id)
    
    if 'name' in data:
        member.name = data['name']
    if 'email' in data:
        member.email = data['email']
    
    try:
        db.session.commit()
        return jsonify(member.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

# Delete a member
@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    try:
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Member deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

# Question 1 Task 3: Managing Workout Sessions with ORM
# Creat the Flask Application
from falsk import Flask, request, jsonify
from falsk_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# define moduls
# Define the Member and WorkoutSession models:

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    workout_sessions = db.relationship('WorkoutSession', backref='member', lazy=True)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    description = db.Column(db.String(200), nullable=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

# Create the Database

# Initialize the database:

@app.before_first_request
def create_tables():
    db.create_all()


# Step 5: Define the Routes

# Route to Schedule a Workout Session

@app.route('/schedule', methods=['POST'])
def schedule_workout():
    data = request.get_json()
    new_session = WorkoutSession(
        date=data['date'],
        duration=data['duration'],
        description=data.get('description'),
        member_id=data['member_id']
    )
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message': 'Workout session scheduled successfully'}), 201


# Route to Update a Workout Session

@app.route('/update/<int:session_id>', methods=['PUT'])
def update_workout(session_id):
    data = request.get_json()
    session = WorkoutSession.query.get(session_id)
    if not session:
        return jsonify({'message': 'Session not found'}), 404

    session.date = data.get('date', session.date)
    session.duration = data.get('duration', session.duration)
    session.description = data.get('description', session.description)
    db.session.commit()
    return jsonify({'message': 'Workout session updated successfully'})


# Route to View All Workout Sessions for a Specific Member

@app.route('/member/<int:member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'message': 'Member not found'}), 404

    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    output = []
    for session in sessions:
        session_data = {
            'id': session.id,
            'date': session.date,
            'duration': session.duration,
            'description': session.description
        }
        output.append(session_data)
    return jsonify({'workout_sessions': output})





