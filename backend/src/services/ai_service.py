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
        As an HR expert, analyze the following documents and provide a comprehensive analysis:

        RESUME:
        {resume_text}

        JOB LISTING:
        {job_listing_text}

        COMPANY INTERVIEW QUESTIONS (if provided):
        {company_questions}

        Please provide a JSON response with the following structure:
        {{
            "candidate_profile": {{
                "key_skills": ["skill1", "skill2", ...],
                "experience_years": "X years",
                "education": "education details",
                "notable_achievements": ["achievement1", "achievement2", ...],
                "strengths": ["strength1", "strength2", ...],
                "potential_concerns": ["concern1", "concern2", ...]
            }},
            "job_requirements": {{
                "required_skills": ["skill1", "skill2", ...],
                "preferred_qualifications": ["qual1", "qual2", ...],
                "key_responsibilities": ["resp1", "resp2", ...],
                "company_culture_indicators": ["indicator1", "indicator2", ...]
            }},
            "match_analysis": {{
                "skill_match_percentage": 85,
                "experience_alignment": "description",
                "gaps_to_explore": ["gap1", "gap2", ...],
                "strengths_to_highlight": ["strength1", "strength2", ...]
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
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
        prompt = f"""
        Based on the following candidate and job analysis, generate {num_questions} tailored interview questions.

        ANALYSIS:
        {json.dumps(analysis_result, indent=2)}

        Generate questions that:
        1. Explore the candidate's experience relevant to the job requirements
        2. Address any gaps or concerns identified in the analysis
        3. Allow the candidate to showcase their strengths
        4. Follow best practices for behavioral interviewing

        Provide the response as a JSON array of objects with this structure:
        [
            {{
                "text": "Question text here",
                "category": "behavioral|technical|situational|cultural",
                "rationale": "Why this question is important for this candidate"
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
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
                model="gpt-4",
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
                model="gpt-4",
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
                model="gpt-4",
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
                model="gpt-4",
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

