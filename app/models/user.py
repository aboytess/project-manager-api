import uuid
from datetime import datetime, timezone
from ..extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    owned_projects = db.relationship('Project', backref='owner', lazy=True, foreign_keys='Project.owner_id')
    assigned_tasks = db.relationship('Task', backref='assignee', lazy=True, foreign_keys='Task.assignee_id')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

    def to_public_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }
