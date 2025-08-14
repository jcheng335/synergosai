# Railway Deployment Guide

This guide will help you deploy the Synergos AI Interview Companion Tool to Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app)
2. Git repository pushed to GitHub
3. Your project should be ready with all the production configurations

## Deployment Steps

### 1. Create a New Railway Project

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `synergosai` repository

### 2. Configure Environment Variables

In your Railway project dashboard, go to the Variables tab and add these environment variables:

**Required:**
```
SECRET_KEY=your-strong-secret-key-here
PORT=5001
```

**Optional (AI Features):**
```
OPENAI_API_KEY=your-openai-api-key-here
AWS_ACCESS_KEY_ID=your-aws-access-key-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-key-here
AWS_DEFAULT_REGION=us-east-1
```

### 3. Add PostgreSQL Database (Recommended)

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set the `DATABASE_URL` environment variable

### 4. Deploy

1. Railway will automatically build and deploy your application
2. The build process will:
   - Install Node.js dependencies
   - Build the React frontend
   - Install Python dependencies
   - Copy built frontend files to backend static folder
   - Start the Flask server

### 5. Access Your Application

1. Once deployed, Railway will provide you with a public URL
2. Your application will be accessible at: `https://your-project-name.railway.app`

## Build Process

The deployment uses the following build process defined in `nixpacks.toml`:

1. **Setup Phase**: Install Node.js and Python
2. **Install Phase**: Install frontend and backend dependencies
3. **Build Phase**: Build React app and copy to backend static folder
4. **Start Phase**: Run the Flask server

## Configuration Details

### Frontend
- Built using Vite
- Static files served by Flask backend
- API calls use relative URLs in production (`/api`)

### Backend
- Flask server with gunicorn for production
- Automatic database initialization
- CORS configured for production
- Static file serving for React app

### Database
- PostgreSQL in production (recommended)
- SQLite fallback for development
- Automatic table creation on startup

## Troubleshooting

### Build Issues
- Check the build logs in Railway dashboard
- Ensure all dependencies are listed in `requirements.txt` and `package.json`

### Environment Variables
- Verify all required environment variables are set
- Use Railway's variable groups for better organization

### Database Connection
- Ensure PostgreSQL service is running
- Check DATABASE_URL format

### API Issues
- Verify CORS settings in production
- Check that API endpoints return proper JSON responses

## Monitoring

1. Use Railway's built-in metrics and logs
2. Monitor application performance
3. Set up alerts for critical issues

## Updates

To update your deployed application:

1. Push changes to your GitHub repository
2. Railway will automatically redeploy
3. Database migrations will run automatically

## Support

If you encounter issues:

1. Check Railway's documentation: https://docs.railway.app
2. Review application logs in Railway dashboard
3. Verify environment variables and configurations

---

**Note**: The application includes an AI settings interface where users can configure OpenAI and AWS API keys directly through the web interface, so these environment variables are optional for basic functionality.