#!/usr/bin/env python3
"""Test script to verify tailored question generation."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.services.ai_service import AIService
from src.services.ai_service_contextual import ContextualQuestionGenerator

# Sample resume text
resume_text = """
John Smith
Senior Software Engineer at TechCorp Inc.

EXPERIENCE:
TechCorp Inc. - Senior Software Engineer (2020-Present)
- Led development of microservices architecture using Python and FastAPI
- Reduced API response time by 40% through query optimization
- Managed team of 5 engineers on Project Phoenix platform
- Implemented CI/CD pipeline using Jenkins and Docker, reducing deployment time by 60%

DataSoft Solutions - Software Engineer (2018-2020)  
- Built real-time data processing system handling 100K transactions/day
- Developed React-based dashboard for monitoring system health
- Increased test coverage from 45% to 85% using pytest

SKILLS:
Python, JavaScript, React, FastAPI, Docker, Kubernetes, PostgreSQL, Redis, AWS, Jenkins

EDUCATION:
B.S. Computer Science - Stanford University (2018)

ACHIEVEMENTS:
- Reduced infrastructure costs by $50K annually through AWS optimization
- Received Excellence Award for Project Phoenix delivery
"""

# Sample job description
job_text = """
Senior Full Stack Engineer - InnovateTech Solutions

We're looking for a Senior Full Stack Engineer to join our growing team!

REQUIREMENTS:
- 5+ years of experience in full-stack development
- Strong expertise in Python and modern JavaScript frameworks (React preferred)
- Experience with microservices architecture and RESTful APIs
- Proficiency with cloud platforms (AWS or Azure)
- Experience with containerization (Docker, Kubernetes)
- Strong knowledge of databases (PostgreSQL, MongoDB)

RESPONSIBILITIES:
- Design and implement scalable backend services
- Develop responsive frontend applications using React
- Collaborate with product team to define technical requirements
- Mentor junior developers and conduct code reviews
- Optimize application performance and ensure high availability

PREFERRED:
- Experience with GraphQL
- Knowledge of machine learning concepts
- Experience with agile methodologies
"""

def test_ai_service():
    """Test AI service question generation."""
    print("Testing AI Service (requires OpenAI API key)...")
    print("=" * 50)
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("WARNING: OPENAI_API_KEY not set. Skipping AI service test.")
        return
    
    try:
        ai_service = AIService()
        
        # Analyze documents
        print("Analyzing documents...")
        analysis = ai_service.analyze_documents(resume_text, job_text)
        
        if 'error' not in analysis:
            print("\nAnalysis Results:")
            print(f"  Candidate Skills: {analysis.get('candidate_profile', {}).get('key_skills', [])[:3]}...")
            print(f"  Job Requirements: {analysis.get('job_requirements', {}).get('required_skills', [])[:3]}...")
            print(f"  Matching Skills: {analysis.get('match_analysis', {}).get('matching_skills', [])[:3]}...")
            
            # Generate questions
            print("\nGenerating tailored questions...")
            questions = ai_service.generate_interview_questions(analysis, num_questions=3)
            
            for i, q in enumerate(questions, 1):
                print(f"\nQuestion {i}:")
                print(f"  Text: {q['text']}")
                print(f"  Category: {q['category']}")
                print(f"  Rationale: {q['rationale']}")
        else:
            print(f"Analysis failed: {analysis['error']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_contextual_generator():
    """Test contextual question generator."""
    print("\n\nTesting Contextual Generator (no API key needed)...")
    print("=" * 50)
    
    try:
        generator = ContextualQuestionGenerator()
        
        # Extract key info
        print("Extracting key information...")
        info = generator.extract_key_info(resume_text, job_text)
        print(f"  Companies found: {info.get('companies_worked', [])}")
        print(f"  Matching skills: {info['matching_skills'][:3] if info['matching_skills'] else 'None'}...")
        print(f"  Missing skills: {info['missing_skills'][:3] if info['missing_skills'] else 'None'}...")
        
        # Generate questions
        print("\nGenerating contextual questions...")
        questions = generator.generate_contextual_questions(resume_text, job_text)
        
        for i, q in enumerate(questions[:3], 1):
            print(f"\nQuestion {i}:")
            print(f"  Text: {q['text']}")
            print(f"  Category: {q['category']}")
            print(f"  Rationale: {q['rationale']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("Testing Tailored Question Generation")
    print("=" * 70)
    
    test_contextual_generator()
    test_ai_service()
    
    print("\n" + "=" * 70)
    print("Test complete! Check the questions above to verify they reference specific details from the resume and job description.")

if __name__ == "__main__":
    main()