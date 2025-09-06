import uuid
import bcrypt
from spyne import ServiceBase, rpc, Unicode
from models.auth_models import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from db import SessionLocal
from db_models import User, Session as DBSession
from sqlalchemy.exc import IntegrityError

def _hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode("utf-8"), hashed.encode("utf-8"))

class AuthService(ServiceBase):
    @rpc(RegisterRequest, _returns=RegisterResponse)
    def register(ctx, req):
        db = SessionLocal()
        try:
            u = User(username=req.username, password_hash=_hash_password(req.password))
            db.add(u)
            db.commit()
            return RegisterResponse(status=True, message="Register success")
        except IntegrityError:
            db.rollback()
            return RegisterResponse(status=False, message="Username already exists")
        finally:
            db.close()

    @rpc(LoginRequest, _returns=LoginResponse)
    def login(ctx, req):
        db = SessionLocal()
        try:
            u = db.query(User).filter(User.username == req.username).first()
            if not u:
                return LoginResponse(status=False, message="User not found", session_key="")

            if not _check_password(req.password, u.password_hash):
                return LoginResponse(status=False, message="Invalid password", session_key="")

            sk = str(uuid.uuid4())
            s = DBSession(session_key=sk, username=u.username)
            db.add(s)
            db.commit()
            return LoginResponse(status=True, message="OK", session_key=sk)
        finally:
            db.close()
