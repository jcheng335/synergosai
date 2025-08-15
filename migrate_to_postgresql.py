#!/usr/bin/env python3
"""Migrate data from SQLite to PostgreSQL."""

import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def migrate_data():
    """Migrate data from SQLite to PostgreSQL."""
    from flask import Flask
    from src.models.interview import db, Interview, Document, Question, Response
    
    print("Database Migration: SQLite -> PostgreSQL")
    print("=" * 50)
    
    # Create two Flask apps - one for each database
    sqlite_app = Flask(__name__)
    postgres_app = Flask(__name__)
    
    # Configure SQLite connection (source)
    sqlite_path = os.path.join(os.path.dirname(__file__), 'backend', 'src', 'database', 'app.db')
    if not os.path.exists(sqlite_path):
        print(f"✗ SQLite database not found at: {sqlite_path}")
        print("  No data to migrate.")
        return False
    
    sqlite_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
    sqlite_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure PostgreSQL connection (destination)
    # You'll need to set this for local testing
    postgres_url = os.environ.get('DATABASE_URL', 
        "postgresql://postgres:INcfLeCuhaduEpSiPfOKKUQKJqZRgzGn@postgres.railway.internal:5432/railway")
    
    # For local testing, you might need the external URL
    if 'railway.internal' in postgres_url and not os.environ.get('RAILWAY_ENVIRONMENT'):
        print("⚠ Warning: Using internal Railway URL. This won't work locally.")
        print("  Set DATABASE_URL to the external URL for local testing.")
        external_url = input("Enter external PostgreSQL URL (or press Enter to skip): ").strip()
        if external_url:
            postgres_url = external_url
    
    if postgres_url.startswith('postgres://'):
        postgres_url = postgres_url.replace('postgres://', 'postgresql://', 1)
    
    postgres_app.config['SQLALCHEMY_DATABASE_URI'] = postgres_url
    postgres_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize databases
    sqlite_db = db
    postgres_db = db
    
    try:
        # Connect to SQLite and load data
        sqlite_db.init_app(sqlite_app)
        
        with sqlite_app.app_context():
            print("\nReading from SQLite...")
            
            # Get all data
            interviews = Interview.query.all()
            documents = Document.query.all()
            questions = Question.query.all()
            responses = Response.query.all()
            
            print(f"  Found {len(interviews)} interviews")
            print(f"  Found {len(documents)} documents")
            print(f"  Found {len(questions)} questions")
            print(f"  Found {len(responses)} responses")
            
            # Store data in memory
            interview_data = []
            for interview in interviews:
                interview_data.append({
                    'id': interview.id,
                    'interviewer_name': interview.interviewer_name,
                    'candidate_name': interview.candidate_name,
                    'position': interview.position,
                    'company': interview.company,
                    'status': interview.status,
                    'created_at': interview.created_at,
                    'completed_at': interview.completed_at
                })
            
            document_data = []
            for doc in documents:
                document_data.append({
                    'id': doc.id,
                    'interview_id': doc.interview_id,
                    'document_type': doc.document_type,
                    'filename': doc.filename,
                    'file_path': doc.file_path,
                    'extracted_text': doc.extracted_text,
                    'analysis_result': doc.analysis_result,
                    'uploaded_at': doc.uploaded_at
                })
            
            question_data = []
            for q in questions:
                question_data.append({
                    'id': q.id,
                    'interview_id': q.interview_id,
                    'text': q.text,
                    'category': q.category,
                    'is_generated': q.is_generated,
                    'is_asked': q.is_asked,
                    'order_index': q.order_index,
                    'created_at': q.created_at
                })
            
            response_data = []
            for r in responses:
                response_data.append({
                    'id': r.id,
                    'interview_id': r.interview_id,
                    'question_id': r.question_id,
                    'transcribed_text': r.transcribed_text,
                    'analysis_result': r.analysis_result,
                    'star_rating': r.star_rating,
                    'created_at': r.created_at
                })
        
        if not interview_data:
            print("\n✓ No data to migrate. PostgreSQL is ready to use!")
            return True
        
        # Connect to PostgreSQL and insert data
        postgres_db.init_app(postgres_app)
        
        with postgres_app.app_context():
            print("\nWriting to PostgreSQL...")
            
            # Create tables
            postgres_db.create_all()
            
            # Check if data already exists
            existing = Interview.query.count()
            if existing > 0:
                print(f"\n⚠ PostgreSQL already contains {existing} interviews.")
                response = input("Do you want to continue and merge data? (y/n): ").lower()
                if response != 'y':
                    print("Migration cancelled.")
                    return False
            
            # Insert interviews
            for data in interview_data:
                interview = Interview(
                    interviewer_name=data['interviewer_name'],
                    candidate_name=data['candidate_name'],
                    position=data['position'],
                    company=data['company'],
                    status=data['status']
                )
                # Preserve timestamps
                interview.created_at = data['created_at']
                interview.completed_at = data['completed_at']
                postgres_db.session.add(interview)
            
            postgres_db.session.commit()
            print(f"  ✓ Migrated {len(interview_data)} interviews")
            
            # Insert documents
            for data in document_data:
                doc = Document(
                    interview_id=data['interview_id'],
                    document_type=data['document_type'],
                    filename=data['filename'],
                    file_path=data['file_path'],
                    extracted_text=data['extracted_text'],
                    analysis_result=data['analysis_result']
                )
                doc.uploaded_at = data['uploaded_at']
                postgres_db.session.add(doc)
            
            postgres_db.session.commit()
            print(f"  ✓ Migrated {len(document_data)} documents")
            
            # Insert questions
            for data in question_data:
                q = Question(
                    interview_id=data['interview_id'],
                    text=data['text'],
                    category=data['category'],
                    is_generated=data['is_generated'],
                    is_asked=data['is_asked'],
                    order_index=data['order_index']
                )
                q.created_at = data['created_at']
                postgres_db.session.add(q)
            
            postgres_db.session.commit()
            print(f"  ✓ Migrated {len(question_data)} questions")
            
            # Insert responses
            for data in response_data:
                r = Response(
                    interview_id=data['interview_id'],
                    question_id=data['question_id'],
                    transcribed_text=data['transcribed_text'],
                    analysis_result=data['analysis_result'],
                    star_rating=data['star_rating']
                )
                r.created_at = data['created_at']
                postgres_db.session.add(r)
            
            postgres_db.session.commit()
            print(f"  ✓ Migrated {len(response_data)} responses")
            
            print("\n✓ Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = migrate_data()
    
    if success:
        print("\nNext steps:")
        print("1. Set DATABASE_URL in Railway environment variables")
        print("2. Deploy the updated application")
        print("3. Verify the app works with PostgreSQL")
        print("4. (Optional) Delete the old SQLite database")
    else:
        print("\nMigration failed. Your SQLite data is still intact.")

if __name__ == "__main__":
    main()