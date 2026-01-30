from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel,Field
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI(title="apprentissage FastAPI")
"""
class User(BaseModel):
    username:str
    is_premium: bool | None = None
    level: int = 1

@app.get("/")
def main():
    return {"message": "Bienvenue sur l'api"}


@app.get("/users/{user_id}")
def get_user(user_id : int , premium: bool = False):
    return{"id": user_id,"is_premium" : premium}




@app.post("/users/")
def create_user(user:User):
    return{"user":f"l'utilisateur {user.username} est niveau {user.level} premium : {user.is_premium}" }

"""

class ItemInput(BaseModel):
    nom :str
    prix : float = Field(gt=0)
    quantite : int = Field(ge=0)
class ItemOutput(BaseModel):
    nom : str 
    prix_ttc : float = Field(gt=0)
    en_stock : bool 


def verif_admin(mdp :str ):
    if mdp != "boss123":
        raise HTTPException(status_code=401, detail = "accès interdit")
    return mdp

@app.get("/stock/stats/", tags=["Public"])
def article_vente(nb_article : int):
    return {"nombre d'article": nb_article}

@app.post("/stock/ajouter",response_model=ItemOutput, tags=["Admin"])
def calcule(item : ItemInput ,data : str = Depends(verif_admin)):
    prix_ttc = item.prix * 1.2 
    if item.quantite > 0 :
        stock = True
        return {"nom": item.nom,"prix_ttc":prix_ttc,"en_stock": stock}
    stock = False
    return {"nom": item.nom,"prix_ttc":prix_ttc,"en_stock": stock}
    


@app.get("/stock/{item_id}", tags=["Public"])
def cherche_article(item_id : int , nom : str):
    return {"nom": nom,"article": item_id}








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

def get_db():

    db = SessionLocal()
    try:
        yield db  # On "prête" la session à la route
    finally:
        db.close() # On la récupère et on la ferme quoi qu'il arrive

class ProduitSchema(BaseModel):
    id: int
    nom: str
    prix: int

    class Config:
        from_attributes = True # Autorise Pydantic à lire les objets de la DB


@app.get("/produits", tags=["Admin"], response_model= list[ProduitSchema])
def get_produit(db : Session = Depends(get_db)):
    resultat =db.query(ProduitDB).all()
    print (resultat)
    return resultat

@app.get("/produit/{nom_produit}", tags=["Admin"],)
def trouver(nom : str , db : Session = Depends(get_db)):
    resultat = db.query(ProduitDB).filter(ProduitDB.nom == nom)






















def verifBadge(couleur : str):
    if couleur !="red":
        raise HTTPException(status_code=403 , detail =" accès non autorisé")
    return couleur

@app.get("/salle-serveur/", tags=["sécurité"])
def accesUser(data : str = Depends(verifBadge)):
    return {"message": f"Vous avez accès au salle serveur et à la zone VIP"}


@app.get("/zone-VIP/", tags=["sécurité"])
def acces(data: str =  Depends(verifBadge)):
    return {"message": f"Vous avez accès au salle serveur et à la zone VIP"}

''' Ceci est un path parameter de ce fait il est obligatoire quant à l'age c'est un query parmeter qui peut etre obligatoire mais aves la syntaxe | None = None elle devient optionnel'''
@app.get("/{nom}/",tags=["utilisateurs"])  
def get_eleve(nom : str ,age : int |None = None):
    if (age != None):
        return{f"Bonjoour {nom} vous avez {age} ans"}
    else:
        return(f"Bonjour {nom}")

""" Ici nous rentrons dans l'utilisation des class via pydantic , utilisé pour la methode post et aussi dans l'utilisation des Field pour gérer les erreurs et imprévue"""
class Produit(BaseModel):
    nom: str = Field(min_length = 2)
    prix : float = Field(gt=0) 
    taxee: bool

@app.post("/product/",tags=["finance"])
def validateur(produit : Produit ):
    if (produit.taxee == True):
        return{f"Le produit {produit.nom} est au prix de {produit.prix * 1.2} € "}
    else:
        return{f"Le produit {produit.nom} est au prix de {produit.prix} € "}


"""exo 3 """

class User(BaseModel):
    pseudo : str = Field(min_length = 3)
    age : int = Field(gt=0)


@app.post("/check-entry/",tags=["utilisateurs"])
def verifAge(user:User):
    if (user.age < 18 ):
        raise HTTPException(status_code=403,detail="Accès interdit aux mineurs ")
    elif (user.pseudo == "admin"):
        raise HTTPException(status_code=401,detail="Pseudo réservé")
    else:
        return {"message": f" Bienvenue {user.pseudo} !"}


class ConvertisseurInput(BaseModel):
    montant : float = Field(gt=0)
    devise : str 
    secret_key : str

class ConvertisseurOutput(BaseModel):
    montant_initial:float
    montant_converti:float
    devise:str

""" La j'apprend a diviser mes parametres pour l'utiliser dans plusieur partie de mon code"""
def verif_clef(convertisseur: ConvertisseurInput):
        if convertisseur.secret_key != "1234":
            raise HTTPException(status_code=401,detail="mdp érroné")
        return convertisseur

@app.post("/convert/", response_model=ConvertisseurOutput,tags=["finance"], summary="converti des euro en dollars")
def convertisseur(data: ConvertisseurInput = Depends(verif_clef)):
    montant_initial = data.montant
    montant_converti= montant_initial * 1.1
    devise=data.devise
    return {"montant_initial":montant_initial,"montant_converti": montant_converti,"devise":devise}


