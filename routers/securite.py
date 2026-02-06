from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone
from jose import jwt,JWTError
from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
import os
from enum import Enum
from dotenv import load_dotenv
load_dotenv()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def hashpassword(password :  str )-> str:
    return pwd_context.hash(password)


def verifMdp(mdpVerif : str , mdphashe: str )->bool:
    return pwd_context.verify(mdpVerif,mdphashe)

def token(data : dict ,expiration_delta : int = 30):
    to_encode =data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=expiration_delta)
    to_encode.update({"exp" :expiration.timestamp()})
    encoded_jwt = jwt.encode(to_encode,os.getenv("cleSecrete"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

def get_token(token :  str = Depends(oauth2_scheme) ):
    try:
        payload = jwt.decode(token,os.getenv("cleSecrete"),algorithms=[os.getenv("ALGORITHM")])
        username : str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Badge invalide")
        return username
    except JWTError as e:
        print(f"Détail de l'erreur : {e}")
        raise HTTPException(status_code=401,detail="session exipire ou invalide")
    
class TypeUser(str, Enum):
    admin="Gestionnaire"
    employe="Technitien"


