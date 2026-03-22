from fastapi import APIRouter, HTTPException, Depends, Form
from typing import List, Optional
from database import supabase
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["Categories"])

class CategoryBase(BaseModel):
    name: str

class CategoryOut(CategoryBase):
    id: int

@router.get("/", response_model=List[CategoryOut])
def get_categories():
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    res = supabase.table("categories").select("*").execute()
    return res.data

@router.post("/", response_model=CategoryOut)
def create_category(category: CategoryBase, username: str = Depends(get_current_user)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    res = supabase.table("categories").insert({"name": category.name}).execute()
    if res.data:
        return res.data[0]
    raise HTTPException(status_code=500, detail="Error al crear categoría")

@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, category: CategoryBase, username: str = Depends(get_current_user)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    res = supabase.table("categories").update({"name": category.name}).eq("id", category_id).execute()
    if res.data:
        return res.data[0]
    raise HTTPException(status_code=404, detail="Categoría no encontrada")

@router.delete("/{category_id}")
def delete_category(category_id: int, username: str = Depends(get_current_user)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    res = supabase.table("categories").delete().eq("id", category_id).execute()
    if res.data:
        return {"message": "Categoría eliminada"}
    raise HTTPException(status_code=404, detail="Categoría no encontrada")
