from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Chandigarh', 'Puducherry',
    'Andaman and Nicobar Islands', 'Dadra and Nagar Haveli', 'Lakshadweep', 'All India'
]

QUALIFICATIONS = [
    '10th Pass', '12th Pass', 'Graduation', 'Post Graduation', 'ITI',
    'Diploma', 'B.Tech/B.E.', 'MBBS', 'LLB', 'B.Ed', 'PhD', 'Any'
]

JOB_TYPES = [
    'latest_jobs', 'admit_card', 'result', 'answer_key', 'syllabus', 'admission'
]


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    jobs = db.relationship('Job', backref='category_rel', lazy='dynamic')


class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(350), unique=True, nullable=False)
    organization = db.Column(db.String(200), default='')
    department = db.Column(db.String(200), default='')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    qualification = db.Column(db.String(100), default='')
    state = db.Column(db.String(100), default='All India')
    total_posts = db.Column(db.String(50), default='')
    salary = db.Column(db.String(200), default='')
    application_fee = db.Column(db.Text, default='')
    age_limit = db.Column(db.Text, default='')
    selection_process = db.Column(db.Text, default='')
    start_date = db.Column(db.String(50), default='')
    last_date = db.Column(db.String(50), default='')
    apply_link = db.Column(db.String(500), default='')
    notification_link = db.Column(db.String(500), default='')
    official_website = db.Column(db.String(500), default='')
    description = db.Column(db.Text, default='')
    how_to_apply = db.Column(db.Text, default='')
    vacancy_details = db.Column(db.Text, default='')
    job_type = db.Column(db.String(50), default='latest_jobs')
    views = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    is_scraped = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    type = db.Column(db.String(50), default='email')
    status = db.Column(db.String(50), default='pending')
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    job = db.relationship('Job', backref='notifications')
