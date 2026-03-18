from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    token: str
    user_id: str
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
