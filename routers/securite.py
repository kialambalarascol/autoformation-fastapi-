from passlib.context import CryptContext
from pydantic import BaseModel,Field
from datetime import datetime, timedelta
from jose import jwt

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hashpassword(password :  str )-> str:
    return pwd_context.hash(password)


def verifMdp(mdpVerif : str , mdphashe: str )->bool:
    return pwd_context.verify(mdpVerif,mdphashe)
