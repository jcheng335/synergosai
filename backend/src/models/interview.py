from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interviewer_name = db.Column(db.String(100), nullable=False)
    interviewer_email = db.Column(db.String(120), nullable=False)
    candidate_name = db.Column(db.String(100), nullable=False)
    candidate_email = db.Column(db.String(120), nullable=True)
    position_title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='preparation')  # preparation, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    documents = db.relationship('Document', backref='interview', lazy=True, cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='interview', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('Response', backref='interview', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Interview {self.id}: {self.candidate_name} for {self.position_title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'interviewer_name': self.interviewer_name,
            'interviewer_email': self.interviewer_email,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
            'position_title': self.position_title,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'documents': [doc.to_dict() for doc in self.documents],
            'questions': [q.to_dict() for q in self.questions],
            'responses': [r.to_dict() for r in self.responses]
        }

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    document_type = db.Column(db.String(20), nullable=False)  # resume, job_listing, questions
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    analysis_result = db.Column(db.Text, nullable=True)  # JSON string
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.id}: {self.document_type} - {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_id': self.interview_id,
            'document_type': self.document_type,
            'filename': self.filename,
            'file_path': self.file_path,
            'extracted_text': self.extracted_text,
            'analysis_result': json.loads(self.analysis_result) if self.analysis_result else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    is_generated = db.Column(db.Boolean, default=False)  # True if AI-generated, False if pre-populated
    is_asked = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.text[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_id': self.interview_id,
            'text': self.text,
            'category': self.category,
            'is_generated': self.is_generated,
            'is_asked': self.is_asked,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)
    question_text = db.Column(db.Text, nullable=False)  # Store actual question asked
    transcribed_text = db.Column(db.Text, nullable=False)
    summary_points = db.Column(db.Text, nullable=True)  # JSON array of bullet points
    star_analysis = db.Column(db.Text, nullable=True)  # JSON object with STAR components
    sentiment_score = db.Column(db.Float, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    evaluation_score = db.Column(db.Float, nullable=True)
    follow_up_questions = db.Column(db.Text, nullable=True)  # JSON array
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    question = db.relationship('Question', backref='responses')
    
    def __repr__(self):
        return f'<Response {self.id}: {self.transcribed_text[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_id': self.interview_id,
            'question_id': self.question_id,
            'question_text': self.question_text,
            'transcribed_text': self.transcribed_text,
            'summary_points': json.loads(self.summary_points) if self.summary_points else [],
            'star_analysis': json.loads(self.star_analysis) if self.star_analysis else {},
            'sentiment_score': self.sentiment_score,
            'confidence_score': self.confidence_score,
            'evaluation_score': self.evaluation_score,
            'follow_up_questions': json.loads(self.follow_up_questions) if self.follow_up_questions else [],
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

