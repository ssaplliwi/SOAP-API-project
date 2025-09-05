import uuid
import bcrypt
from spyne import ServiceBase, rpc, Unicode
from models.auth_models import RegisterResponse, LoginResponse
from storage.memory import users, sessions

class AuthService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=RegisterResponse)
    def register(ctx, username, password):
        if username in users:
            return RegisterResponse(status=False, message="User already exists!")
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        users[username] = hashed
        return RegisterResponse(status=True, message="Register success!")
    
    @rpc(Unicode, Unicode, _returns=LoginResponse)
    def login(ctx, username, password):
        hashed = users.get(username)
        if not hashed:
            return LoginResponse(status=False, message="User not found", session_key="")
        if bcrypt.checkpw(password.encode("utf-8"), hashed):
            session_key = str(uuid.uuid4())
            sessions[session_key] = username
            return LoginResponse(status=True, message="OK", session_key=session_key)
        return LoginResponse(status=False, message="Invalid password", session_key="")
