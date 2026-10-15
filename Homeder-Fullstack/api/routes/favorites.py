from fastapi import APIRouter, HTTPException, Path
import sys
sys.path.append('..')
from database import get_connection
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class FavoriteCreate(BaseModel):
    user_id: int
    prop_id: int

class PropertyImage(BaseModel):
    img_id: int
    img_url: str
    is_cover: bool

class FavoriteProperty(BaseModel):
    prop_id: int
    owner_id: int
    price: Optional[str]
    title: Optional[str]
    description: Optional[str]
    city: Optional[str]
    floor: Optional[str]
    rooms: Optional[str]
    current_tenants: Optional[str]
    potential_tenants: Optional[str]
    images: Optional[List[PropertyImage]] = []

class FavoriteResponse(BaseModel):
    user_id: int
    prop_id: int
    property: FavoriteProperty

@router.post("/")
async def add_to_favorites(fav: FavoriteCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM favorites WHERE user_id = %s AND prop_id = %s", 
            (fav.user_id, fav.prop_id)
        )
        if cursor.fetchone()[0] > 0:
            return {"status": "already_exists", "message": "Already in favorites"}
        
        cursor.execute(
            "INSERT INTO favorites (user_id, prop_id) VALUES (%s, %s)",
            (fav.user_id, fav.prop_id)
        )
        conn.commit()
        return {"status": "success", "message": "Added to favorites"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.delete("/{user_id}/{prop_id}")
async def remove_from_favorites(
    user_id: int = Path(..., description="User ID"),
    prop_id: int = Path(..., description="Property ID")
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM favorites WHERE user_id = %s AND prop_id = %s",
            (user_id, prop_id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        conn.commit()
        return {"status": "success", "message": "Removed from favorites"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/user/{user_id}")
async def get_user_favorites(user_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT f.user_id, f.prop_id, 
                   p.title, p.price, p.description, p.city, p.owner_id, p.floor, p.rooms, p.current_tenants, p.potential_tenants
            FROM favorites f
            JOIN properties p ON f.prop_id = p.prop_id
            WHERE f.user_id = %s
            ORDER BY p.created_at DESC
        """, (user_id,))
        favorites = cursor.fetchall()
        
        result = []
        for fav in favorites:
            cursor.execute(
                "SELECT img_id, img_url, is_cover FROM prop_image WHERE property = %s ORDER BY is_cover DESC, img_id",
                (fav['prop_id'],)
            )
            images = cursor.fetchall()
            
            result.append(FavoriteResponse(
                user_id=fav['user_id'],
                prop_id=fav['prop_id'],
                property=FavoriteProperty(
                    prop_id=fav['prop_id'],
                    owner_id=fav['owner_id'],
                    price=fav['price'],
                    title=fav['title'],
                    description=fav['description'],
                    city=fav['city'],
                    floor=fav['floor'],
                    rooms=fav['rooms'],
                    current_tenants=fav['current_tenants'],
                    potential_tenants=fav['potential_tenants'],
                    images=[PropertyImage(**img) for img in images]
                )
            ))
        
        return {"count": len(result), "favorites": result}
    
    finally:
        cursor.close()
        conn.close()