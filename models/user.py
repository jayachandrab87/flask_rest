from db import db

class UserModel(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords
    email = db.Column(db.String(120), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def json(self):
        return {"id": self.id, "username": self.username, "email": self.email}