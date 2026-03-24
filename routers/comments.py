from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from database import supabase
from auth import get_current_user

router = APIRouter(prefix="/arrangements", tags=["Comments"])

class CommentCreate(BaseModel):
    author_name: str
    content: str

class CommentOut(BaseModel):
    id: int
    arrangement_id: int
    author_name: str
    content: str
    is_approved: bool
    created_at: str

@router.get("/{arrangement_id}/comments", response_model=List[CommentOut])
def get_comments(arrangement_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    
    # Solo retornamos comentarios aprobados para el frontend público
    res = supabase.table("comments").select("*").eq("arrangement_id", arrangement_id).eq("is_approved", True).order("created_at", desc=False).execute()
    return res.data

@router.post("/{arrangement_id}/comments", response_model=CommentOut)
def create_comment(arrangement_id: int, comment: CommentCreate):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    
    # Verificar que el arreglo existe
    res_arr = supabase.table("arrangements").select("id").eq("id", arrangement_id).execute()
    if not res_arr.data:
        raise HTTPException(status_code=404, detail="Arreglo no encontrado")

    new_comment = {
        "arrangement_id": arrangement_id,
        "author_name": comment.author_name,
        "content": comment.content,
        "is_approved": True # Por defecto aprobados, el admin puede cambiarlo después si se habilita la función
    }
    
    try:
        res = supabase.table("comments").insert(new_comment).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar comentario: {str(e)}")
        
    raise HTTPException(status_code=500, detail="Error desconocido guardando el comentario")

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, username: str = Depends(get_current_user)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    
    res = supabase.table("comments").delete().eq("id", comment_id).execute()
    if res.data:
        return {"message": "Comentario eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Error o comentario no encontrado")
