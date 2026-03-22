from fastapi import APIRouter, HTTPException, Depends
from database import supabase
from auth import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/stats", tags=["Stats"])

class StatLine(BaseModel):
    name: str
    count: int

class StatsOut(BaseModel):
    completed_sales: int
    cancelled_sales: int
    most_viewed: List[StatLine]
    most_liked: List[StatLine]
    most_ordered: List[StatLine]

@router.get("/", response_model=StatsOut)
def get_stats(username: str = Depends(get_current_user)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")
    
    # 1. Ventas Completadas (status 'completed')
    res_completed = supabase.table("orders").select("*", count="exact").eq("status", "completed").execute()
    completed = res_completed.count if res_completed.count is not None else len(res_completed.data)
    
    # 2. Ventas Canceladas (status 'cancelled')
    res_cancelled = supabase.table("orders").select("*", count="exact").eq("status", "cancelled").execute()
    cancelled = res_cancelled.count if res_cancelled.count is not None else len(res_cancelled.data)
    
    # 3. Productos más vistos (views top 5)
    res_views = supabase.table("arrangements").select("title, views").order("views", desc=True).limit(5).execute()
    most_viewed = [{"name": item["title"], "count": item["views"]} for item in res_views.data]
    
    # 4. Productos más gustados (likes top 5)
    res_likes = supabase.table("arrangements").select("title, likes").order("likes", desc=True).limit(5).execute()
    most_liked = [{"name": item["title"], "count": item["likes"]} for item in res_likes.data]
    
    return {
        "completed_sales": completed,
        "cancelled_sales": cancelled,
        "most_viewed": most_viewed,
        "most_liked": most_liked,
        "most_ordered": [] # Placeholder for now
    }

@router.post("/view/{arrangement_id}")
def increment_view(arrangement_id: int):
    if not supabase:
        return {"error": "DB no set"}
    
    # RPC or direct update if we have the current view count.
    # Simpler: just update the views counter
    res_arr = supabase.table("arrangements").select("views").eq("id", arrangement_id).execute()
    if res_arr.data:
        curr = res_arr.data[0].get("views", 0)
        supabase.table("arrangements").update({"views": curr + 1}).eq("id", arrangement_id).execute()
        return {"views": curr + 1}
    return {"message": "Not found"}

@router.post("/like/{arrangement_id}")
def increment_like(arrangement_id: int):
    if not supabase:
        return {"error": "DB no set"}
    
    res_arr = supabase.table("arrangements").select("likes").eq("id", arrangement_id).execute()
    if res_arr.data:
        curr = res_arr.data[0].get("likes", 0)
        supabase.table("arrangements").update({"likes": curr + 1}).eq("id", arrangement_id).execute()
        return {"likes": curr + 1}
    return {"message": "Not found"}
