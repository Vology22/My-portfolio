from fastapi import APIRouter, HTTPException
from typing import Optional
import sys
sys.path.append('..')
from database import get_connection
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    full_name: str
    bio: Optional[str] = ""
    tg_id: str
    avatar: Optional[str] = ""
    age: int
    gender: Optional[str] = ""
    badHabits: Optional[str] = ""
    pet: Optional[str] = ""
    hasRoommate: Optional[str] = ""

class UserResponse(BaseModel):
    user_id: int
    full_name: Optional[str]
    bio: Optional[str]
    avatar: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    badHabits: Optional[str]
    pet: Optional[str]
    hasRoommate: Optional[str]
    tg_id: Optional[str]

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE tg_id = %s", (user.tg_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(
                "UPDATE users SET full_name = %s, bio = %s, avatar = %s, age = %s, gender = %s, bad_habits = %s, pets = %s, partner = %s WHERE tg_id = %s",
                (user.full_name, user.bio, user.avatar, user.age, user.gender, user.badHabits, user.pet, user.hasRoommate, user.tg_id)
            )
            user_id = existing[0]
        else:
            cursor.execute(
                "INSERT INTO users (full_name, bio, avatar, age, gender, bad_habits, pets, partner, tg_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (user.full_name, user.bio, user.avatar, user.age, user.gender, user.badHabits, user.pet, user.hasRoommate, user.tg_id)
            )
            user_id = cursor.lastrowid
        
        conn.commit()
        return UserResponse(
            user_id=user_id,
            full_name=user.full_name,
            bio=user.bio,
            avatar=user.avatar,
            age=user.age,
            gender=user.gender,
            badHabits=user.badHabits,
            pet=user.pet,
            hasRoommate=user.hasRoommate,
            tg_id=user.tg_id
        )
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/by-tg/{tg_id}", response_model=UserResponse)
async def get_user_by_tg(tg_id: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE tg_id = %s", (tg_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            user_id=user["user_id"],
            full_name=user["full_name"],
            bio=user["bio"],
            avatar=user["avatar"],
            age=user["age"],
            gender=user["gender"],
            badHabits=user["bad_habits"],
            pet=user["pets"],
            hasRoommate=user["partner"],
            tg_id=user["tg_id"],
        )
    
    finally:
        cursor.close()
        conn.close()