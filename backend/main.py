from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlmodel import Session, SQLModel, create_engine, select
from typing import Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import os
from dotenv import load_dotenv

from models import User, FileRecord, UserCreate, UserLogin, Token
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cadviewer.db")
engine = create_engine(DATABASE_URL, echo=True)

# Create tables
SQLModel.metadata.create_all(engine)

# FastAPI app
app = FastAPI(title="CAD Viewer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File storage setup
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"message": "CAD Viewer API", "version": "1.0.0"}


# Auth endpoints
@app.post("/api/auth/register", response_model=User)
def register(user: UserCreate, session: Session = Depends(get_session)):
    # Check if user exists
    existing_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(400, detail="Email already registered")

    # Create new user
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.post("/api/auth/login", response_model=Token)
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(User.email == user_login.email)
    ).first()

    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/api/auth/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# File endpoints
@app.post("/api/files/upload", response_model=FileRecord)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Validate file type
    allowed_extensions = ['.gltf', '.glb', '.babylon', '.obj', '.stl']
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(400, detail="Invalid file type")

    # Save file
    file_id = f"{current_user.id}_{datetime.now().timestamp()}"
    file_path = UPLOAD_DIR / f"{file_id}{file_ext}"

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Save to database
    file_record = FileRecord(
        name=file.filename,
        path=str(file_path),
        size=len(content),
        user_id=current_user.id,
        uploaded_at=datetime.now()
    )

    session.add(file_record)
    session.commit()
    session.refresh(file_record)

    return file_record


@app.get("/api/files", response_model=List[FileRecord])
def get_user_files(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    files = session.exec(
        select(FileRecord).where(FileRecord.user_id == current_user.id)
    ).all()
    return files


@app.get("/api/files/{file_id}/download")
def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    file_record = session.exec(
        select(FileRecord).where(
            FileRecord.id == file_id,
            FileRecord.user_id == current_user.id
        )
    ).first()

    if not file_record:
        raise HTTPException(404, detail="File not found")

    return FileResponse(file_record.path, filename=file_record.name)


@app.delete("/api/files/{file_id}")
def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    file_record = session.exec(
        select(FileRecord).where(
            FileRecord.id == file_id,
            FileRecord.user_id == current_user.id
        )
    ).first()

    if not file_record:
        raise HTTPException(404, detail="File not found")

    # Delete file from disk
    try:
        os.remove(file_record.path)
    except:
        pass

    # Delete from database
    session.delete(file_record)
    session.commit()

    return {"message": "File deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)