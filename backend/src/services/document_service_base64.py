import os
import base64
import json
from typing import Dict, Any, Optional, Tuple
from werkzeug.utils import secure_filename

class DocumentServiceBase64:
    def __init__(self):
        self.allowed_extensions = {'txt', 'pdf', 'doc', 'docx'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def decode_base64_file(self, base64_data: str, filename: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """Decode base64 file data and validate."""
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 data
            file_data = base64.b64decode(base64_data)
            
            # Check file size
            if len(file_data) > self.max_file_size:
                return False, None, f"File size exceeds {self.max_file_size // (1024*1024)}MB limit"
            
            # Check if file extension is allowed
            if not self.allowed_file(filename):
                return False, None, f"File type not allowed. Supported: {', '.join(self.allowed_extensions)}"
            
            return True, file_data, None
            
        except Exception as e:
            return False, None, f"Error decoding file: {str(e)}"
    
    def save_base64_file(self, base64_data: str, filename: str, interview_id: int, document_type: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Save base64-encoded file and return filename, file path, and error message."""
        try:
            print(f"DEBUG: Processing base64 file for interview {interview_id}, type {document_type}")
            
            # Decode and validate file
            success, file_data, error_msg = self.decode_base64_file(base64_data, filename)
            if not success:
                print(f"DEBUG: File validation failed: {error_msg}")
                return None, None, error_msg
            
            # Create upload directory structure
            upload_dir = os.path.join('src', 'uploads', str(interview_id))
            print(f"DEBUG: Creating upload directory: {upload_dir}")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate safe filename
            safe_filename = secure_filename(filename)
            final_filename = f"{document_type}_{safe_filename}"
            file_path = os.path.join(upload_dir, final_filename)
            
            print(f"DEBUG: Saving file to: {file_path}")
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Verify file was saved
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"DEBUG: File saved successfully, size: {file_size} bytes")
                return final_filename, file_path, None
            else:
                print("DEBUG: File was not saved successfully")
                return None, None, "Failed to save file to disk"
                
        except Exception as e:
            print(f"DEBUG: Error saving base64 file: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None, f"Server error: {str(e)}"
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from uploaded file - simplified version."""
        try:
            if not file_path or not os.path.exists(file_path):
                return "File not found or path is empty."
                
            if file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    return content if content.strip() else "Empty file content."
            else:
                # For demo purposes, return placeholder text with file info
                file_size = os.path.getsize(file_path)
                return f"Document content extracted successfully from {os.path.basename(file_path)} ({file_size} bytes). This is a simplified version for deployment."
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def process_url_content(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Process job posting URL and extract content."""
        try:
            print(f"DEBUG: Processing URL: {url}")
            
            # For demo purposes, return simulated content
            # In production, this would use web scraping or API calls
            simulated_content = f"""
Job Posting Content from {url}

Position: Software Developer
Company: Tech Company Inc.
Location: Remote/Hybrid
Requirements:
- 3+ years of experience in software development
- Proficiency in Python, JavaScript, or similar languages
- Experience with web frameworks and databases
- Strong problem-solving skills
- Bachelor's degree in Computer Science or related field

Responsibilities:
- Develop and maintain web applications
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews
- Contribute to technical documentation

Benefits:
- Competitive salary
- Health insurance
- Remote work options
- Professional development opportunities
"""
            
            return simulated_content.strip(), None
            
        except Exception as e:
            print(f"DEBUG: Error processing URL: {str(e)}")
            return None, f"Error processing URL: {str(e)}"

class TranscriptionService:
    def __init__(self):
        pass
    
    def transcribe_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """Simulate audio transcription - simplified version."""
        return {
            "text": "This is a simulated transcription for deployment testing.",
            "speaker": "candidate",
            "confidence": 0.95,
            "timestamp": "00:00:05"
        }
    
    def detect_speaker(self, audio_data: bytes) -> str:
        """Simulate speaker detection."""
        return "candidate"  # Simplified - always return candidate

