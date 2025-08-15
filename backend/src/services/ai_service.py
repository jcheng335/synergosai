import openai
import json
import re
from typing import List, Dict, Any, Optional

class AIService:
    def __init__(self):
        # OpenAI client is already configured via environment variables
        self.client = openai.OpenAI()
    
    def analyze_documents(self, resume_text: str, job_listing_text: str, company_questions: str = "") -> Dict[str, Any]:
        """Analyze uploaded documents to extract key information."""
        prompt = f"""
        As an expert HR interviewer, carefully analyze the following resume and job listing to create a detailed profile.
        Focus on extracting SPECIFIC details, technologies, companies, projects, and achievements mentioned.

        RESUME:
        {resume_text}

        JOB LISTING:
        {job_listing_text}

        COMPANY INTERVIEW QUESTIONS (if provided):
        {company_questions}

        Provide a DETAILED JSON response. Be SPECIFIC - extract actual company names, project names, technologies, and achievements from the documents:
        {{
            "candidate_profile": {{
                "key_skills": ["list actual technologies/skills from resume"],
                "experience_years": "specific number",
                "current_role": "actual job title from resume",
                "companies_worked": ["actual company names from resume"],
                "education": "specific degree and institution",
                "notable_achievements": ["specific achievements with metrics from resume"],
                "projects": ["specific project names/descriptions from resume"],
                "strengths": ["specific strengths evident from experience"],
                "potential_concerns": ["specific gaps or concerns based on job requirements"]
            }},
            "job_requirements": {{
                "job_title": "exact job title from listing",
                "company_name": "company name if mentioned",
                "required_skills": ["specific skills from job listing"],
                "preferred_qualifications": ["specific qualifications from listing"],
                "key_responsibilities": ["specific responsibilities from listing"],
                "experience_required": "specific years/level from listing",
                "industry_context": "industry/domain from listing"
            }},
            "match_analysis": {{
                "matching_skills": ["specific skills candidate has that job requires"],
                "missing_skills": ["specific skills job requires that aren't evident in resume"],
                "relevant_experience": ["specific experiences from resume relevant to job"],
                "transferable_skills": ["skills from different context applicable to this role"],
                "areas_to_probe": ["specific topics to explore in interview based on gaps or questions"]
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # More capable model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse analysis response"}
                
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def generate_interview_questions(self, analysis_result: Dict[str, Any], num_questions: int = 5) -> List[Dict[str, str]]:
        """Generate tailored interview questions based on document analysis."""
        
        # Extract specific details from analysis
        candidate = analysis_result.get('candidate_profile', {})
        job = analysis_result.get('job_requirements', {})
        match = analysis_result.get('match_analysis', {})
        
        # Create a more direct prompt with the actual resume and job text
        prompt = f"""
        You are conducting an interview for {job.get('job_title', 'this position')} at {job.get('company_name', 'our company')}.
        
        The candidate has:
        - Worked at: {', '.join(candidate.get('companies_worked', [])) if candidate.get('companies_worked') else 'various companies'}
        - Skills: {', '.join(candidate.get('key_skills', [])[:5]) if candidate.get('key_skills') else 'multiple technical skills'}
        - Projects: {', '.join(candidate.get('projects', [])[:3]) if candidate.get('projects') else 'several projects'}
        - Achievements: {', '.join(candidate.get('notable_achievements', [])[:3]) if candidate.get('notable_achievements') else 'various achievements'}
        
        The role requires:
        - Skills: {', '.join(job.get('required_skills', [])[:5]) if job.get('required_skills') else 'technical expertise'}
        - Responsibilities: {', '.join(job.get('key_responsibilities', [])[:3]) if job.get('key_responsibilities') else 'key responsibilities'}
        
        Generate {num_questions} interview questions that:
        1. MUST mention specific companies, projects, or achievements from the candidate's background
        2. MUST relate to specific requirements or responsibilities of the job
        3. MUST be behavioral (start with "Tell me about...", "Describe a time...", "Walk me through...")
        4. MUST probe deeper into their actual experience, not hypotheticals
        
        For each question, pick ONE specific item from their background and connect it to ONE specific job requirement.
        
        EXAMPLES OF EXCELLENT TAILORED QUESTIONS:
        - "At {candidate.get('companies_worked', ['TechCorp'])[0] if candidate.get('companies_worked') else 'your previous company'}, you {candidate.get('notable_achievements', ['led a project'])[0] if candidate.get('notable_achievements') else 'worked on projects'}. Walk me through how you approached this and how it prepares you for {job.get('key_responsibilities', ['similar responsibilities'])[0] if job.get('key_responsibilities') else 'this role'}."
        - "You mentioned {candidate.get('projects', ['a specific project'])[0] if candidate.get('projects') else 'project experience'}. This role requires {job.get('required_skills', ['specific skills'])[0] if job.get('required_skills') else 'similar expertise'}. Describe how you applied similar skills in that context."
        - "Looking at your experience with {candidate.get('key_skills', ['Python'])[0] if candidate.get('key_skills') else 'technology'} and our need for {job.get('required_skills', ['similar tech'])[0] if job.get('required_skills') else 'technical skills'}, tell me about the most complex problem you solved using this technology."
        
        Return ONLY a JSON array with this exact structure:
        [
            {{
                "text": "Your specific question here",
                "category": "behavioral|technical|situational|cultural",
                "rationale": "Why this question matters for this specific candidate and role"
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # More capable model
                messages=[
                    {"role": "system", "content": "You are an expert interviewer who ALWAYS creates highly specific questions that reference the candidate's actual experience and companies. Never ask generic questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,  # Higher for more creative questions
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            # Extract JSON array from the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return []
                
        except Exception as e:
            print(f"Question generation failed: {str(e)}")
            return []
    
    def generate_direct_questions(self, resume_text: str, job_text: str, num_questions: int = 7) -> List[Dict[str, str]]:
        """Generate questions directly from resume and job text without intermediate analysis."""
        prompt = f"""
        Create {num_questions} highly specific interview questions for this candidate.
        
        RESUME:
        {resume_text[:2000]}  # First 2000 chars
        
        JOB DESCRIPTION:
        {job_text[:2000]}  # First 2000 chars
        
        REQUIREMENTS:
        1. Each question MUST quote or reference something SPECIFIC from the resume (a company name, project, achievement, or technology)
        2. Each question MUST connect to a SPECIFIC requirement from the job description
        3. Use this format: "I see you [specific thing from resume]. How would you apply that to [specific job requirement]?"
        4. Start questions with: "Tell me about...", "Walk me through...", "I noticed you...", "Your resume mentions..."
        
        Return a JSON array with questions that feel like you actually read their resume:
        [
            {{
                "text": "Question referencing specific details",
                "category": "behavioral|technical|situational",
                "rationale": "Why this matters"
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are reviewing a specific resume and job description. Create questions that prove you've read both documents carefully. Reference specific companies, projects, and achievements by name."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except Exception as e:
            print(f"Direct question generation failed: {str(e)}")
            return []
    
    def analyze_response(self, question: str, response_text: str, job_context: str = "") -> Dict[str, Any]:
        """Analyze candidate response and provide STAR breakdown and evaluation."""
        prompt = f"""
        As an HR expert, analyze this candidate's response to an interview question:

        QUESTION: {question}
        RESPONSE: {response_text}
        JOB CONTEXT: {job_context}

        Provide a comprehensive analysis in JSON format:
        {{
            "summary_points": ["bullet point 1", "bullet point 2", "bullet point 3"],
            "star_analysis": {{
                "situation": {{
                    "present": true/false,
                    "content": "extracted situation or null"
                }},
                "task": {{
                    "present": true/false,
                    "content": "extracted task or null"
                }},
                "action": {{
                    "present": true/false,
                    "content": "extracted action or null"
                }},
                "result": {{
                    "present": true/false,
                    "content": "extracted result or null"
                }}
            }},
            "evaluation": {{
                "relevance_score": 0-10,
                "completeness_score": 0-10,
                "specificity_score": 0-10,
                "overall_score": 0-10,
                "strengths": ["strength1", "strength2"],
                "areas_for_improvement": ["area1", "area2"]
            }},
            "sentiment_analysis": {{
                "confidence_level": "high|medium|low",
                "enthusiasm": "high|medium|low",
                "clarity": "high|medium|low"
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # More capable model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse response analysis"}
                
        except Exception as e:
            return {"error": f"Response analysis failed: {str(e)}"}
    
    def generate_follow_up_questions(self, original_question: str, response_text: str, star_analysis: Dict[str, Any]) -> List[str]:
        """Generate follow-up questions based on missing STAR components."""
        missing_components = []
        for component, data in star_analysis.items():
            if not data.get('present', False):
                missing_components.append(component)
        
        if not missing_components:
            return []
        
        prompt = f"""
        Based on the candidate's response to the interview question, generate follow-up questions to explore missing STAR components.

        ORIGINAL QUESTION: {original_question}
        CANDIDATE RESPONSE: {response_text}
        MISSING STAR COMPONENTS: {', '.join(missing_components)}

        Generate 2-3 follow-up questions that would help the candidate provide the missing information.
        Focus on: {', '.join(missing_components)}

        Provide the response as a JSON array of question strings:
        ["Follow-up question 1", "Follow-up question 2", "Follow-up question 3"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # More capable model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return []
                
        except Exception as e:
            print(f"Follow-up question generation failed: {str(e)}")
            return []
    
    def generate_final_evaluation(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final candidate evaluation based on all responses."""
        prompt = f"""
        As an HR expert, provide a comprehensive final evaluation of this candidate based on their interview performance:

        INTERVIEW DATA:
        {json.dumps(interview_data, indent=2)}

        Provide a detailed evaluation in JSON format:
        {{
            "overall_score": 0-100,
            "category_scores": {{
                "technical_competency": 0-100,
                "communication_skills": 0-100,
                "cultural_fit": 0-100,
                "problem_solving": 0-100,
                "leadership_potential": 0-100
            }},
            "strengths": ["strength1", "strength2", "strength3"],
            "areas_for_development": ["area1", "area2"],
            "recommendation": "strong_hire|hire|maybe|no_hire",
            "key_insights": ["insight1", "insight2", "insight3"],
            "next_steps": ["step1", "step2"],
            "summary": "2-3 sentence overall summary of the candidate"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # More capable model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse final evaluation"}
                
        except Exception as e:
            return {"error": f"Final evaluation failed: {str(e)}"}
    
    def detect_question_match(self, spoken_text: str, available_questions: List[str]) -> Optional[Dict[str, Any]]:
        """Detect which question from the list matches the spoken text."""
        prompt = f"""
        Analyze the spoken text and determine which of the available questions it matches best.

        SPOKEN TEXT: "{spoken_text}"

        AVAILABLE QUESTIONS:
        {json.dumps(available_questions, indent=2)}

        If the spoken text matches or is a variation of one of the available questions, return:
        {{
            "matched": true,
            "question_index": 0,
            "confidence": 0.95,
            "exact_match": false
        }}

        If no match is found, return:
        {{
            "matched": false,
            "question_index": null,
            "confidence": 0.0,
            "exact_match": false
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # More capable model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"matched": False, "question_index": None, "confidence": 0.0, "exact_match": False}
                
        except Exception as e:
            print(f"Question matching failed: {str(e)}")
            return {"matched": False, "question_index": None, "confidence": 0.0, "exact_match": False}

# Pre-populated common HR interview questions
COMMON_HR_QUESTIONS = [
    {
        "text": "Tell me about yourself and your background.",
        "category": "behavioral",
        "rationale": "Allows candidate to provide overview and sets the tone for the interview"
    },
    {
        "text": "Why are you interested in this position and our company?",
        "category": "cultural",
        "rationale": "Assesses motivation and cultural alignment"
    },
    {
        "text": "Describe a challenging situation you faced at work and how you handled it.",
        "category": "behavioral",
        "rationale": "Evaluates problem-solving skills and resilience"
    },
    {
        "text": "What are your greatest strengths and how do they apply to this role?",
        "category": "behavioral",
        "rationale": "Identifies key competencies and self-awareness"
    },
    {
        "text": "Describe a time when you had to work with a difficult team member.",
        "category": "behavioral",
        "rationale": "Assesses interpersonal and conflict resolution skills"
    },
    {
        "text": "Where do you see yourself in 5 years?",
        "category": "cultural",
        "rationale": "Evaluates career goals and long-term commitment"
    },
    {
        "text": "Describe a project you led and the outcome.",
        "category": "behavioral",
        "rationale": "Assesses leadership and project management capabilities"
    },
    {
        "text": "How do you handle stress and pressure?",
        "category": "behavioral",
        "rationale": "Evaluates stress management and coping strategies"
    },
    {
        "text": "What motivates you in your work?",
        "category": "cultural",
        "rationale": "Assesses intrinsic motivation and job satisfaction factors"
    },
    {
        "text": "Do you have any questions for us?",
        "category": "cultural",
        "rationale": "Evaluates engagement level and preparation"
    }
]

