from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Homeder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    allowed_keys = os.getenv('ALLOWED_SERVICES', '').split(',')
    if not x_api_key or x_api_key not in allowed_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

from routes import users, properties, favorites, matches

app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(properties.router, prefix="/v1/properties", tags=["Properties"])
app.include_router(favorites.router, prefix="/v1/favorites", tags=["Favorites"])
app.include_router(matches.router, prefix="/v1/matches", tags=["Matches"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
