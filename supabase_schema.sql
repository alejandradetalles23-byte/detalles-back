-- Este script debe ser ejecutado en el SQL Editor de tu proyecto de Supabase

-- 1. Crear tabla de usuarios (para el admin)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Insertar usuario admin por defecto con la contraseña 'admin123'
-- Nota: La contraseña fue generada mediante bcrypt para 'admin123'
INSERT INTO users (username, password_hash)
VALUES ('admin', '$2b$12$yPyUItUl4Gu.9VZYMeKIhO.lk011mATpgbpOt0AV.pVPCe6x5rYqu')
ON CONFLICT (username) DO NOTHING;

-- 3. Crear tabla de arreglos florales
CREATE TABLE IF NOT EXISTS arrangements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    photo1 VARCHAR(255),
    photo2 VARCHAR(255),
    photo3 VARCHAR(255),
    photo4 VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Habilitar RLS (Row Level Security) (Opcional, pero recomendado en Supabase)
-- En este caso se permitirá el acceso a anon en lectura y escritura temporalmente
-- Si quieres restringir, cambia true por false y maneja JWT con supabase_auth.
ALTER TABLE arrangements ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public select" ON arrangements FOR SELECT USING (true);
CREATE POLICY "Public insert" ON arrangements FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update" ON arrangements FOR UPDATE USING (true);
CREATE POLICY "Public delete" ON arrangements FOR DELETE USING (true);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public select users" ON users FOR SELECT USING (true);
CREATE POLICY "Public update users" ON users FOR UPDATE USING (true);
