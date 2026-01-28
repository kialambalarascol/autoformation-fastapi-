from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class  userDB(Base):
    __tablename__ = "utilisateur"
    id = Column(Integer , primaary_key= True,index=True)
    nom = Column(String)
    prix = Column(Int)