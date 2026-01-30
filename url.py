from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./magasin.db"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base =  declarative_base()


class  ProduitDB(Base):
    __tablename__ = "produits"
    id = Column(Integer , primary_key= True,index=True)
    nom = Column(String, index = True)
    prix = Column(Integer)

Base.metadata.create_all(bind=engine)    

db = SessionLocal()

nouveau_produit = ProduitDB(nom="Ordinateur",prix =1000)

db.add(nouveau_produit)
db.commit()
db.refresh(nouveau_produit)

nouveau_produit = ProduitDB(nom="RTX_5090",prix =3000)

db.add(nouveau_produit)
db.commit()
db.refresh(nouveau_produit)

db.close()