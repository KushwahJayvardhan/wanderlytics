"""
main.py

FastAPI app exposing the TripScope API.

Run locally:
    uvicorn api.main:app --reload

Docs available at /docs (Swagger) and /redoc.
"""

import logging

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api import schemas
from api.auth import create_access_token, get_current_user, hash_password, verify_password
from database.database import Base, engine, get_db
from database.models import Destination, Favorite, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tripscope")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TripScope API",
    description="REST API for exploring scraped travel destinations.",
    version="1.0.0",
)

# In production, restrict this to your actual Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled error on %s", request.url)
    raise HTTPException(status_code=500, detail="Internal server error") from exc


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- Destinations ----------

@app.get("/destinations", response_model=schemas.DestinationListResponse)
def list_destinations(
    q: str | None = Query(None, description="Search by name or description"),
    sort_by: str = Query("popularity", pattern="^(popularity|name)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Destination)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Destination.name.ilike(like), Destination.description.ilike(like))
        )

    total = query.count()

    if sort_by == "popularity":
        query = query.order_by(Destination.popularity_score.desc())
    else:
        query = query.order_by(Destination.name.asc())

    results = query.offset(offset).limit(limit).all()

    return schemas.DestinationListResponse(
        total=total, limit=limit, offset=offset, results=results
    )


@app.get("/destinations/{destination_id}", response_model=schemas.DestinationOut)
def get_destination(destination_id: int, db: Session = Depends(get_db)):
    destination = db.query(Destination).get(destination_id)
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    return destination


# ---------- Auth ----------

@app.post("/auth/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.Token)
def login(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(subject=user.email)
    return schemas.Token(access_token=token)


# ---------- Favorites (protected) ----------

@app.get("/favorites", response_model=list[schemas.DestinationOut])
def list_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [fav.destination for fav in current_user.favorites]


@app.post("/favorites", status_code=status.HTTP_201_CREATED)
def add_favorite(
    payload: schemas.FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    destination = db.query(Destination).get(payload.destination_id)
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    existing = (
        db.query(Favorite)
        .filter_by(user_id=current_user.id, destination_id=payload.destination_id)
        .first()
    )
    if existing:
        return {"message": "Already in favorites"}

    db.add(Favorite(user_id=current_user.id, destination_id=payload.destination_id))
    db.commit()
    return {"message": "Added to favorites"}


@app.delete("/favorites/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    destination_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fav = (
        db.query(Favorite)
        .filter_by(user_id=current_user.id, destination_id=destination_id)
        .first()
    )
    if fav:
        db.delete(fav)
        db.commit()
