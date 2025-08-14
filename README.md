# Synergos AI Interview Companion Tool

An intelligent interview assistant that helps interviewers conduct structured behavioral interviews using the STAR methodology with real-time AI-powered analysis.

## Features

### 🎯 Core Capabilities
- **Real-time Speech Transcription**: Live audio transcription during interviews
- **STAR Analysis**: Automatic detection and analysis of Situation, Task, Action, and Result components
- **Contextual Question Generation**: AI-generated questions based on resume and job description
- **Live Follow-up Suggestions**: Real-time follow-up questions based on candidate responses
- **Document Analysis**: Extract key information from resumes and job descriptions

### 🚀 Key Features
- Upload and analyze candidate resumes and job descriptions
- Generate tailored interview questions based on document content
- Real-time transcription with Web Speech API
- Live STAR methodology analysis during responses
- Automatic silence detection (2-second pause triggers analysis)
- Follow-up question generation targeting missing STAR components
- API key configuration for OpenAI and AWS Bedrock/Nova
- Interview session management and response tracking

## Technology Stack

### Frontend
- React.js with Vite
- Tailwind CSS for styling
- shadcn/ui components
- Web Speech API for transcription
- Real-time state management

### Backend
- Flask (Python)
- SQLAlchemy ORM
- SQLite database
- OpenAI GPT API integration
- AWS Bedrock support
- Document processing (PDF, DOCX, TXT)

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- OpenAI API key (optional, for enhanced AI features)

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/jcheng335/synergosai.git
cd synergosai
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd ../frontend
npm install
```

4. Start the backend server:
```bash
cd ../backend
python src/main.py
```

5. Start the frontend development server (in a new terminal):
```bash
cd frontend
npm run dev
```

6. Access the application at `http://localhost:5173`

## Usage

1. **Create Interview Session**: Enter interviewer and candidate information
2. **Upload Documents**: Upload candidate resume and job description (PDF, DOCX, or TXT)
3. **Analyze Documents**: Click "Analyze & Continue" to generate contextual questions
4. **Conduct Interview**: 
   - Select questions from the AI-generated list
   - Click "Start Recording" to begin transcription
   - Watch real-time STAR analysis appear as the candidate speaks
   - Use suggested follow-up questions to probe deeper
5. **Complete Interview**: Review all responses and generate final evaluation

## Configuration

### API Keys
Configure API keys through the Settings interface (gear icon):
- **OpenAI**: For enhanced STAR analysis and question generation
- **AWS Bedrock**: Alternative AI provider support

### Environment Variables
Create a `.env` file in the backend directory:
```
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```

## Features in Detail

### Real-time STAR Analysis
- Automatically analyzes responses every 100 words or after 2 seconds of silence
- Identifies presence and quality of STAR components
- Provides immediate feedback on missing elements
- Generates targeted follow-up questions

### Contextual Question Generation
- Extracts skills and requirements from documents
- Matches candidate skills with job requirements
- Creates role-specific behavioral questions
- Generates questions about specific achievements mentioned

### Live Transcription
- Browser-based speech recognition (Chrome/Edge recommended)
- Real-time transcription display
- Speaker identification
- Microphone status indicators

## Project Structure
```
synergosai/
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/ # React components
│   │   └── lib/       # Utilities
│   └── package.json
├── backend/           # Flask backend application
│   ├── src/
│   │   ├── models/    # Database models
│   │   ├── routes/    # API endpoints
│   │   └── services/  # Business logic
│   └── requirements.txt
└── README.md
```

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License
MIT License

## Support
For issues or questions, please open an issue on GitHub or contact the maintainers.

---
Built with ❤️ for better interviews using AI-powered insights