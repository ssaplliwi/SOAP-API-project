from spyne import ComplexModel, Boolean, Unicode

class RegisterResponse(ComplexModel):
    status = Boolean
    message = Unicode

class LoginResponse(ComplexModel):
    status = Boolean
    message = Unicode
    session_key = Unicode
    