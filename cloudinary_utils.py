import os
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.getenv("CLOUDINARY_API_KEY", ""),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
    secure=True
)

async def upload_image(file: UploadFile, folder: str = "arreglos_florales") -> str:
    """Sube una imagen a Cloudinary y devuelve la URL segura"""
    try:
        # FastAPI's UploadFile reads asynchronously. Cloudinary needs a file-like object or bytes
        contents = await file.read()
        response = cloudinary.uploader.upload(contents, folder=folder)
        return response.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo imagen a Cloudinary: {str(e)}")
