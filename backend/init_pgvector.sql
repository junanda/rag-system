-- init_pgvector.sql
-- Skrip inisialisasi untuk PostgreSQL + pgvector
-- File ini akan dijalankan otomatis saat PostgreSQL pertama kali dibuat oleh Docker

-- Buat ekstensi vector jika belum ada
CREATE EXTENSION IF NOT EXISTS vector;

-- Contoh: Buat tabel sederhana untuk menyimpan chunk teks dan vektornya (opsional)
-- CREATE TABLE document_chunks (
--     id SERIAL PRIMARY KEY,
--     source TEXT NOT NULL,
--     text TEXT NOT NULL,
--     embedding vector(384) -- Sesuaikan dimensi dengan model embedding Anda (misalnya 384 dari all-MiniLM-L6-v2)
-- );

-- Cek versi pgvector untuk verifikasi
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
