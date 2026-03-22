from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, arrangements, categories, stats, settings

app = FastAPI(title="API Alejandra Detalles")

# Configurar CORS (ajustar origins según sea necesario)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://alejandra-detalles.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(arrangements.router)
app.include_router(categories.router)
app.include_router(stats.router)
app.include_router(settings.router)

@app.get("/")
def root():
    return {"message": "API de Arreglos Florales iniciada exitosamente. Usa /docs para ver la documentación."}
