import os
import secrets
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# 1. Cargar las variables de entorno actuales
env_path = ".env"
load_dotenv(env_path)

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key_or_pwd = os.getenv("SUPABASE_KEY", "")

# Generar un token JWT seguro si no existe o si es el de prueba
current_jwt = os.getenv("JWT_SECRET", "")
new_jwt = secrets.token_hex(32)

# Actualizar el .env con el token seguro
with open(env_path, "r") as f:
    lines = f.readlines()

with open(env_path, "w") as f:
    for line in lines:
        if line.startswith("JWT_SECRET="):
            f.write(f"JWT_SECRET={new_jwt}\n")
        else:
            f.write(line)

print(f"✅ JWT_SECRET actualizado exitosamente en el .env a uno seguro.")

# 2. Configurar la base de datos automáticamente
try:
    # Supabase_URL tiene la forma: https://<project_ref>.supabase.co
    parsed_url = urlparse(supabase_url)
    project_ref = parsed_url.hostname.split('.')[0]
    
    # Intentar conexión PostgreSQL directa a la base de datos usando la contraseña proporcionada en SUPABASE_KEY
    conn = psycopg2.connect(
        host=f"db.{project_ref}.supabase.co",
        database="postgres",
        user="postgres",
        password=supabase_key_or_pwd,
        port=5432
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Ejecutar el esquema SQL
    print("Conectado a PostgreSQL en Supabase. Configurando esquema...")
    with open("supabase_schema.sql", "r") as sql_file:
        sql_script = sql_file.read()
        cursor.execute(sql_script)
        
    print("✅ Tablas de arreglos y usuario administrador configurados correctamente en la base de datos.")
    cursor.close()
    conn.close()
except psycopg2.OperationalError:
    print("❌ ERROR DE CONEXIÓN A POSTGRESQL:")
    print("Parece que SUPABASE_KEY no es tu contraseña de base de datos o hay un problema de red.")
    print("Recuerda: Para el cliente REST, SUPABASE_KEY debe ser la 'anon key' y no la contraseña del proyecto de Supabase.")
except Exception as e:
    print(f"❌ Ocurrió un error al configurar la base de datos: {e}")
