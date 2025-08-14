# Deployment Guide

This document provides comprehensive deployment instructions for the Synergos AI Interview Companion Tool.

## 🏗️ Architecture Overview

The application consists of two separate services:
- **Frontend**: React.js application (user interface)
- **Backend**: Flask Python API (business logic and data processing)

## 🚀 Local Development Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Git

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd synergos-ai-complete
```

### Step 2: Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python src/main.py
   ```

The backend will be available at `http://localhost:5000`

### Step 3: Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## 🌐 Production Deployment

### Option 1: Cloud Platform Deployment

#### Frontend Deployment (Netlify/Vercel)

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy the `dist/` folder to your preferred hosting service:
   - **Netlify**: Drag and drop the `dist` folder
   - **Vercel**: Connect your GitHub repository
   - **AWS S3**: Upload to S3 bucket with static website hosting

3. Update the API base URL in production:
   ```javascript
   // In src/App.jsx and src/components/DocumentUpload.jsx
   const API_BASE_URL = 'https://your-backend-domain.com/api'
   ```

#### Backend Deployment (Heroku/Railway/DigitalOcean)

1. Create a `Procfile` in the backend directory:
   ```
   web: python src/main.py
   ```

2. Update the Flask app to use environment port:
   ```python
   # In src/main.py
   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 5000))
       app.run(host='0.0.0.0', port=port, debug=False)
   ```

3. Deploy to your preferred platform:
   - **Heroku**: `git push heroku main`
   - **Railway**: Connect GitHub repository
   - **DigitalOcean App Platform**: Connect GitHub repository

### Option 2: Docker Deployment

#### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

EXPOSE 5000

CMD ["python", "src/main.py"]
```

#### Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

Run with:
```bash
docker-compose up -d
```

## 🔧 Environment Configuration

### Backend Environment Variables

Create `backend/.env`:
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
MAX_CONTENT_LENGTH=16777216
```

### Frontend Environment Variables

Create `frontend/.env`:
```env
VITE_API_BASE_URL=https://your-backend-domain.com/api
```

Update the frontend code to use environment variables:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Use HTTPS for both frontend and backend
- [ ] Set secure CORS origins (not `*` in production)
- [ ] Use environment variables for sensitive data
- [ ] Enable rate limiting on API endpoints
- [ ] Implement proper authentication if needed
- [ ] Use secure session cookies
- [ ] Validate and sanitize all user inputs

### CORS Configuration for Production

Update `backend/src/main.py`:
```python
# For production, specify exact origins
CORS(app, origins=["https://your-frontend-domain.com"])
```

## 📊 Monitoring and Logging

### Backend Logging

Add logging configuration in `backend/src/main.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
```

### Health Check Endpoints

Add health check in `backend/src/main.py`:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS is configured correctly
   - Check that frontend is calling the correct backend URL

2. **File Upload Issues**
   - Verify `MAX_CONTENT_LENGTH` is set appropriately
   - Check file size limits on your hosting platform

3. **Database Issues**
   - Ensure database directory exists and is writable
   - For production, consider using PostgreSQL instead of SQLite

4. **Port Conflicts**
   - Change default ports if 5000 or 5173 are in use
   - Update API URLs accordingly

### Debug Mode

Enable debug mode for development:
```python
# In backend/src/main.py
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 📈 Performance Optimization

### Frontend Optimization

1. Enable gzip compression
2. Use CDN for static assets
3. Implement code splitting
4. Optimize images and assets

### Backend Optimization

1. Use production WSGI server (Gunicorn)
2. Implement caching for frequent requests
3. Optimize database queries
4. Use connection pooling

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
          
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
          
      - name: Deploy Frontend
        run: |
          cd frontend
          npm install
          npm run build
          # Deploy to your hosting service
          
      - name: Deploy Backend
        run: |
          cd backend
          pip install -r requirements.txt
          # Deploy to your hosting service
```

This deployment guide provides multiple options for hosting the Synergos AI application, from simple local development to production-ready cloud deployments.

