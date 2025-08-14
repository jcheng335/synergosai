#!/usr/bin/env python3
"""
Test script to verify production configuration
"""
import os
import sys
import subprocess
import time
import requests

def test_production_build():
    """Test the production build locally"""
    print("🔧 Testing production build...")
    
    # Set production environment
    os.environ['RAILWAY_ENVIRONMENT'] = 'production'
    os.environ['PORT'] = '5001'
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # Start the server
    print("🚀 Starting production server...")
    try:
        # Start server in background
        process = subprocess.Popen([sys.executable, 'src/main.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Test if server is running
        try:
            response = requests.get('http://localhost:5001/')
            if response.status_code == 200:
                print("✅ Frontend serving correctly")
            else:
                print(f"❌ Frontend serving failed: {response.status_code}")
                
            # Test API endpoint
            response = requests.get('http://localhost:5001/api/interviews')
            if response.status_code == 200:
                print("✅ API endpoints working")
            else:
                print(f"❌ API endpoints failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Server not responding")
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
    finally:
        # Clean up
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("🛑 Server stopped")

if __name__ == "__main__":
    test_production_build()