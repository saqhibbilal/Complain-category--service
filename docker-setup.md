# Docker Setup Guide

## Prerequisites

- **Docker Desktop** installed on Windows
  - Download from: https://www.docker.com/products/docker-desktop/
  - Make sure Docker Desktop is running before proceeding

## Quick Start

### 1. Start PostgreSQL with pgvector

```powershell
# Navigate to project directory
cd C:\Users\USER\Desktop\Category-rag

# Start PostgreSQL container
docker-compose up -d
```

This will:
- Pull the `pgvector/pgvector:pg16` image (PostgreSQL 16 with pgvector)
- Create a container named `complaints_db`
- Set up database `complaints_db` with user `postgres` / password `postgres`
- Expose PostgreSQL on port `5432`

### 2. Verify PostgreSQL is running

```powershell
# Check container status
docker-compose ps

# Check logs
docker-compose logs postgres

# Test connection (if you have psql installed)
psql -h localhost -U postgres -d complaints_db
# Password: postgres
```

### 3. Verify pgvector extension

```powershell
# Connect to PostgreSQL
docker exec -it complaints_db psql -U postgres -d complaints_db

# Inside psql, run:
CREATE EXTENSION IF NOT EXISTS vector;

# Verify it's installed
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
# Should show: vector | 0.5.0 (or similar version)

# Exit psql
\q
```

### 4. Update your .env file

Make sure your `.env` file has:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/complaints_db
```

## Useful Docker Commands

### Stop PostgreSQL
```powershell
docker-compose down
```

### Stop and remove volumes (⚠️ deletes all data)
```powershell
docker-compose down -v
```

### View logs
```powershell
docker-compose logs -f postgres
```

### Restart PostgreSQL
```powershell
docker-compose restart postgres
```

### Access PostgreSQL shell directly
```powershell
docker exec -it complaints_db psql -U postgres -d complaints_db
```

### Backup database
```powershell
docker exec complaints_db pg_dump -U postgres complaints_db > backup.sql
```

### Restore database
```powershell
docker exec -i complaints_db psql -U postgres complaints_db < backup.sql
```

## Troubleshooting

### Port 5432 already in use
If you have a local PostgreSQL installation using port 5432:
1. Stop local PostgreSQL service: `Get-Service postgresql* | Stop-Service`
2. Or change port in docker-compose.yml: `"5433:5432"` and update DATABASE_URL

### Container won't start
```powershell
# Check logs
docker-compose logs postgres

# Remove and recreate
docker-compose down -v
docker-compose up -d
```

### Reset everything
```powershell
# Stop and remove everything
docker-compose down -v

# Remove image (optional)
docker rmi pgvector/pgvector:pg16

# Start fresh
docker-compose up -d
```

## Notes

- Data persists in Docker volume `postgres_data` even if container is stopped
- To completely reset: `docker-compose down -v` (⚠️ deletes all data)
- Default credentials: `postgres` / `postgres` (change in docker-compose.yml for production)
