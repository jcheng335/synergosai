from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

from src.models.interview import db, Interview, Document, Question, Response
from src.services.ai_service_simple import AIService, COMMON_HR_QUESTIONS
from src.services.document_service_simple import DocumentService, TranscriptionService
from src.services.ai_service_enhanced import EnhancedAIService
from src.services.ai_service_contextual import ContextualQuestionGenerator

interview_bp = Blueprint('interview', __name__)

# Initialize services
ai_service = AIService()
enhanced_ai_service = EnhancedAIService()
contextual_generator = ContextualQuestionGenerator()
document_service = DocumentService()
transcription_service = TranscriptionService()

@interview_bp.route('/interviews', methods=['POST'])
def create_interview():
    """Create a new interview session."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['interviewer_name', 'interviewer_email', 'candidate_name', 'position_title']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new interview
        interview = Interview(
            interviewer_name=data['interviewer_name'],
            interviewer_email=data['interviewer_email'],
            candidate_name=data['candidate_name'],
            candidate_email=data.get('candidate_email'),
            position_title=data['position_title']
        )
        
        db.session.add(interview)
        db.session.commit()
        
        return jsonify({
            'message': 'Interview created successfully',
            'interview': interview.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>', methods=['GET'])
def get_interview(interview_id):
    """Get interview details."""
    try:
        interview = Interview.query.get_or_404(interview_id)
        return jsonify({'interview': interview.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews', methods=['GET'])
def list_interviews():
    """List all interviews."""
    try:
        interviews = Interview.query.order_by(Interview.created_at.desc()).all()
        return jsonify({
            'interviews': [interview.to_dict() for interview in interviews]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/documents', methods=['POST'])
def upload_document():
    """Upload a document for an interview."""
    try:
        print(f"DEBUG: Upload request received for interview {request.view_args.get('interview_id')}")
        
        interview_id = request.view_args['interview_id']
        interview = Interview.query.get_or_404(interview_id)
        
        print(f"DEBUG: Interview found: {interview.id}")
        
        if 'file' not in request.files:
            print("DEBUG: No file in request.files")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type')
        
        print(f"DEBUG: File: {file}, Document type: {document_type}")
        
        if not file or not file.filename:
            print("DEBUG: File is empty or has no filename")
            return jsonify({'error': 'No file selected or file has no name'}), 400
        
        if not document_type or document_type not in ['resume', 'job_listing', 'questions']:
            print(f"DEBUG: Invalid document type: {document_type}")
            return jsonify({'error': 'Invalid document type. Must be: resume, job_listing, or questions'}), 400
        
        print(f"DEBUG: Attempting to save file: {file.filename}")
        
        # Save uploaded file
        filename, filepath = document_service.save_uploaded_file(file, interview_id, document_type)
        
        print(f"DEBUG: Save result - filename: {filename}, filepath: {filepath}")
        
        if not filename or not filepath:
            print("DEBUG: Failed to save file")
            return jsonify({'error': 'Failed to save uploaded file. Please check file type and size.'}), 400
        
        print(f"DEBUG: Extracting text from: {filepath}")
        
        # Extract text from file
        extracted_text = document_service.extract_text_from_file(filepath)
        
        print(f"DEBUG: Extracted text length: {len(extracted_text) if extracted_text else 0}")
        
        # Create document record
        document = Document(
            interview_id=interview_id,
            document_type=document_type,
            filename=filename,
            file_path=filepath,
            extracted_text=extracted_text
        )
        
        print("DEBUG: Adding document to database")
        
        db.session.add(document)
        db.session.commit()
        
        print("DEBUG: Document saved successfully")
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/job-url', methods=['POST'])
def add_job_url():
    """Add job posting from URL."""
    try:
        interview_id = request.view_args['interview_id']
        interview = Interview.query.get_or_404(interview_id)
        
        data = request.get_json()
        job_url = data.get('url')
        
        if not job_url:
            return jsonify({'error': 'Job URL is required'}), 400
        
        # For now, create a simple job listing document with the URL
        # In a full implementation, you would scrape the URL content
        job_content = f"Job Posting URL: {job_url}\n\nThis is a placeholder for job content that would be scraped from the URL. In a production environment, this would contain the actual job description, requirements, and company information extracted from the provided URL."
        
        # Check if job_listing document already exists
        existing_doc = Document.query.filter_by(
            interview_id=interview_id, 
            document_type='job_listing'
        ).first()
        
        if existing_doc:
            # Update existing document
            existing_doc.filename = f"job_listing_from_url.txt"
            existing_doc.file_path = f"url:{job_url}"
            existing_doc.extracted_text = job_content
        else:
            # Create new document record
            document = Document(
                interview_id=interview_id,
                document_type='job_listing',
                filename=f"job_listing_from_url.txt",
                file_path=f"url:{job_url}",
                extracted_text=job_content
            )
            db.session.add(document)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Job URL added successfully',
            'document': existing_doc.to_dict() if existing_doc else document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/analyze', methods=['POST'])
def analyze_documents(interview_id):
    """Analyze uploaded documents and generate questions."""
    try:
        print(f"Starting analysis for interview {interview_id}")
        interview = Interview.query.get_or_404(interview_id)
        
        # Get documents
        documents = {doc.document_type: doc for doc in interview.documents}
        
        if 'resume' not in documents or 'job_listing' not in documents:
            return jsonify({'error': 'Both resume and job listing are required for analysis'}), 400
        
        resume_text = documents['resume'].extracted_text
        job_listing_text = documents['job_listing'].extracted_text
        company_questions = documents.get('questions', {}).get('extracted_text', '')
        
        print(f"Documents loaded - Resume: {len(resume_text)} chars, Job: {len(job_listing_text)} chars")
        
        # Check if API key is configured
        import os
        api_key_configured = bool(os.environ.get('OPENAI_API_KEY'))
        print(f"OpenAI API key configured: {api_key_configured}")
        
        # Analyze documents
        analysis_result = ai_service.analyze_documents(resume_text, job_listing_text, company_questions)
        print(f"Analysis complete: {list(analysis_result.keys())}")
        
        # Store analysis results
        documents['resume'].analysis_result = json.dumps(analysis_result)
        
        # Generate questions - prioritize OpenAI if configured
        generated_questions = []
        
        if api_key_configured:
            # Use OpenAI for more intelligent question generation
            try:
                print("Using OpenAI for tailored question generation...")
                generated_questions = ai_service.generate_interview_questions(analysis_result, num_questions=7)
                print(f"Generated {len(generated_questions)} tailored questions using OpenAI")
            except Exception as e:
                print(f"OpenAI generation failed: {str(e)}")
        
        # Fallback to contextual generator if OpenAI fails or is not configured
        if not generated_questions:
            try:
                print("Using contextual pattern matching for question generation...")
                contextual_questions = contextual_generator.generate_contextual_questions(resume_text, job_listing_text)
                generated_questions = contextual_questions[:7]
                print(f"Generated {len(generated_questions)} questions using contextual patterns")
            except Exception as e:
                print(f"Contextual generation also failed: {str(e)}")
                # Last resort - use default questions
                generated_questions = []
        
        # Save generated questions
        for i, q_data in enumerate(generated_questions):
            question = Question(
                interview_id=interview_id,
                text=q_data['text'],
                category=q_data['category'],
                is_generated=True,
                order_index=i
            )
            db.session.add(question)
        
        # Add common HR questions as options
        for i, q_data in enumerate(COMMON_HR_QUESTIONS[:5]):
            question = Question(
                interview_id=interview_id,
                text=q_data['text'],
                category=q_data['category'],
                is_generated=False,
                order_index=i + 10  # Offset to separate from generated questions
            )
            db.session.add(question)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'analysis': analysis_result,
            'generated_questions': generated_questions,
            'total_questions': len(generated_questions) + len(COMMON_HR_QUESTIONS[:5])
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/questions', methods=['GET'])
def get_questions(interview_id):
    """Get all questions for an interview."""
    try:
        interview = Interview.query.get_or_404(interview_id)
        questions = Question.query.filter_by(interview_id=interview_id).order_by(Question.order_index).all()
        
        return jsonify({
            'questions': [q.to_dict() for q in questions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/start', methods=['POST'])
def start_interview(interview_id):
    """Start an interview session."""
    try:
        interview = Interview.query.get_or_404(interview_id)
        
        if interview.status != 'preparation':
            return jsonify({'error': 'Interview cannot be started from current status'}), 400
        
        interview.status = 'active'
        interview.started_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Interview started successfully',
            'interview': interview.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/questions/<int:question_id>/ask', methods=['POST'])
def ask_question(interview_id, question_id):
    """Mark a question as asked."""
    try:
        interview = Interview.query.get_or_404(interview_id)
        question = Question.query.filter_by(id=question_id, interview_id=interview_id).first_or_404()
        
        question.is_asked = True
        db.session.commit()
        
        return jsonify({
            'message': 'Question marked as asked',
            'question': question.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/transcribe', methods=['POST'])
def transcribe_audio():
    """Handle audio transcription during interview."""
    try:
        interview_id = request.view_args['interview_id']
        interview = Interview.query.get_or_404(interview_id)
        
        data = request.get_json()
        audio_data = data.get('audio_data')  # Base64 encoded audio
        current_question_id = data.get('question_id')
        
        if not audio_data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Transcribe audio (placeholder implementation)
        transcription_result = transcription_service.transcribe_audio(audio_data.encode())
        
        return jsonify({
            'transcription': transcription_result['transcription'],
            'speakers': transcription_result['speakers'],
            'confidence': transcription_result['confidence']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/analyze-live', methods=['POST'])
def analyze_live(interview_id):
    """Perform live STAR analysis on partial response."""
    try:
        interview = Interview.query.get_or_404(interview_id)
        
        data = request.get_json()
        question_text = data.get('question_text', '')
        partial_response = data.get('partial_response', '')
        
        if not partial_response:
            return jsonify({'error': 'No response text provided'}), 400
        
        # Use enhanced AI service for live STAR analysis
        try:
            star_result = enhanced_ai_service.analyze_response_star(question_text, partial_response)
            
            # Return streamlined analysis for live updates
            return jsonify({
                'star_breakdown': star_result.get('star_breakdown'),
                'missing_components': star_result.get('missing_components', []),
                'follow_up_questions': star_result.get('follow_up_questions', []),
                'summary_points': star_result.get('summary_points', []),
                'overall_quality': star_result.get('overall_quality', 'analyzing')
            }), 200
            
        except Exception as e:
            # Fallback to simple analysis
            analysis_result = ai_service.analyze_response(question_text, partial_response, "")
            follow_ups = ai_service.generate_follow_up_questions(
                question_text, partial_response, analysis_result.get('star_analysis', {})
            )
            
            return jsonify({
                'star_analysis': analysis_result.get('star_analysis'),
                'follow_up_questions': follow_ups[:3],
                'summary_points': analysis_result.get('summary_points', [])
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/responses', methods=['POST'])
def save_response(interview_id):
    """Save candidate response and generate analysis."""
    try:
        interview = Interview.query.get_or_404(interview_id)
        
        data = request.get_json()
        question_id = data.get('question_id')
        question_text = data.get('question_text')
        transcribed_text = data.get('transcribed_text')
        
        if not transcribed_text:
            return jsonify({'error': 'No transcribed text provided'}), 400
        
        # Get job context for analysis
        job_doc = Document.query.filter_by(interview_id=interview_id, document_type='job_listing').first()
        job_context = job_doc.extracted_text if job_doc else ""
        
        # Use enhanced AI service for STAR analysis if available
        try:
            # Try enhanced STAR analysis first
            star_result = enhanced_ai_service.analyze_response_star(question_text, transcribed_text)
            
            # Merge with basic analysis
            analysis_result = ai_service.analyze_response(question_text, transcribed_text, job_context)
            
            # Override with enhanced STAR analysis
            if star_result:
                analysis_result['star_analysis'] = star_result.get('star_breakdown', analysis_result.get('star_analysis'))
                analysis_result['star_breakdown'] = star_result.get('star_breakdown')
                analysis_result['missing_components'] = star_result.get('missing_components', [])
                analysis_result['strengths'] = star_result.get('strengths', analysis_result.get('evaluation', {}).get('strengths', []))
                analysis_result['improvements'] = star_result.get('improvements', analysis_result.get('evaluation', {}).get('areas_for_improvement', []))
                
                # Use enhanced follow-up questions
                follow_up_questions = star_result.get('follow_up_questions', [])
            else:
                # Fallback to simple follow-up generation
                follow_up_questions = ai_service.generate_follow_up_questions(
                    question_text, transcribed_text, analysis_result.get('star_analysis', {})
                )
        except Exception as e:
            print(f"Enhanced AI analysis failed: {str(e)}")
            # Fallback to simple analysis
            analysis_result = ai_service.analyze_response(question_text, transcribed_text, job_context)
            follow_up_questions = ai_service.generate_follow_up_questions(
                question_text, transcribed_text, analysis_result.get('star_analysis', {})
            )
        
        # Calculate scores
        sentiment_score = None
        confidence_score = None
        evaluation_score = None
        
        if 'sentiment_analysis' in analysis_result:
            sentiment_data = analysis_result['sentiment_analysis']
            confidence_mapping = {'high': 0.8, 'medium': 0.6, 'low': 0.4}
            confidence_score = confidence_mapping.get(sentiment_data.get('confidence_level'), 0.5)
        
        if 'evaluation' in analysis_result:
            evaluation_score = analysis_result['evaluation'].get('overall_score', 0) / 10.0
        
        # Create response record
        response = Response(
            interview_id=interview_id,
            question_id=question_id,
            question_text=question_text,
            transcribed_text=transcribed_text,
            summary_points=json.dumps(analysis_result.get('summary_points', [])),
            star_analysis=json.dumps(analysis_result.get('star_analysis', {})),
            sentiment_score=sentiment_score,
            confidence_score=confidence_score,
            evaluation_score=evaluation_score,
            follow_up_questions=json.dumps(follow_up_questions)
        )
        
        db.session.add(response)
        db.session.commit()
        
        return jsonify({
            'message': 'Response saved successfully',
            'response': response.to_dict(),
            'analysis': analysis_result,
            'follow_up_questions': follow_up_questions
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/complete', methods=['POST'])
def complete_interview(interview_id):
    """Complete an interview and generate final evaluation."""
    try:
        interview = Interview.query.get_or_404(interview_id)
        
        if interview.status != 'active':
            return jsonify({'error': 'Interview is not active'}), 400
        
        # Gather all interview data
        responses = Response.query.filter_by(interview_id=interview_id).all()
        documents = Document.query.filter_by(interview_id=interview_id).all()
        
        interview_data = {
            'interview': interview.to_dict(),
            'responses': [r.to_dict() for r in responses],
            'documents': [d.to_dict() for d in documents]
        }
        
        # Generate final evaluation
        final_evaluation = ai_service.generate_final_evaluation(interview_data)
        
        # Update interview status
        interview.status = 'completed'
        interview.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Interview completed successfully',
            'interview': interview.to_dict(),
            'final_evaluation': final_evaluation
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/interviews/<int:interview_id>/detect-question', methods=['POST'])
def detect_question(interview_id):
    """Detect which question is being asked based on speech."""
    try:
        interview = Interview.query.get_or_404(interview_id)
        
        data = request.get_json()
        spoken_text = data.get('spoken_text')
        
        if not spoken_text:
            return jsonify({'error': 'No spoken text provided'}), 400
        
        # Get available questions
        questions = Question.query.filter_by(interview_id=interview_id).all()
        question_texts = [q.text for q in questions]
        
        # Detect question match
        match_result = ai_service.detect_question_match(spoken_text, question_texts)
        
        if match_result['matched']:
            question_index = match_result['question_index']
            matched_question = questions[question_index]
            
            # Mark question as asked
            matched_question.is_asked = True
            db.session.commit()
            
            return jsonify({
                'matched': True,
                'question': matched_question.to_dict(),
                'confidence': match_result['confidence'],
                'exact_match': match_result['exact_match']
            }), 200
        else:
            return jsonify({
                'matched': False,
                'message': 'No matching question found'
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interview_bp.route('/common-questions', methods=['GET'])
def get_common_questions():
    """Get list of common HR interview questions."""
    return jsonify({
        'questions': COMMON_HR_QUESTIONS
    }), 200


# Import the new base64 document service
from src.services.document_service_base64 import DocumentServiceBase64

# Initialize base64 document service
document_service_base64 = DocumentServiceBase64()

@interview_bp.route('/interviews/<int:interview_id>/documents-base64', methods=['POST'])
def upload_document_base64(interview_id):
    """Upload a document using base64 encoding - optimized for deployment."""
    try:
        print(f"DEBUG: Base64 upload request received for interview {interview_id}")
        interview = Interview.query.get_or_404(interview_id)
        
        print(f"DEBUG: Interview found: {interview.id}")
        
        data = request.get_json()
        if not data:
            print("DEBUG: No JSON data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        base64_data = data.get('file_data')
        filename = data.get('filename')
        document_type = data.get('document_type')
        
        print(f"DEBUG: Filename: {filename}, Document type: {document_type}")
        print(f"DEBUG: Base64 data length: {len(base64_data) if base64_data else 0}")
        
        if not base64_data or not filename or not document_type:
            print("DEBUG: Missing required fields")
            return jsonify({'error': 'Missing required fields: file_data, filename, document_type'}), 400
        
        if document_type not in ['resume', 'job_listing', 'questions']:
            print(f"DEBUG: Invalid document type: {document_type}")
            return jsonify({'error': 'Invalid document type. Must be: resume, job_listing, or questions'}), 400
        
        print(f"DEBUG: Processing base64 file: {filename}")
        
        # Save base64 file
        saved_filename, filepath, error_msg = document_service_base64.save_base64_file(
            base64_data, filename, interview_id, document_type
        )
        
        print(f"DEBUG: Save result - filename: {saved_filename}, filepath: {filepath}, error: {error_msg}")
        
        if error_msg:
            print(f"DEBUG: Failed to save file: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        if not saved_filename or not filepath:
            print("DEBUG: Failed to save file - unknown error")
            return jsonify({'error': 'Failed to save uploaded file'}), 400
        
        print(f"DEBUG: Extracting text from: {filepath}")
        
        # Extract text from file
        extracted_text = document_service_base64.extract_text_from_file(filepath)
        
        print(f"DEBUG: Extracted text length: {len(extracted_text) if extracted_text else 0}")
        
        # Check if document already exists
        existing_doc = Document.query.filter_by(
            interview_id=interview_id, 
            document_type=document_type
        ).first()
        
        if existing_doc:
            print("DEBUG: Updating existing document")
            # Update existing document
            existing_doc.filename = saved_filename
            existing_doc.file_path = filepath
            existing_doc.extracted_text = extracted_text
            document = existing_doc
        else:
            print("DEBUG: Creating new document")
            # Create new document record
            document = Document(
                interview_id=interview_id,
                document_type=document_type,
                filename=saved_filename,
                file_path=filepath,
                extracted_text=extracted_text
            )
            db.session.add(document)
        
        print("DEBUG: Committing to database")
        db.session.commit()
        
        print("DEBUG: Document saved successfully")
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        print(f"DEBUG: Exception in base64 upload: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@interview_bp.route('/interviews/<int:interview_id>/job-url-enhanced', methods=['POST'])
def add_job_url_enhanced(interview_id):
    """Add job posting from URL with enhanced processing."""
    try:
        print(f"DEBUG: Enhanced URL processing for interview {interview_id}")
        interview = Interview.query.get_or_404(interview_id)
        
        data = request.get_json()
        job_url = data.get('url')
        
        print(f"DEBUG: Processing URL: {job_url}")
        
        if not job_url:
            return jsonify({'error': 'Job URL is required'}), 400
        
        # Import and use document service
        from src.services.document_service_base64 import DocumentServiceBase64
        base64_service = DocumentServiceBase64()
        
        # Process URL content
        job_content, error_msg = base64_service.process_url_content(job_url)
        
        if error_msg:
            print(f"DEBUG: URL processing failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Check if job_listing document already exists
        existing_doc = Document.query.filter_by(
            interview_id=interview_id, 
            document_type='job_listing'
        ).first()
        
        if existing_doc:
            print("DEBUG: Updating existing job listing document")
            # Update existing document
            existing_doc.filename = f"job_listing_from_url.txt"
            existing_doc.file_path = f"url:{job_url}"
            existing_doc.extracted_text = job_content
            document = existing_doc
        else:
            print("DEBUG: Creating new job listing document")
            # Create new document record
            document = Document(
                interview_id=interview_id,
                document_type='job_listing',
                filename=f"job_listing_from_url.txt",
                file_path=f"url:{job_url}",
                extracted_text=job_content
            )
            db.session.add(document)
        
        db.session.commit()
        
        print("DEBUG: Job URL processed successfully")
        
        return jsonify({
            'message': 'Job URL processed successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        print(f"DEBUG: Exception in URL processing: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500







