#!/bin/bash
# Railway build script

echo "🚀 Starting build process..."

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps

# Build frontend
echo "🔨 Building frontend..."
npm run build

# Copy built files to backend static folder
echo "📂 Copying frontend build to backend..."
cd ..
cp -r frontend/dist/* backend/src/static/

echo "✅ Build complete!"