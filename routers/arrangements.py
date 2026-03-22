from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from models import ArrangementOut
from cloudinary_utils import upload_image
from auth import get_current_user
from database import supabase

router = APIRouter(prefix="/arrangements", tags=["Arrangements"])

def format_arrangement(data: dict) -> dict:
    photos = [data.get(f"photo{i}") for i in range(1, 5) if data.get(f"photo{i}")]
    return {
        "id": data["id"],
        "title": data["title"],
        "description": data["description"],
        "price": data["price"],
        "category_id": data.get("category_id"),
        "views": data.get("views", 0),
        "photos": photos,
        "created_at": data["created_at"]
    }

@router.get("/", response_model=List[ArrangementOut])
def get_arrangements(category_id: Optional[int] = None):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    
    query = supabase.table("arrangements").select("*")
    if category_id:
        query = query.eq("category_id", category_id)
    
    res = query.order("created_at", desc=True).execute()
    return [format_arrangement(item) for item in res.data]

@router.get("/{arrangement_id}", response_model=ArrangementOut)
def get_arrangement(arrangement_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    
    res = supabase.table("arrangements").select("*").eq("id", arrangement_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Arreglo no encontrado")
    
    return format_arrangement(res.data[0])

@router.post("/", response_model=ArrangementOut)
async def create_arrangement(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category_id: Optional[int] = Form(None),
    photo1: Optional[UploadFile] = File(None),
    photo2: Optional[UploadFile] = File(None),
    photo3: Optional[UploadFile] = File(None),
    photo4: Optional[UploadFile] = File(None),
    username: str = Depends(get_current_user)
):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
        
    new_data = {
        "title": title,
        "description": description,
        "price": price,
        "category_id": category_id
    }
    
    for i, photo in enumerate([photo1, photo2, photo3, photo4], 1):
        if photo and photo.filename:
            url = await upload_image(photo)
            new_data[f"photo{i}"] = url
        else:
            new_data[f"photo{i}"] = None

    try:
        res = supabase.table("arrangements").insert(new_data).execute()
        if res.data:
            return format_arrangement(res.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Supabase: {str(e)}")
        
    raise HTTPException(status_code=500, detail="Error al crear el arreglo")

@router.put("/{arrangement_id}", response_model=ArrangementOut)
async def update_arrangement(
    arrangement_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category_id: Optional[int] = Form(None),
    photo1: Optional[UploadFile] = File(None),
    photo2: Optional[UploadFile] = File(None),
    photo3: Optional[UploadFile] = File(None),
    photo4: Optional[UploadFile] = File(None),
    username: str = Depends(get_current_user)
):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
        
    res = supabase.table("arrangements").select("*").eq("id", arrangement_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Arreglo no encontrado")
    
    update_data = {}
    if title is not None: update_data["title"] = title
    if description is not None: update_data["description"] = description
    if price is not None: update_data["price"] = price
    if category_id is not None: update_data["category_id"] = category_id
    
    for i, photo in enumerate([photo1, photo2, photo3, photo4], 1):
        if photo and photo.filename:
            url = await upload_image(photo)
            update_data[f"photo{i}"] = url

    if not update_data:
        return format_arrangement(res.data[0])
        
    try:
        updated = supabase.table("arrangements").update(update_data).eq("id", arrangement_id).execute()
        if updated.data:
            return format_arrangement(updated.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Supabase: {str(e)}")
        
    raise HTTPException(status_code=500, detail="Error actualizando registro")

@router.delete("/{arrangement_id}")
def delete_arrangement(arrangement_id: int, username: str = Depends(get_current_user)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    
    deleted = supabase.table("arrangements").delete().eq("id", arrangement_id).execute()
    if deleted.data:
        return {"message": "Arreglo eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Error o no encontrado")
