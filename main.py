import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, status, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

print("Environment Variables Loaded:")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PW: {os.getenv('DB_PW')}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

# Get the environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")

# Construct the DATABASE_URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PW}@care2share-db.clygygsmuyod.us-east-1.rds.amazonaws.com:3306/{DB_NAME}"
print(f"DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model for Users
class UserModel(Base):
    __tablename__ = "Users"  # Use the existing Users table
    UNI = Column(String, primary_key=True)
    password_hash = Column(String)
    num_of_swipes_given = Column(Integer, default=0)
    num_of_swipes_received = Column(Integer, default=0)


# Get a db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic model for request validation
class User(BaseModel):
    UNI: str
    password_hash: str
    num_of_swipes_given: Optional[int] = 0
    num_of_swipes_received: Optional[int] = 0


class UserResponse(BaseModel):
    user: User
    links: Dict[str, str]


class UserSwipeUpdate(BaseModel):
    UNI: str
    num_of_swipes_received: int


# Root endpoint
@app.get("/")
async def root():
    return {"\n\nmessage": "Hello from recipient_service_Care2Share!\n\n"}


@app.get("/hello/{name}")
async def hello(name: str):
    msg = f"Hello {name} from recipient_service_Care2Share!"
    return {"\n\nmessage": msg}


# Endpoint to create a new user with 201 Created and Location Header
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create User")
async def create_user(user: User, response: Response, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.UNI == user.UNI).first():
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Set the Location header
    response.headers["Location"] = f"/users/{db_user.UNI}"

    return UserResponse(
        user=user,
        links={
            "self": f"/users/{db_user.UNI}",
            "list": "/users/",
            "update": f"/users/{db_user.UNI}",
            "delete": f"/users/{db_user.UNI}"
        }
    )


# Retrieve user by UNI
@app.get("/users/{UNI}", response_model=UserResponse)
async def get_user(UNI: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.UNI == UNI).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        user=User(UNI=user.UNI, password_hash=user.password_hash,
                   num_of_swipes_given=user.num_of_swipes_given,
                   num_of_swipes_received=user.num_of_swipes_received),
        links={
            "self": f"/users/{UNI}",
            "list": "/users/",
            "update": f"/users/{UNI}",
            "delete": f"/users/{UNI}"
        }
    )


# Update user's information
@app.put("/users/{UNI}", response_model=UserResponse)
async def update_user(UNI: str, updated_user: User, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.UNI == UNI).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in updated_user.dict().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return UserResponse(
        user=User(UNI=user.UNI, password_hash=user.password_hash,
                   num_of_swipes_given=user.num_of_swipes_given,
                   num_of_swipes_received=user.num_of_swipes_received),
        links={
            "self": f"/users/{UNI}",
            "list": "/users/",
            "delete": f"/users/{UNI}"
        }
    )


# Delete a user by UNI
@app.delete("/users/{UNI}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(UNI: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.UNI == UNI).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# List users with pagination
@app.get("/users/", response_model=List[UserResponse])
async def list_users(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset((page - 1) * page_size).limit(page_size).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    return [UserResponse(
        user=User(UNI=u.UNI, password_hash=u.password_hash,
                   num_of_swipes_given=u.num_of_swipes_given,
                   num_of_swipes_received=u.num_of_swipes_received),
        links={
            "self": f"/users/{u.UNI}",
            "list": "/users/",
            "update": f"/users/{u.UNI}",
            "delete": f"/users/{u.UNI}"
        }
    ) for u in users]


# Asynchronous user points update with 202 Accepted
@app.put("/user_swipes/update_async", status_code=status.HTTP_202_ACCEPTED)
async def update_user_swipes_async(updates: UserSwipeUpdate, db: Session = Depends(get_db)):
    async def update_swipes(UNI: str, swipes: int):
        await asyncio.sleep(1)  # Simulate async work

        user = db.query(UserModel).filter(UserModel.UNI == UNI).first()
        if user:
            user.num_of_swipes_received += swipes
            db.commit()
        else:
            raise HTTPException(status_code=404, detail="User not found")

    await asyncio.gather(update_swipes(updates.UNI, updates.num_of_swipes_received))
    return {
        "status": "User swipes update has been accepted and is processing",
        "self": f"/user_swipes/update_async"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)