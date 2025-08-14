#!/usr/bin/env python3
"""Test script to verify the deployed API is working with API keys."""

import requests
import json

# Your Railway deployment URL
BASE_URL = "https://synergosai-production.up.railway.app"

def test_api_status():
    """Test if the API is accessible."""
    print("Testing API status...")
    try:
        response = requests.get(f"{BASE_URL}/api/settings/api-keys")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"[OK] API is accessible")
            print(f"[OK] OpenAI configured: {data.get('openai_configured', False)}")
            print(f"[OK] AWS configured: {data.get('aws_configured', False)}")
            return True
        else:
            print(f"[ERROR] API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return False

def test_homepage():
    """Test if the frontend is being served."""
    print("\nTesting homepage...")
    try:
        response = requests.get(BASE_URL)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("[OK] Homepage is accessible")
            # Check if it's serving the React app
            if "<!DOCTYPE html>" in response.text or "<!doctype html>" in response.text.lower():
                print("[OK] HTML content is being served")
            return True
        else:
            print(f"✗ Homepage returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return False

def main():
    print(f"Testing Railway deployment at: {BASE_URL}")
    print("=" * 50)
    
    # Test homepage
    homepage_ok = test_homepage()
    
    # Test API
    api_ok = test_api_status()
    
    print("\n" + "=" * 50)
    if homepage_ok and api_ok:
        print("[SUCCESS] All tests passed! The deployment is working.")
        print("\nNext steps:")
        print("1. Make sure OPENAI_API_KEY is set in Railway Variables")
        print("2. Try uploading resume and job listing")
        print("3. Click 'Analyze' to generate questions")
    else:
        print("[FAILED] Some tests failed. Check the deployment logs in Railway.")

if __name__ == "__main__":
    main()