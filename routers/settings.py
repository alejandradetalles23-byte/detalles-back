from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
from database import supabase
from auth import get_current_user
from cloudinary_utils import upload_image
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingsOut(BaseModel):
    whatsapp_number: str
    about_us: str
    logo_url: Optional[str] = None
    icon_url: Optional[str] = None
    admin_name: Optional[str] = "Administrador"
    admin_avatar_url: Optional[str] = None
    address: Optional[str] = "Edo. Aragua, Venezuela"
    maps_url: Optional[str] = None
    instagram_url: Optional[str] = None
    footer_text: Optional[str] = None

@router.get("/", response_model=SettingsOut)
def get_settings():
    if not supabase:
        raise HTTPException(status_code=500, detail="DB not set")
    res = supabase.table("site_settings").select("*").execute()
    data = {item["key"]: item["value"] for item in res.data}
    return {
        "whatsapp_number": data.get("whatsapp_number", ""),
        "about_us": data.get("about_us", ""),
        "logo_url": data.get("logo_url"),
        "icon_url": data.get("icon_url"),
        "admin_name": data.get("admin_name", "Administrador"),
        "admin_avatar_url": data.get("admin_avatar_url"),
        "address": data.get("address", "Edo. Aragua, Venezuela"),
        "maps_url": data.get("maps_url"),
        "instagram_url": data.get("instagram_url"),
        "footer_text": data.get("footer_text")
    }

@router.post("/")
async def update_settings(
    whatsapp_number: Optional[str] = Form(None),
    about_us: Optional[str] = Form(None),
    admin_name: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    maps_url: Optional[str] = Form(None),
    instagram_url: Optional[str] = Form(None),
    footer_text: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    avatar: Optional[UploadFile] = File(None),
    username: str = Depends(get_current_user)
):
    if not supabase:
        raise HTTPException(status_code=500, detail="DB not set")
    
    updates = []
    if whatsapp_number is not None:
        updates.append({"key": "whatsapp_number", "value": whatsapp_number})
    if about_us is not None:
        updates.append({"key": "about_us", "value": about_us})
    if admin_name is not None:
        updates.append({"key": "admin_name", "value": admin_name})
    if address is not None:
        updates.append({"key": "address", "value": address})
    if maps_url is not None:
        updates.append({"key": "maps_url", "value": maps_url})
    if instagram_url is not None:
        updates.append({"key": "instagram_url", "value": instagram_url})
    if footer_text is not None:
        updates.append({"key": "footer_text", "value": footer_text})
    
    if logo and logo.filename:
        logo_url = await upload_image(logo)
        updates.append({"key": "logo_url", "value": logo_url})
    
    if avatar and avatar.filename:
        avatar_url = await upload_image(avatar)
        updates.append({"key": "admin_avatar_url", "value": avatar_url})

    for update in updates:
        supabase.table("site_settings").upsert(update, on_conflict="key").execute()
    
    return {"message": "Configuración actualizada"}
