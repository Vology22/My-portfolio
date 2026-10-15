from fastapi import APIRouter, HTTPException
from typing import Optional, List
import sys
sys.path.append('..')
from database import get_connection
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PropertyCreate(BaseModel):
    owner_id: int
    price: Optional[str] = ""
    title: str
    description: str
    city: Optional[str] = ""
    floor: Optional[str] = ""
    rooms: Optional[str] = ""
    current_tenants: Optional[str] = ""
    potential_tenants: Optional[str] = ""

class PropertyImage(BaseModel):
    img_id: int
    img_url: str
    is_cover: bool

class PropertyResponse(BaseModel):
    prop_id: int
    owner_id: int
    price: Optional[str]
    title: Optional[str]
    description: Optional[str]
    city: Optional[str]
    created_at: Optional[datetime]
    floor: Optional[str]
    rooms: Optional[str]
    current_tenants: Optional[str]
    potential_tenants: Optional[str]
    images: Optional[List[PropertyImage]] = []

@router.post("/", response_model=PropertyResponse)
async def create_property(property: PropertyCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO properties (owner_id, price, title, description, city, floor, rooms, current_tenants, potential_tenants) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (property.owner_id, property.price, property.title, property.description, property.city, property.floor, property.rooms, property.current_tenants, property.potential_tenants)
        )
        prop_id = cursor.lastrowid
        conn.commit()
        
        return PropertyResponse(
            prop_id=prop_id,
            owner_id=property.owner_id,
            price=property.price,
            title=property.title,
            description=property.description,
            city=property.city,
            floor=property.floor,
            rooms=property.rooms,
            current_tenants=property.current_tenants,
            potential_tenants=property.potential_tenants
        )
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/", response_model=List[PropertyResponse])
async def get_properties(limit: int = 50, offset: int = 0):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Получаем свойства
        cursor.execute(
            "SELECT * FROM properties ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset)
        )
        properties = cursor.fetchall()
        
        # Для каждого свойства получаем фотографии
        result = []
        for prop in properties:
            cursor.execute(
                "SELECT img_id, img_url, is_cover FROM prop_image WHERE property = %s ORDER BY is_cover DESC, img_id",
                (prop['prop_id'],)
            )
            images = cursor.fetchall()
            
            result.append(PropertyResponse(
                prop_id=prop['prop_id'],
                owner_id=prop['owner_id'],
                price=prop['price'],
                title=prop['title'],
                description=prop['description'],
                city=prop['city'],
                floor=prop['floor'],
                rooms=prop['rooms'],
                current_tenants=prop['current_tenants'],
                potential_tenants=prop['potential_tenants'],
                created_at=prop['created_at'],
                images=[PropertyImage(**img) for img in images]
            ))
        
        return result
    
    finally:
        cursor.close()
        conn.close()

@router.get("/{prop_id}", response_model=PropertyResponse)
async def get_property(prop_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM properties WHERE prop_id = %s", (prop_id,))
        prop = cursor.fetchone()
        
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        
        cursor.execute(
            "SELECT img_id, img_url, is_cover FROM prop_image WHERE property = %s ORDER BY is_cover DESC, img_id",
            (prop_id,)
        )
        images = cursor.fetchall()
        
        return PropertyResponse(
            prop_id=prop['prop_id'],
            owner_id=prop['owner_id'],
            price=prop['price'],
            title=prop['title'],
            description=prop['description'],
            city=prop['city'],
            floor=prop['floor'],
            rooms=prop['rooms'],
            current_tenants=prop['current_tenants'],
            potential_tenants=prop['potential_tenants'],
            created_at=prop['created_at'],
            images=[PropertyImage(**img) for img in images]
        )
    
    finally:
        cursor.close()
        conn.close()