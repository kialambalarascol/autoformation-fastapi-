from fastapi import FastAPI , HTTPException,Depends
from pydantic import BaseModel,Field
from sqlalchemy import create_engine, Column, Integer, String,Boolean,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.security import OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv
from  routers import mail,securite

load_dotenv()


app = FastAPI(title="apprentissage FastAPI")

app.include_router(mail.router)
    
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







SQLALCHEMY_DATABASE_URL = f"postgresql+pg8000://postgres:{os.getenv('mdpDB')}@localhost:{os.getenv('port')}/magasin"

if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("L'URL de la base de donnees n'est pas configuree dans le fichier .env")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base =  declarative_base()





class  ProduitDB(Base):
    __tablename__ = "produits"
    id = Column(Integer , primary_key= True,index=True)
    nom = Column(String, index = True)
    prix = Column(Integer)



def get_db():

    db = SessionLocal()
    try:
        yield db  # On "prête" la session à la route
    finally:
        db.close() # On la recupere et on la ferme quoi qu'il arrive


class UtilisateurDB(Base):
    __tablename__ = "utilisateur"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    mdp = Column(Text)

class UtilisateurIn(BaseModel):
    nom: str
    mdp : str
    class Config:
        from_attributes=True

class UtilisateurOut(BaseModel):
    id : int
    nom: str
    class Config:
        from_attributes = True

@app.post("/inscription", tags=["utilisateurs"])
def ajoutUser(userData: UtilisateurIn,db: Session = Depends(get_db)):
    mdphashe=userData.mdp
    mdphashe=securite.hashpassword(mdphashe)
    verif  = db.query(UtilisateurDB).filter( UtilisateurDB.nom == userData.nom,  ).first()
    if verif :
        raise HTTPException(status_code=401,detail="utilisateur deja existant")
    ajout = UtilisateurDB(nom=userData.nom,mdp=mdphashe)
    db.add(ajout)
    db.commit()
    db.refresh(ajout)
    return{"message": f"utilisateur {userData.nom} a ete cree"}


@app.delete("/suppression",tags=["Admin"])
def supUser(nom:str ,db: Session = Depends(get_db)):
    supp = db.query(UtilisateurDB).filter(UtilisateurDB.nom == nom).first()
    if supp:
        db.delete(supp)
        db.commit()
        return {"message": f"utilisateur {nom} supprime"}
    raise HTTPException(status_code=404,detail="utilisateur inexistant")


@app.post("/login",tags=["utilisateurs"])
def connexion(formData :  OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    verificationUser =   db.query(UtilisateurDB).filter(UtilisateurDB.nom==formData.username).first()
    if(verificationUser and securite.verifMdp(formData.password, verificationUser.mdp)):
            user={"sub":verificationUser.nom}
            token = securite.token(user)
            return {"access_token":token,"token_type":"bearer"}
    else:
        raise HTTPException(status_code=401,detail="mot de passe ou utilisateur errone")
            

@app.get("/trouver",tags=["utilisateur"],response_model=list[UtilisateurOut])
def trouverUser(db:Session = Depends(get_db),nom_user : str =Depends(securite.get_token) ):
    rslt = db.query(UtilisateurDB).all()
    return rslt


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

class PlatDB(Base):
    __tablename__ = "plats"
    id =Column(Integer,primary_key=True,index= True, )
    nom =Column(String)
    en_stock = Column(Boolean)

class PlatSchema(BaseModel):
    id : int
    nom : str
    en_stock : bool

    class Config:
        from_attributes = True
        

class PlatCreate(BaseModel):
    nom :  str
    en_stock: bool


@app.post("/plats", response_model=list[PlatSchema])
def ajouterplat(plat :  PlatCreate ,db : Session= Depends(get_db)):
    
    ajout =  PlatDB(nom = plat.nom,en_stock=plat.en_stock)
    db.add(ajout)
    db.commit()
    db.refresh(ajout)
    rslt = db.query(PlatDB).all()
    return rslt






class CommandeCafe(BaseModel):
    nomCafe : str =Field(min_length = 4)
    taille : str =Field(min_length = 4)
    sucre : int = Field(ge=0)


@app.post("/commander")
def commander(commande : CommandeCafe):
    return {"commande":f"Votre {commande.nomCafe} {commande.taille} avec {commande.sucre} est en preparation"}


def verifBadge(couleur : str):
    if couleur !="red":
        raise HTTPException(status_code=403 , detail =" accès non autorise")
    return couleur

@app.get("/salle-serveur/", tags=["securite"])
def accesUser(data : str = Depends(verifBadge)):
    return {"message": f"Vous avez accès au salle serveur et à la zone VIP"}


@app.get("/zone-VIP/", tags=["securite"])
def acces(data: str =  Depends(verifBadge)):
    return {"message": f"Vous avez accès au salle serveur et à la zone VIP"}

''' Ceci est un path parameter de ce fait il est obligatoire quant à l'age c'est un query parmeter qui peut etre obligatoire mais aves la syntaxe | None = None elle devient optionnel'''
@app.get("/{nom}/",tags=["utilisateurs"])  
def get_eleve(nom : str ,age : int |None = None):
    if (age != None):
        return{f"Bonjoour {nom} vous avez {age} ans"}
    else:
        return(f"Bonjour {nom}")

""" Ici nous rentrons dans l'utilisation des class via pydantic , utilise pour la methode post et aussi dans l'utilisation des Field pour gerer les erreurs et imprevue"""
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
        raise HTTPException(status_code=401,detail="Pseudo reserve")
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
            raise HTTPException(status_code=401,detail="mdp errone")
        return convertisseur

@app.post("/convert/", response_model=ConvertisseurOutput,tags=["finance"], summary="converti des euro en dollars")
def convertisseur(data: ConvertisseurInput = Depends(verif_clef)):
    montant_initial = data.montant
    montant_converti= montant_initial * 1.1
    devise=data.devise
    return {"montant_initial":montant_initial,"montant_converti": montant_converti,"devise":devise}

# --- UPDATE PLAT ---
@app.put("/plats/{plat_id}", response_model=PlatSchema, tags=["Plats"])
def modifier_plat(plat_id: int, plat_in: PlatCreate, db: Session = Depends(get_db)):
    # 1. Recherche du plat
    db_plat = db.query(PlatDB).filter(PlatDB.id == plat_id).first()
    
    if not db_plat:
        raise HTTPException(status_code=404, detail="Plat introuvable")
    
    # 2. Mise à jour des donnees
    db_plat.nom = plat_in.nom
    db_plat.en_stock = plat_in.en_stock
    
    # 3. Validation en base
    db.commit()
    db.refresh(db_plat)
    return db_plat

# --- DELETE PLAT ---
@app.delete("/plats/{plat_id}", tags=["Plats"])
def supprimer_plat(plat_id: int, db: Session = Depends(get_db)):
    db_plat = db.query(PlatDB).filter(PlatDB.id == plat_id).first()
    
    if not db_plat:
        raise HTTPException(status_code=404, detail="Impossible de supprimer : plat inexistant")
    
    db.delete(db_plat)
    db.commit() # Toujours avec les parenthèses !
    return {"status": "success", "message": f"Plat {plat_id} supprime"}

Base.metadata.create_all(bind=engine)    