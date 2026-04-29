from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token
from app.utils import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter()
security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Récupère l'utilisateur depuis le token JWT"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Token manquant")
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user


@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = hash_password(user.password)
    # store hashed password into existing 'password' column
    new_user = User(username=user.username, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": new_user.username})
    return {"access_token": token}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    stored = getattr(db_user, 'password', None)
    # If stored looks like a bcrypt hash, verify; otherwise compare plaintext and upgrade to hashed
    if stored and (stored.startswith('$2a$') or stored.startswith('$2b$') or stored.startswith('$2y$')):
        if not verify_password(user.password, stored):
            raise HTTPException(status_code=401, detail="Identifiants incorrects")
    else:
        # fallback for legacy plaintext passwords
        if stored != user.password:
            raise HTTPException(status_code=401, detail="Identifiants incorrects")
        # upgrade to hashed password
        db_user.password = hash_password(user.password)
        db.add(db_user)
        db.commit()
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token}


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    """Retourne le profil de l'utilisateur connecté depuis la base de données"""
    return {
        "username": current_user.username,
    }


@router.put("/profile")
def update_profile(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Met à jour le profil utilisateur en base de données"""
    # Mise à jour username
    if "username" in data and data["username"] and data["username"] != current_user.username:
        existing = db.query(User).filter(User.username == data["username"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris")
        current_user.username = data["username"]

    # Mise à jour mot de passe
    if "password" in data and data["password"]:
        current_user.password = hash_password(data["password"])

    db.commit()
    db.refresh(current_user)
    return {
        "status": "ok",
        "username": current_user.username,
    }


@router.get("/users")
def search_users(
    search: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recherche d'utilisateurs par nom (pour l'admin)"""
    if not search:
        return []
    pattern = f"%{search}%"
    users = db.query(User).filter(
        User.username.ilike(pattern)
    ).limit(10).all()
    return [
        {"id": u.username, "username": u.username}
        for u in users
    ]
