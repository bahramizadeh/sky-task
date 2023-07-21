from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token
from db import db
from models.user import UserModel
from schemas import UserSchema



blp = Blueprint("Users","users",description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    
    @blp.arguments(UserSchema)
    def post(self, user_info):
        if UserModel.query.filter(UserModel.username==user_info["username"]).first():
            abort(409, message="A user with that username already exists.")
        
        user = UserModel(
            username = user_info["username"], 
            password = pbkdf2_sha256.hash(user_info["password"])
        )
        
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201
    
    
    
@blp.route("/user/<int:user_id>")
class User(MethodView):
    
    @blp.response(200, UserSchema)
    def get(self, user_id):
        
        user = UserModel.query.get_or_404(user_id)
        return user
    

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return {"message": "User deleted."}, 201
        


@blp.route("/login")        
class login(MethodView):
    
    @blp.arguments(UserSchema)
    def post(self, user_info):
        user = UserModel.query.filter(
            UserModel.username == user_info["username"]
        ).first()
        
        if user and pbkdf2_sha256.verify(user_info["password"], user.password):
            access_token = create_access_token(identity=user.id)
            
            return {"access_tocken": access_token}, 200
        
        
        abort(401, message="Invalid credentials.")