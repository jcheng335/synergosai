import os
import PyPDF2
import docx
from werkzeug.utils import secure_filename
from typing import Optional, Tuple
import tempfile

class DocumentService:
    def __init__(self, upload_folder: str = None):
        self.upload_folder = upload_folder or tempfile.gettempdir()
        self.allowed_extensions = {'txt', 'pdf', 'doc', 'docx'}
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_uploaded_file(self, file, interview_id: int, document_type: str) -> Tuple[str, str]:
        """Save uploaded file and return filename and filepath."""
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        if not self.allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}")
        
        # Create secure filename
        filename = secure_filename(file.filename)
        if not filename:
            raise ValueError("Invalid filename")
        
        # Create directory structure
        interview_dir = os.path.join(self.upload_folder, f"interview_{interview_id}")
        os.makedirs(interview_dir, exist_ok=True)
        
        # Add document type prefix to filename
        filename = f"{document_type}_{filename}"
        filepath = os.path.join(interview_dir, filename)
        
        # Save file
        file.save(filepath)
        
        return filename, filepath
    
    def extract_text_from_file(self, filepath: str) -> str:
        """Extract text content from various file formats."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_extension = filepath.rsplit('.', 1)[1].lower()
        
        try:
            if file_extension == 'txt':
                return self._extract_from_txt(filepath)
            elif file_extension == 'pdf':
                return self._extract_from_pdf(filepath)
            elif file_extension in ['doc', 'docx']:
                return self._extract_from_docx(filepath)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            raise Exception(f"Failed to extract text from {filepath}: {str(e)}")
    
    def _extract_from_txt(self, filepath: str) -> str:
        """Extract text from TXT file."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            # Fallback: try with different PDF library if available
            raise Exception(f"PDF extraction failed: {str(e)}")
        
        return text.strip()
    
    def _extract_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(filepath)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    def delete_file(self, filepath: str) -> bool:
        """Delete a file safely."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Failed to delete file {filepath}: {str(e)}")
            return False
    
    def get_file_info(self, filepath: str) -> dict:
        """Get file information."""
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        stat = os.stat(filepath)
        return {
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "extension": filepath.rsplit('.', 1)[1].lower() if '.' in filepath else None
        }

class TranscriptionService:
    """Service for handling speech transcription (placeholder for Amazon Nova)."""
    
    def __init__(self):
        # This would be configured with Amazon Nova credentials
        # For now, we'll use OpenAI Whisper as a placeholder
        self.client = None
    
    def transcribe_audio(self, audio_data: bytes, speaker_diarization: bool = True) -> dict:
        """Transcribe audio with speaker diarization."""
        # Placeholder implementation
        # In production, this would use Amazon Nova
        return {
            "transcription": "This is a placeholder transcription",
            "speakers": [
                {
                    "speaker_id": "interviewer",
                    "segments": [
                        {"start": 0.0, "end": 5.0, "text": "Hello, please tell me about yourself"}
                    ]
                },
                {
                    "speaker_id": "candidate", 
                    "segments": [
                        {"start": 5.0, "end": 15.0, "text": "I am a software engineer with 5 years of experience"}
                    ]
                }
            ],
            "confidence": 0.95
        }
    
    def detect_speaker_change(self, current_speaker: str, audio_segment: bytes) -> str:
        """Detect if speaker has changed."""
        # Placeholder implementation
        return current_speaker
    
    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of transcribed text."""
        # Placeholder for Amazon Nova sentiment analysis
        return {
            "sentiment": "positive",
            "confidence": 0.85,
            "emotions": {
                "confidence": 0.7,
                "enthusiasm": 0.6,
                "nervousness": 0.3
            }
        }

