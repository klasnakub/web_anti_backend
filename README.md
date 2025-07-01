# FastAPI User Login System

A production-ready FastAPI backend for user authentication with Google BigQuery integration, bcrypt password hashing, and JWT token authentication.

## Features

- 🔐 Secure user authentication with bcrypt password hashing
- 🗄️ Google BigQuery integration for user data storage
- 🎫 JWT token-based authentication
- 🐳 Docker containerization ready for Google Cloud Run
- 📊 Automatic last login tracking
- 🏥 Health check endpoint
- 🔒 Role-based access control

## Prerequisites

- Python 3.8+
- Google Cloud Project with BigQuery enabled
- Google Service Account with BigQuery permissions
- Docker (for containerization)

## BigQuery Table Schema

The application expects a BigQuery table with the following schema:

```sql
CREATE TABLE `practise-bi.user.users` (
  user_id STRING,
  username STRING,
  email STRING,
  password_hash STRING,
  role STRING,
  is_active BOOLEAN,
  created_at TIMESTAMP,
  last_login TIMESTAMP
);
```

## Local Development Setup

1. **Clone the repository and navigate to the project directory**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your JWT secret
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8080 --reload
   ```

5. **Access the API documentation**
   - Swagger UI: http://localhost:8080/docs
   - ReDoc: http://localhost:8080/redoc

## API Endpoints

### POST /login
Authenticate a user and return a JWT token.

**Request Body:**
```json
{
  "username": "user123",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "user_123",
  "username": "user123",
  "email": "user@example.com",
  "role": "user"
}
```

### GET /me
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "user_id": "user_123",
  "username": "user123",
  "email": "user@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "last_login": "2024-01-01T12:00:00"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Docker Deployment

### Building the Docker Image

```bash
docker build -t fastapi-login-system .
```

### Running Locally with Docker

```bash
docker run -p 8080:8080 \
  -e JWT_SECRET=your-secret-key \
  fastapi-login-system
```

## Google Cloud Run Deployment

### 1. Build and Push to Google Container Registry

```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Build the image
docker build -t gcr.io/$PROJECT_ID/fastapi-login-system .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/fastapi-login-system
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy fastapi-login-system \
  --image gcr.io/$PROJECT_ID/fastapi-login-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars JWT_SECRET=your-super-secret-jwt-key
```

### 3. Alternative: Deploy using Cloud Build

Create a `cloudbuild.yaml` file:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/fastapi-login-system', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/fastapi-login-system']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'fastapi-login-system'
      - '--image'
      - 'gcr.io/$PROJECT_ID/fastapi-login-system'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--port'
      - '8080'
      - '--set-env-vars'
      - 'JWT_SECRET=your-super-secret-jwt-key'
```

Then run:
```bash
gcloud builds submit --config cloudbuild.yaml
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET` | Secret key for JWT token signing | `your-secret-key-change-in-production` |
| `PROJECT_ID` | Google Cloud Project ID | `practise-bi` |
| `DATASET_NAME` | BigQuery dataset name | `user` |
| `TABLE_NAME` | BigQuery table name | `users` |

## Security Considerations

1. **JWT Secret**: Always use a strong, unique secret key in production
2. **Service Account**: Ensure the service account has minimal required permissions
3. **HTTPS**: Always use HTTPS in production
4. **Password Hashing**: Passwords are hashed using bcrypt with salt
5. **Token Expiration**: JWT tokens expire after 24 hours by default

## Testing

### Using curl

1. **Login:**
   ```bash
   curl -X POST "http://localhost:8080/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "user123", "password": "password123"}'
   ```

2. **Get user info:**
   ```bash
   curl -X GET "http://localhost:8080/me" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Health check:**
   ```bash
   curl -X GET "http://localhost:8080/health"
   ```

## Troubleshooting

### Common Issues

1. **BigQuery Connection Error**
   - Verify the service account JSON file is present
   - Check BigQuery permissions for the service account
   - Ensure the project ID is correct

2. **JWT Token Issues**
   - Verify the JWT_SECRET environment variable is set
   - Check token expiration time

3. **Password Verification Fails**
   - Ensure passwords in BigQuery are bcrypt hashes
   - Verify the password_hash field contains valid bcrypt hashes

### Logs

Check application logs for detailed error messages:
```bash
# Local development
python app.py

# Docker
docker logs <container_id>

# Cloud Run
gcloud logs read --service=fastapi-login-system
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 