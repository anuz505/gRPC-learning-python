# Integration Guide: Setting Up and Running the Microservices

This guide walks through setting up and running both services locally.

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 14+ (or Docker)
- pip or conda package manager

## 🐳 Quick Setup with Docker

### Using Docker Compose

Create a `docker-compose.yml` in the project root if not already present:

```bash
cd python-grpc-learning/
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Auth Service on port 5501
- FastAPI Service on port 8000

## 🚀 Manual Setup

### Step 1: Install Dependencies

#### Auth Service
```bash
cd server/
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install grpcio==1.62.0 \
            grpcio-tools==1.62.0 \
            sqlalchemy==2.0.23 \
            psycopg2-binary==2.9.9 \
            python-jose[cryptography]==3.3.0 \
            argon2-cffi==23.1.0 \
            pydantic-settings==2.1.0 \
            python-dotenv==1.0.0

# Or use requirements.txt
pip install -r requirements.txt
```

#### FastAPI Service
```bash
cd client/
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install fastapi==0.109.0 \
            uvicorn==0.27.0 \
            sqlalchemy==2.0.23 \
            psycopg2-binary==2.9.9 \
            pydantic-settings==2.1.0 \
            python-dotenv==1.0.0

# Or use requirements.txt
pip install -r requirements.txt
```

### Step 2: Setup Databases

You'll need PostgreSQL running. If using Docker:

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=root \
  -e POSTGRES_USER=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

Create the two databases:

```bash
# Connect to postgres
psql -h localhost -U postgres -c "CREATE DATABASE auth_service;"
psql -h localhost -U postgres -c "CREATE DATABASE fastapi_service;"
```

### Step 3: Generate Proto Files

If proto files have been modified or not yet generated:

```bash
cd server/
python -m grpc_tools.protoc -I./protos \
  --python_out=./gen \
  --pyi_out=./gen \
  --grpc_python_out=./gen \
  ./protos/auth.proto

# Optionally copy to client
cp gen/auth_pb2* ../client/gen/
```

### Step 4: Configure Environment Variables

#### Auth Service (server/.env)
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=auth_service
JWT_SECRET=super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=15
REFRESH_TOKEN_EXPIRES_DAYS=7
LOG_LEVEL=INFO
DEBUG=True
```

#### FastAPI Service (client/.env)
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fastapi_service
JWT_SECRET=super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=15
REFRESH_TOKEN_EXPIRES_DAYS=7
AUTH_SERVICE_HOST=localhost
AUTH_SERVICE_PORT=5501
APP_NAME=FastAPI Service with gRPC Auth
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
DEBUG=True
```

### Step 5: Start Auth Service

```bash
cd server/
# Make sure venv is activated
source venv/bin/activate

python main.py
```

You should see:
```
Creating database tables...
Database tables created
Auth Service gRPC server listening on port 5501
```

### Step 6: Start FastAPI Service (in new terminal)

```bash
cd client/
# Make sure venv is activated
source venv/bin/activate

python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## ✅ Verify Services Are Running

### Check Auth Service
```bash
# The Auth service is gRPC, not HTTP
# You can verify it's listening with:
netstat -tuln | grep 5501
# or
lsof -i :5501
```

### Check FastAPI Service
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "FastAPI service is running..."
}
```

Open the interactive docs:
- FastAPI Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Test the Full Flow

### 1. Register a User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "SecurePassword123"
  }'
```

Response:
```json
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "User registered successfully"
}
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john@example.com",
    "password": "SecurePassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoyMDIzLTAxLTE1VDEwOjQ1OjAwLCJpYXQiOjIwMjMtMDEtMTVUMTA6MzA6MDB9.signature...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MjAyMy0wMS0yMlQxMDozMDowMCwiaWF0IjoyMDIzLTAxLTE1VDEwOjMwOjAwfQ.signature...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

Save the `access_token` for the next step.

### 3. Create a Todo (Using Access Token)
```bash
ACCESS_TOKEN="your_access_token_from_login"

curl -X POST http://localhost:8000/todo/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn gRPC",
    "description": "Master microservices with gRPC"
  }'
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Learn gRPC",
  "description": "Master microservices with gRPC",
  "completed": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 4. Get All Todos
```bash
ACCESS_TOKEN="your_access_token_from_login"

curl -X GET http://localhost:8000/todo/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 5. Refresh Access Token
```bash
REFRESH_TOKEN="your_refresh_token_from_login"

curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

## 🐛 Troubleshooting

### Auth Service Won't Start
```
Error: Could not connect to PostgreSQL
```
- Verify PostgreSQL is running: `docker ps | grep postgres`
- Check database name matches config: `psql -l | grep auth_service`
- Verify connection string in `.env`

### FastAPI Can't Connect to Auth Service
```
Auth gRPC error: Failed to connect to localhost:5501
```
- Verify Auth service is running on port 5501
- Check `AUTH_SERVICE_HOST` and `AUTH_SERVICE_PORT` in FastAPI `.env`
- Ensure both services are on the same network

### Token Verification Fails
```
Token is invalid or expired
```
- Verify `JWT_SECRET` is the same in both services
- Check that access token hasn't expired (default 15 minutes)
- Use refresh token to get a new access token

### Database Migration Issues
```
Column "id" already exists
```
- Delete the database and recreate it: `dropdb auth_service && createdb auth_service`
- Or restart with fresh database

## 📊 Database Structure

### Auth Service (PostgreSQL)
```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL CHECK (length(password) >= 8),
  role VARCHAR(50) DEFAULT 'user' NOT NULL,
  created_at TIMESTAMP DEFAULT now() NOT NULL,
  updated_at TIMESTAMP DEFAULT now() NOT NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### FastAPI Service (PostgreSQL)
```sql
-- Todos table
CREATE TABLE todos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT false NOT NULL,
  created_at TIMESTAMP DEFAULT now() NOT NULL,
  updated_at TIMESTAMP DEFAULT now() NOT NULL
);

CREATE INDEX idx_todos_user_id ON todos(user_id);
```

## 🔗 Service Communication Flow

```
Client (Browser/cURL)
    ├─ HTTP POST /auth/register
    │  └─ FastAPI → gRPC Auth Service → Database
    │
    ├─ HTTP POST /auth/login
    │  └─ FastAPI → gRPC Auth Service → Token Generation
    │
    ├─ HTTP GET /todo/
    │  ├─ Authentication Check (via gRPC)
    │  └─ FastAPI queries its own database
    │
    └─ HTTP POST /auth/refresh
       └─ FastAPI → gRPC Auth Service → New Token
```

## 📝 Logs and Debugging

Both services log important events:

**Auth Service Logs:**
```
User registered successfully: john@example.com
User logged in: john@example.com
Token verified for user: 550e8400-e29b-41d4-a716-446655440000
```

**FastAPI Service Logs:**
```
Connected to Auth service: localhost:5501
User authenticated: 550e8400-e29b-41d4-a716-446655440000
creating todo for user: 550e8400-e29b-41d4-a716-446655440000
```

Enable debug logs by setting `LOG_LEVEL=DEBUG` in `.env`

## 🎯 Next: Production Deployment

For production deployment, consider:
- Use strong JWT_SECRET (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- Use external PostgreSQL database
- Deploy with Docker and Kubernetes
- Use TLS/mTLS for gRPC
- Implement rate limiting and monitoring
- Use API Gateway (Kong, Traefik)
- Add database migrations and versioning

