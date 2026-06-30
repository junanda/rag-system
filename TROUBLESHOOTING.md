# Troubleshooting Guide

## Frontend TypeScript Errors

### Symptom
```
Cannot find module 'react' or its corresponding type declarations.
Cannot find module 'axios' or its corresponding type declarations.
Cannot find module '@tanstack/react-query' or its corresponding type declarations.
```

### Cause
`node_modules` is not installed, or dependencies are missing.

### Solution

#### Using Docker (recommended)
```bash
# The Docker container installs dependencies automatically
docker-compose up --build
```

#### Local development
```bash
cd frontend
npm install
npm run dev
```

---

## Backend Python Errors

### Symptom
```
ModuleNotFoundError: No module named 'numpy'
ModuleNotFoundError: No module named 'docling'
```

### Solution

#### Using Docker (recommended)
```bash
docker-compose up --build
```

#### Local development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Common Errors

### 1. "Cannot connect to database"

**Cause**: PostgreSQL is not running, or the connection settings are incorrect.

**Solution**:
```bash
# Start PostgreSQL with Docker
docker-compose up postgres -d

# Verify the connection
docker-compose exec postgres psql -U funduser -d funddb
```

### 2. "OpenAI API key not found"

**Cause**: The API key is not set in the `.env` file.

**Solution**:
```bash
# Create the .env file
cp .env.example .env

# Edit .env and add your API key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. "Port already in use"

**Cause**: The port is already in use by another process.

**Solution**:
```bash
# Find the process using the port (Mac/Linux)
lsof -i :8000  # backend
lsof -i :3000  # frontend

# Kill the process
kill -9 <PID>

# Or restart the Docker containers
docker-compose down
docker-compose up
```

### 4. Lint warnings can be ignored

The project runs correctly even with lint warnings. They typically occur because:

- **Frontend**: TypeScript can't resolve modules before `npm install` is run.
- **Backend**: Imports intentionally ignored with `# noqa` comments (e.g. SQLAlchemy model registration).

---

## Verifying the Setup

### Check that all services are running

```bash
# Service status
docker-compose ps

# View logs
docker-compose logs -f

# Health checks
curl http://localhost:8000/health
curl http://localhost:3000
```

### Example of healthy output
```
NAME                COMMAND                  SERVICE             STATUS
fund-backend        "sh -c 'python app/d…"   backend             Up
fund-frontend       "npm run dev"            frontend            Up
fund-postgres       "docker-entrypoint.s…"   postgres            Up (healthy)
fund-redis          "docker-entrypoint.s…"   redis               Up (healthy)
```

---

## Further Help

If the problem persists:

1. **Check logs**: `docker-compose logs [service-name]`
2. **Restart a container**: `docker-compose restart [service-name]`
3. **Full rebuild**: `docker-compose down && docker-compose up --build`
4. **Remove volumes** (warning: data loss): `docker-compose down -v`

---

## Confirming It Works

When the project runs correctly:

✅ Frontend: http://localhost:3000 is reachable
✅ Backend API: http://localhost:8000/docs is reachable
✅ Health check: `curl http://localhost:8000/health` responds OK
✅ Database: PostgreSQL connection works
✅ Redis: Redis connection works

Once all services are healthy, you can test the document upload and chat features.
</content>
