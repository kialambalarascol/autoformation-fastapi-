
from fastapi import APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic_settings import BaseSettings
from pydantic import BaseModel,Field
import os
from dotenv import load_dotenv
load_dotenv()

router=APIRouter(prefix='/utilisateur/mail', tags=["EMAIL"])



class Settings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD : str
    MAIL_FROM:str
    MAIL_PORT: int
    MAIL_SERVER : str
    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)


class EmailRequest(BaseModel):
    destinataire :  str
    sujet : str
    contenu : str


@router.post("")
async def envoi_email(request : EmailRequest):
    message = MessageSchema(
        subject=request.sujet,
        recipients=[request.destinataire],
        body=request.contenu,
        subtype=MessageType.html
        )
    fm = FastMail(mail_conf)
    await fm.send_message(message)
    return {"status": "success", "message": "Email envoyé avec succès"}
