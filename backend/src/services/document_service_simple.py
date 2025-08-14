import os
from typing import Dict, Any, Optional, Tuple
from werkzeug.utils import secure_filename

class DocumentService:
    def __init__(self):
        self.allowed_extensions = {'txt', 'pdf', 'doc', 'docx'}
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
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
                # For demo purposes, return placeholder text
                return f"Document content extracted successfully from {os.path.basename(file_path)}. This is a simplified version for deployment."
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def save_uploaded_file(self, file, interview_id: int, document_type: str) -> Tuple[Optional[str], Optional[str]]:
        """Save uploaded file and return filename and file path."""
        try:
            print(f"DEBUG: Attempting to save file for interview {interview_id}, type {document_type}")
            
            # Check if file exists and has a filename
            if not file:
                print("DEBUG: No file provided")
                return None, None
                
            if not hasattr(file, 'filename') or not file.filename:
                print("DEBUG: File has no filename")
                return None, None
                
            print(f"DEBUG: File filename: {file.filename}")
            
            # Check if file is allowed
            if not self.allowed_file(file.filename):
                print(f"DEBUG: File type not allowed: {file.filename}")
                return None, None
            
            # Create upload directory structure
            upload_dir = os.path.join('src', 'uploads', str(interview_id))
            print(f"DEBUG: Creating upload directory: {upload_dir}")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate safe filename
            safe_filename = secure_filename(file.filename)
            filename = f"{document_type}_{safe_filename}"
            file_path = os.path.join(upload_dir, filename)
            
            print(f"DEBUG: Saving file to: {file_path}")
            
            # Save file
            file.save(file_path)
            
            # Verify file was saved
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"DEBUG: File saved successfully, size: {file_size} bytes")
                return filename, file_path
            else:
                print("DEBUG: File was not saved successfully")
                return None, None
                
        except Exception as e:
            print(f"DEBUG: Error saving file: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None

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

