from spyne import ComplexModel, Boolean, Unicode
from .common_base import TnsModel

class RegisterRequest(TnsModel):
    username = Unicode
    password = Unicode

class RegisterResponse(TnsModel):
    status = Boolean
    message = Unicode

class LoginRequest(TnsModel):
    username = Unicode
    password = Unicode

class LoginResponse(TnsModel):
    status = Boolean
    message = Unicode
    session_key = Unicode
