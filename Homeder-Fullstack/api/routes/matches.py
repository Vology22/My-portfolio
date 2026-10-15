from fastapi import APIRouter, HTTPException
import sys
sys.path.append('..')
from database import get_connection
from pydantic import BaseModel

router = APIRouter()

class MatchCreate(BaseModel):
    sender_id: int
    receiver_id: int

@router.post("/")
async def create_match(match: MatchCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO matches (sender_id, receiver_id) VALUES (%s, %s)",
            (match.sender_id, match.receiver_id)
        )
        conn.commit()
        
        cursor.execute("""
            SELECT COUNT(*) FROM matches 
            WHERE sender_id = %s AND receiver_id = %s
        """, (match.receiver_id, match.sender_id))
        
        is_mutual = cursor.fetchone()[0] > 0
        
        return {"status": "success", "is_mutual": is_mutual}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()