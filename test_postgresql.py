#!/usr/bin/env python3
"""Test PostgreSQL connection and setup."""

import os
import sys
import psycopg2
from psycopg2 import sql

# Your Railway PostgreSQL URL
DATABASE_URL = "postgresql://postgres:INcfLeCuhaduEpSiPfOKKUQKJqZRgzGn@postgres.railway.internal:5432/railway"

# For local testing, you might need the external URL instead
# Get this from Railway dashboard if testing locally
EXTERNAL_DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL', DATABASE_URL)

def test_direct_connection():
    """Test direct PostgreSQL connection."""
    print("Testing PostgreSQL connection...")
    print("-" * 50)
    
    try:
        # Try to connect
        conn = psycopg2.connect(EXTERNAL_DATABASE_URL)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ Connected to PostgreSQL")
        print(f"  Version: {version[0]}")
        
        # Check existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n✓ Existing tables in database:")
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  (No tables found - database is empty)")
        
        # Check if our app tables exist
        app_tables = ['interview', 'document', 'question', 'response']
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN %s;
        """, (tuple(app_tables),))
        existing_app_tables = cursor.fetchall()
        
        if existing_app_tables:
            print(f"\n✓ App tables found: {[t[0] for t in existing_app_tables]}")
            
            # Get row counts
            for table in existing_app_tables:
                cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                    sql.Identifier(table[0])
                ))
                count = cursor.fetchone()[0]
                print(f"  - {table[0]}: {count} rows")
        else:
            print(f"\n⚠ App tables not found. They will be created on first run.")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure DATABASE_URL is set in Railway variables")
        print("2. If testing locally, you need the external URL from Railway")
        print("3. Check that PostgreSQL addon is attached to your service")
        return False

def test_sqlalchemy_connection():
    """Test connection through SQLAlchemy."""
    print("\n\nTesting SQLAlchemy connection...")
    print("-" * 50)
    
    try:
        # Add backend to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Set DATABASE_URL environment variable
        os.environ['DATABASE_URL'] = EXTERNAL_DATABASE_URL
        os.environ['RAILWAY_ENVIRONMENT'] = 'production'  # Simulate production
        
        from src.models.interview import db, Interview, Document, Question, Response
        from flask import Flask
        
        # Create minimal Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = EXTERNAL_DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Try to create tables
            db.create_all()
            print("✓ SQLAlchemy connected and tables created")
            
            # Test a query
            interview_count = Interview.query.count()
            print(f"✓ Interview count: {interview_count}")
            
            return True
            
    except Exception as e:
        print(f"✗ SQLAlchemy connection failed: {e}")
        return False

def main():
    print("PostgreSQL Connection Test")
    print("=" * 50)
    
    # Note about Railway internal URLs
    print("\nNOTE: The internal URL (postgres.railway.internal) only works")
    print("within Railway's network. For local testing, you need the")
    print("external URL from your Railway PostgreSQL settings.")
    print("")
    
    # Test direct connection
    direct_ok = test_direct_connection()
    
    # Test SQLAlchemy
    sqlalchemy_ok = test_sqlalchemy_connection()
    
    print("\n" + "=" * 50)
    if direct_ok and sqlalchemy_ok:
        print("✓ All tests passed! PostgreSQL is properly configured.")
        print("\nNext steps:")
        print("1. Make sure DATABASE_URL is set in Railway variables")
        print("2. Redeploy your application")
        print("3. Your app will now use PostgreSQL instead of SQLite")
    else:
        print("✗ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()