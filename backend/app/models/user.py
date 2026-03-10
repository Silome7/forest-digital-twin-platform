from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin  
from app.models.associations import user_roles


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    firstname = db.Column(db.String(120), unique=False, nullable=True)
    lastname = db.Column(db.String(120), unique=False, nullable=True)
    telephone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="agent")  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    roles = db.relationship('Role', secondary=user_roles, back_populates='users',lazy="dynamic")
    
    def set_password(self, password):
        
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
    
        return check_password_hash(self.password_hash, password)
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission_name):
        for role in self.roles:
            if permission_name in role.permissions:
                return True
        return False
    
    def add_role(self, role):
        if not self.has_role(role.name):
            self.roles.append(role)
    
    def remove_role(self, role_name):
        role_to_remove = None
        for role in self.roles:
            if role.name == role_name:
                role_to_remove = role
                break
        if role_to_remove:
            self.roles.remove(role_to_remove)
    
    def __repr__(self):
        return f'<User {self.email}>'
