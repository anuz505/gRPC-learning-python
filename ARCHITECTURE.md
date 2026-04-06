# Microservices Architecture: Auth Service + FastAPI

This document describes the refactored microservices architecture with a dedicated gRPC Auth Service and FastAPI API Gateway.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  HTTP Client / Frontend                     │
│                     (e.g., React, cURL)                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP (REST)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           FastAPI Service (API Gateway)                      │
│            Port: 8000                                        │
├─────────────────────────────────────────────────────────────┤
│ HTTP Routes:                                                │
│  • POST   /auth/register   → Register user                 │
│  • POST   /auth/login      → Login (get tokens)            │
│  • POST   /auth/refresh    → Refresh access token          │
│  • GET    /todo/           → List user todos (auth req)    │
│  • POST   /todo/           → Create todo (auth req)        │
│  • PUT    /todo/{id}       → Update todo (auth req)        │
│  • DELETE /todo/{id}       → Delete todo (auth req)        │
│                                                             │
│ Database: PostgreSQL (Todo data only)                      │
│ Auth: Calls gRPC Auth Service for all auth operations     │
└────────────────┬────────────────────────────────────────────┘
                 │ gRPC (secure)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│          gRPC Auth Service (Microservice)                    │
│            Port: 5501                                        │
├─────────────────────────────────────────────────────────────┤
│ gRPC Methods:                                               │
│  • Register(username, email, password)                      │
│    → RegisterResponse(success, user_id, message)           │
│                                                             │
│  • Login(email, password)                                   │
│    → LoginResponse(access_token, refresh_token, expires)  │
│                                                             │
│  • VerifyToken(token)                                       │
│    → VerifyTokenResponse(is_valid, user_id, error)        │
│                                                             │
│  • RefreshToken(refresh_token)                              │
│    → RefreshTokenResponse(access_token, user_id, expires) │
│                                                             │
│ Logic:                                                      │
│  • Hash passwords with Argon2                              │
│  • Generate JWT tokens (access + refresh)                  │
│  • Validate tokens with expiration checking                │
│  • Single source of truth for auth                         │
│                                                             │
│ Database: PostgreSQL (User data only)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Key Design Principles

### 1. **Separation of Concerns**
- **Auth Service**: Owns all authentication logic
  - User registration
  - Password hashing (Argon2)
  - JWT token generation & validation
  - User database
  
- **FastAPI Service**: Owns API layer and todo data
  - HTTP routes
  - Todo management
  - Calls Auth service for user verification
  - Application database

### 2. **Single Source of Truth**
- Auth Service is the **only** place that:
  - Knows the JWT secret
  - Handles password hashing
  - Generates tokens
  - Validates tokens

### 3. **Clean Communication**
- **gRPC between services**: Fast, typed, binary protocol
- **REST HTTP for clients**: Standard, easy to consume
- **No JWT logic in FastAPI**: Delegates to Auth service

### 4. **Database Isolation**
- **Auth Service**: `users` table only
- **FastAPI Service**: `todos` table only
- No cross-service direct database access

## 🚀 Environment Configuration

### Auth Service (.env)
```bash
# PostgreSQL (for users table)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=auth_service

# JWT Configuration
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=15
REFRESH_TOKEN_EXPIRES_DAYS=7

# Server
LOG_LEVEL=INFO
DEBUG=True
```

### FastAPI Service (.env)
```bash
# PostgreSQL (for todos table)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fastapi_service

# JWT Configuration (must match Auth Service!)
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=15
REFRESH_TOKEN_EXPIRES_DAYS=7

# Auth Service gRPC Connection
AUTH_SERVICE_HOST=localhost
AUTH_SERVICE_PORT=5501

# Server
APP_NAME=FastAPI Service with gRPC Auth
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
DEBUG=True
```

## ⚙️ Running the Services

### 1. Start Auth Service (gRPC)
```bash
cd server/
python main.py
# Output: Auth Service gRPC server listening on port 5501
```

### 2. Start FastAPI Service (HTTP)
```bash
cd client/
python main.py
# OR with uvicorn:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Both services should now be running:
- Auth Service: `localhost:5501` (gRPC)
- FastAPI Service: `localhost:8000` (HTTP)

## 📝 API Examples

### Register User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePassword123"
  }'
```

**Response:**
```json
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "User registered successfully"
}
```

### Login User
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john@example.com",
    "password": "SecurePassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

### Create Todo (Requires Auth)
```bash
curl -X POST http://localhost:8000/todo/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs"
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "completed": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Get All Todos (Requires Auth)
```bash
curl -X GET http://localhost:8000/todo/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Refresh Access Token
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

## 🔐 Security Features

### Password Security
- **Argon2**: State-of-the-art password hashing algorithm
- **Memory-hard**: Resistant to GPU attacks
- **Automatic salting**: Each password uniquely salted

### Token Security
- **JWT with expiration**: Access tokens expire in 15 minutes
- **Refresh tokens**: Long-lived (7 days) for getting new access tokens
- **HS256 signature**: HMAC-SHA256 for token verification
- **Token type enforcement**: Access vs refresh token validation

### Database Security
- **User isolation**: Each user only sees their own todos
- **Input validation**: Pydantic schemas validate all input
- **Error handling**: Generic error messages (no info leakage)

## 📂 Project Structure

### Auth Service (server/)
```
server/
├── main.py                          # gRPC server entry point
├── protos/
│   └── auth.proto                   # gRPC service definitions
├── services/
│   └── auth_service.py              # Business logic
├── repositories/
│   └── auth_repo.py                 # Data access layer
├── db/
│   ├── db_models.py                 # SQLAlchemy setup
│   └── auth_models.py               # User model
├── utils/
│   ├── jwt_utils.py                 # JWT token handling
│   └── password_utils.py            # Password hashing
├── core/
│   └── config.py                    # Configuration
└── gen/                             # Generated protobuf files
    ├── auth_pb2.py
    └── auth_pb2_grpc.py
```

### FastAPI Service (client/)
```
client/
├── main.py                          # FastAPI app entry point
├── api/
│   ├── auth_routes.py               # Auth HTTP endpoints
│   └── todo_routes.py               # Todo HTTP endpoints
├── services/
│   ├── auth_grpc_client.py          # gRPC client for Auth service
│   └── todo_service.py              # Todo business logic
├── repositories/
│   └── todo_repo.py                 # Todo data access
├── dependencies/
│   └── auth_dependency.py           # get_current_user dependency
├── db/
│   ├── db_models.py                 # SQLAlchemy setup
│   └── todo_models.py               # Todo model
├── schema/
│   └── *.py                         # Pydantic schemas
├── core/
│   └── config.py                    # Configuration
└── gen/                             # Generated protobuf files
    ├── auth_pb2.py
    └── auth_pb2_grpc.py
```

## 🔄 Data Flow Example: User Login

```
1. Client POST /auth/login
        ↓
2. FastAPI receives request (auth_routes.py)
        ↓
3. FastAPI calls AuthGrpcClient.login()
        ↓
4. gRPC client sends LoginRequest to Auth service
        ↓
5. Auth Service receives request (main.py)
        ↓
6. Auth Service calls auth_service.login():
   - Lookup user by email (repository)
   - Verify password (PasswordManager)
   - Generate tokens (JWTHandler)
        ↓
7. Auth Service returns LoginResponse
        ↓
8. FastAPI receives response
        ↓
9. FastAPI returns tokens to client
```

## 🔄 Data Flow Example: Access Protected Resource

```
1. Client GET /todo/ with Authorization header
        ↓
2. FastAPI receives request (todo_routes.py)
        ↓
3. FastAPI calls get_current_user dependency
        ↓
4. Dependency calls AuthGrpcClient.verify_token()
        ↓
5. gRPC client sends VerifyTokenRequest to Auth service
        ↓
6. Auth Service receives request (main.py)
        ↓
7. Auth Service calls auth_service.verify_token():
   - Decode JWT (JWTHandler)
   - Extract user_id
   - Verify user still exists (repository)
        ↓
8. Auth Service returns VerifyTokenResponse
        ↓
9. FastAPI receives user_id
        ↓
10. FastAPI calls get_all_todos(user_id)
        ↓
11. FastAPI returns user's todos only
```

## ✅ Requirements Met

- ✓ Auth Service as independent gRPC microservice
- ✓ Handles registration, login, token verification, token refresh
- ✓ Argon2 password hashing
- ✓ JWT token generation and validation
- ✓ FastAPI HTTP API Gateway
- ✓ gRPC inter-service communication with Protocol Buffers
- ✓ SQLAlchemy for database access
- ✓ Pydantic for schema validation
- ✓ Clean layering: routes → services → repositories
- ✓ Dependency injection for auth flow
- ✓ Environment-based configuration
- ✓ Production-ready code structure
- ✓ No auth logic duplication
- ✓ Auth Service = single source of truth

## 📦 Dependencies

### Auth Service (server/requirements.txt)
```
grpcio==1.62.0
grpcio-tools==1.62.0
fastapi==0.109.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
argon2-cffi==23.1.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

### FastAPI Service (client/requirements.txt)
```
grpcio==1.62.0
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

## 🛠️ Generating Proto Files

When you modify `.proto` files, regenerate the Python code:

```bash
# From server directory
python -m grpc_tools.protoc -I./protos \
  --python_out=./gen \
  --pyi_out=./gen \
  --grpc_python_out=./gen \
  ./protos/auth.proto

# Copy to client
cp server/gen/auth_pb2* client/gen/
```

## 🤝 Next Steps & Enhancements

- Add database connection pooling for production
- Implement service-to-service authentication with mTLS
- Add gRPC interceptors for logging and metrics
- Implement Redis for token blacklisting
- Add rate limiting on auth endpoints
- Implement API key authentication for service-to-service calls
- Add database migrations with Alembic
- Implement comprehensive logging with correlation IDs
- Add unit tests for all services
- Use Docker Compose for local development

