#!/usr/bin/env python3
import os
import sys
import subprocess

print("=== Starting Synergos AI Deployment ===")

# Install and build frontend
print("Building frontend...")
try:
    # Change to frontend directory
    os.chdir('frontend')
    
    # Install npm dependencies
    print("Installing frontend dependencies...")
    subprocess.run(['npm', 'install', '--legacy-peer-deps'], check=True)
    
    # Build frontend
    print("Building frontend assets...")
    subprocess.run(['npm', 'run', 'build'], check=True)
    
    # Copy dist to backend static
    print("Copying build to backend...")
    import shutil
    src_dir = 'dist'
    dst_dir = '../backend/src/static'
    
    # Clear existing static files
    if os.path.exists(dst_dir):
        for item in os.listdir(dst_dir):
            if item != '.gitkeep':
                item_path = os.path.join(dst_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
    
    # Copy new files
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dst_path = os.path.join(dst_dir, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    
    # Change back to root
    os.chdir('..')
    print("Frontend build complete!")
    
except Exception as e:
    print(f"Frontend build failed: {e}")
    # Continue anyway - maybe static files already exist

# Start the backend with gunicorn
print("Starting backend server...")
os.chdir('backend')

# Import and run gunicorn programmatically
try:
    import gunicorn.app.wsgiapp
    
    # Set up gunicorn arguments
    port = os.environ.get("PORT", 8080)
    sys.argv = ['gunicorn', '--bind', f'0.0.0.0:{port}', 'src.main:app']
    
    print(f"Starting gunicorn on port {port}...")
    gunicorn.app.wsgiapp.run()
    
except Exception as e:
    print(f"Failed to start server: {e}")
    sys.exit(1)