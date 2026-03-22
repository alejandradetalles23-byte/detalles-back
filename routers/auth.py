import random
import string
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from auth import verify_password, create_access_token, get_current_user, hash_password
from database import supabase
from email_utils import send_reset_code_email, send_email_change_code

router = APIRouter(prefix="/auth", tags=["Auth"])

def generate_code() -> str:
    """Genera un código numérico de 6 dígitos."""
    return "".join(random.choices(string.digits, k=6))

@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends()):
    if not supabase:
        raise HTTPException(status_code=500, detail="La base de datos no está configurada")

    try:
        res = supabase.table("users").select("*").eq("username", request.username).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a Supabase. Detalles: {str(e)}")
        
    data = res.data
    if not data or not verify_password(request.password, data[0]["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(data={"sub": request.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/request-reset")
async def request_password_reset(username: str):
    """Genera un código de 6 dígitos, lo guarda en la DB y lo envía por correo."""
    res = supabase.table("users").select("*").eq("username", username).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user = res.data[0]
    if not user.get("email"):
        raise HTTPException(status_code=400, detail="El usuario no tiene un correo configurado")

    code = generate_code()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()

    # Guardar código en la DB
    supabase.table("users").update({
        "reset_code": code,
        "reset_code_expires_at": expires_at
    }).eq("username", username).execute()

    # Enviar correo real
    try:
        await send_reset_code_email(user["email"], code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando correo: {str(e)}")

    return {"message": "Código de recuperación enviado al correo registrado"}

@router.post("/reset-password")
def reset_password(username: str, code: str, new_password: str):
    """Verifica el código y actualiza la contraseña."""
    res = supabase.table("users").select("*").eq("username", username).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user = res.data[0]
    
    # Validaciones de seguridad
    if user.get("reset_code") != code:
        raise HTTPException(status_code=400, detail="Código inválido")

    # Verificar expiración (si guardas con ISO format en su lugar usa fromisoformat)
    # Supabase guarda fechas nativas como strings en ISO
    expires = datetime.fromisoformat(user["reset_code_expires_at"])
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=400, detail="El código ha expirado")

    new_hash = hash_password(new_password)
    supabase.table("users").update({
        "password_hash": new_hash,
        "reset_code": None, # Limpiar código
        "reset_code_expires_at": None
    }).eq("username", username).execute()

    return {"message": "Contraseña restablecida exitosamente"}

@router.post("/change-password")
def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    username: str = Depends(get_current_user)
):
    res = supabase.table("users").select("*").eq("username", username).execute()
    data = res.data

    if not data or not verify_password(current_password, data[0]["password_hash"]):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")

    new_hash = hash_password(new_password)
    supabase.table("users").update({"password_hash": new_hash}).eq("username", username).execute()

    return {"message": "Contraseña actualizada exitosamente"}

@router.post("/request-email-change")
async def request_email_change(
    new_email: str = Form(...),
    username: str = Depends(get_current_user)
):
    """
    Inicia el proceso de cambio de email enviando un código de verificación 
    al NUEVO correo proporcionado.
    """
    code = generate_code()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()

    # Guardamos el código temporalmente en la base de datos
    supabase.table("users").update({
        "reset_code": code,
        "reset_code_expires_at": expires_at
    }).eq("username", username).execute()

    try:
        # Enviamos el código al correo NUEVO para verificar que el usuario tenga acceso
        await send_email_change_code(new_email, code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando correo: {str(e)}")

    return {"message": f"Código de verificación enviado a {new_email}"}

@router.post("/confirm-email-change")
async def confirm_email_change(
    new_email: str = Form(...),
    code: str = Form(...),
    username: str = Depends(get_current_user)
):
    """
    Valida el código enviado al nuevo email y actualiza la cuenta del usuario.
    """
    res = supabase.table("users").select("*").eq("username", username).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user = res.data[0]

    # Validaciones de seguridad
    if user.get("reset_code") != code:
        raise HTTPException(status_code=400, detail="Código de verificación incorrecto")

    expires = datetime.fromisoformat(user["reset_code_expires_at"])
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=400, detail="El código ha expirado")

    # Si todo es correcto, actualizamos el campo email del usuario
    supabase.table("users").update({
        "email": new_email,
        "reset_code": None, # Limpiamos el código
        "reset_code_expires_at": None
    }).eq("username", username).execute()

    return {"message": "Tu correo electrónico ha sido actualizado correctamente"}

