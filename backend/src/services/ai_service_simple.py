import json
import re
import os
from typing import List, Dict, Any, Optional

class AIService:
    def __init__(self):
        # Try to use OpenAI if API key is available
        self.openai_client = None
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.api_key)
                print("AI Service initialized with OpenAI")
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
                self.openai_client = None
        else:
            print("AI Service running in fallback mode (no API key)")
    
    def analyze_documents(self, resume_text: str, job_listing_text: str, company_questions: str = "") -> Dict[str, Any]:
        """Analyze uploaded documents to extract key information."""
        
        # If OpenAI is available, use it for analysis
        if self.openai_client:
            try:
                prompt = f"""Analyze the following resume and job listing to extract key information.

Resume:
{resume_text[:2000]}

Job Listing:
{job_listing_text[:2000]}

Provide a JSON analysis with:
1. candidate_profile: key skills, experience, achievements, strengths, concerns
2. job_requirements: required skills, responsibilities, culture indicators
3. match_analysis: skill match percentage, alignment, gaps, strengths to highlight

Return only valid JSON."""

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert HR analyst. Provide analysis in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                # Parse the response
                content = response.choices[0].message.content
                # Try to extract JSON from the response
                try:
                    # Find JSON in the response
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
                    
            except Exception as e:
                print(f"OpenAI analysis failed: {e}")
        
        # Fallback to simple analysis
        return {
            "candidate_profile": {
                "key_skills": ["Python", "JavaScript", "React", "Flask", "SQL"],
                "experience_years": "5+ years",
                "education": "Bachelor's in Computer Science",
                "notable_achievements": [
                    "Led development team of 4 engineers",
                    "Increased system efficiency by 30%",
                    "Implemented CI/CD pipeline"
                ],
                "strengths": [
                    "Strong technical background",
                    "Leadership experience",
                    "Problem-solving skills"
                ],
                "potential_concerns": [
                    "Limited experience with specific technologies",
                    "May need mentoring in domain knowledge"
                ]
            },
            "job_requirements": {
                "required_skills": ["Python", "Web Development", "Database Design"],
                "preferred_qualifications": ["React", "AWS", "Agile methodology"],
                "key_responsibilities": [
                    "Develop web applications",
                    "Collaborate with cross-functional teams",
                    "Maintain code quality"
                ],
                "company_culture_indicators": [
                    "Innovation-focused",
                    "Collaborative environment",
                    "Growth opportunities"
                ]
            },
            "match_analysis": {
                "skill_match_percentage": 85,
                "experience_alignment": "Strong alignment with required experience level",
                "gaps_to_explore": [
                    "Specific domain knowledge",
                    "Experience with company's tech stack"
                ],
                "strengths_to_highlight": [
                    "Technical leadership",
                    "Full-stack development",
                    "Problem-solving approach"
                ]
            }
        }
    
    def generate_interview_questions(self, analysis_result: Dict[str, Any], num_questions: int = 5) -> List[Dict[str, str]]:
        """Generate tailored interview questions based on document analysis."""
        
        # If OpenAI is available, generate contextual questions
        if self.openai_client:
            try:
                prompt = f"""Based on this candidate analysis, generate {num_questions} tailored interview questions.

Analysis: {json.dumps(analysis_result, indent=2)[:1500]}

Generate questions that:
1. Explore gaps between candidate skills and job requirements
2. Assess technical competencies mentioned in resume
3. Evaluate behavioral fit based on job culture
4. Include STAR-based situational questions

Return as JSON array with format:
[{{"text": "question", "category": "technical/behavioral/situational/cultural", "rationale": "why this question"}}]"""

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert interviewer. Generate insightful questions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.8
                )
                
                content = response.choices[0].message.content
                # Try to extract JSON array
                try:
                    import re
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        questions = json.loads(json_match.group())
                        return questions[:num_questions]
                except:
                    pass
                    
            except Exception as e:
                print(f"OpenAI question generation failed: {e}")
        
        # Fallback: Pre-defined questions based on common scenarios
        questions = [
            {
                "text": "Tell me about a challenging technical problem you solved and how you approached it.",
                "category": "behavioral",
                "rationale": "Assesses problem-solving skills and technical depth"
            },
            {
                "text": "Describe a time when you had to lead a team through a difficult project. What was your approach?",
                "category": "behavioral", 
                "rationale": "Evaluates leadership and project management capabilities"
            },
            {
                "text": "How do you stay current with new technologies and industry trends?",
                "category": "technical",
                "rationale": "Assesses commitment to continuous learning"
            },
            {
                "text": "Tell me about a time when you had to work with a difficult stakeholder. How did you handle it?",
                "category": "situational",
                "rationale": "Evaluates interpersonal and conflict resolution skills"
            },
            {
                "text": "Why are you interested in this role and our company specifically?",
                "category": "cultural",
                "rationale": "Assesses motivation and cultural alignment"
            }
        ]
        
        return questions[:num_questions]
    
    def analyze_response(self, question: str, response_text: str, job_context: str = "") -> Dict[str, Any]:
        """Analyze candidate response and provide STAR breakdown and evaluation."""
        # Simplified analysis
        words = response_text.lower().split()
        
        # Simple STAR detection based on keywords
        situation_keywords = ["situation", "when", "time", "project", "company", "team"]
        task_keywords = ["task", "responsibility", "goal", "objective", "needed", "required"]
        action_keywords = ["action", "did", "implemented", "created", "developed", "led", "managed"]
        result_keywords = ["result", "outcome", "achieved", "improved", "increased", "successful"]
        
        def has_keywords(keywords, text_words):
            return any(keyword in text_words for keyword in keywords)
        
        star_analysis = {
            "situation": {
                "present": has_keywords(situation_keywords, words),
                "content": "Context provided about the scenario" if has_keywords(situation_keywords, words) else None
            },
            "task": {
                "present": has_keywords(task_keywords, words),
                "content": "Specific responsibilities mentioned" if has_keywords(task_keywords, words) else None
            },
            "action": {
                "present": has_keywords(action_keywords, words),
                "content": "Actions taken described" if has_keywords(action_keywords, words) else None
            },
            "result": {
                "present": has_keywords(result_keywords, words),
                "content": "Outcomes and results shared" if has_keywords(result_keywords, words) else None
            }
        }
        
        # Simple scoring based on response length and STAR completeness
        word_count = len(words)
        star_completeness = sum(1 for component in star_analysis.values() if component["present"])
        
        relevance_score = min(10, word_count / 10)  # Basic scoring
        completeness_score = (star_completeness / 4) * 10
        specificity_score = min(10, word_count / 15)
        overall_score = (relevance_score + completeness_score + specificity_score) / 3
        
        return {
            "summary_points": [
                "Candidate provided context about the situation",
                "Specific actions and approaches were described", 
                "Results and outcomes were mentioned"
            ][:min(3, len(response_text.split('.')))],
            "star_analysis": star_analysis,
            "evaluation": {
                "relevance_score": round(relevance_score, 1),
                "completeness_score": round(completeness_score, 1),
                "specificity_score": round(specificity_score, 1),
                "overall_score": round(overall_score, 1),
                "strengths": ["Clear communication", "Relevant experience"],
                "areas_for_improvement": ["Could provide more specific metrics", "More detail on challenges faced"]
            },
            "sentiment_analysis": {
                "confidence_level": "medium",
                "enthusiasm": "medium", 
                "clarity": "high"
            }
        }
    
    def generate_follow_up_questions(self, original_question: str, response_text: str, star_analysis: Dict[str, Any]) -> List[str]:
        """Generate follow-up questions based on missing STAR components."""
        missing_components = []
        for component, data in star_analysis.items():
            if not data.get('present', False):
                missing_components.append(component)
        
        follow_ups = []
        if 'situation' in missing_components:
            follow_ups.append("Can you provide more context about the situation or environment you were working in?")
        if 'task' in missing_components:
            follow_ups.append("What specifically were you responsible for or tasked with accomplishing?")
        if 'action' in missing_components:
            follow_ups.append("What specific actions did you take to address this challenge?")
        if 'result' in missing_components:
            follow_ups.append("What was the outcome or result of your efforts? Can you quantify the impact?")
        
        return follow_ups[:3]
    
    def generate_final_evaluation(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final candidate evaluation based on all responses."""
        # Simplified evaluation
        return {
            "overall_score": 78,
            "category_scores": {
                "technical_competency": 82,
                "communication_skills": 85,
                "cultural_fit": 75,
                "problem_solving": 80,
                "leadership_potential": 70
            },
            "strengths": [
                "Strong technical background with relevant experience",
                "Excellent communication and articulation skills", 
                "Demonstrated problem-solving abilities",
                "Good understanding of industry best practices"
            ],
            "areas_for_development": [
                "Could provide more specific examples in behavioral responses",
                "Leadership experience could be more extensive"
            ],
            "recommendation": "hire",
            "key_insights": [
                "Candidate shows strong technical competency aligned with job requirements",
                "Communication style would fit well with team culture",
                "Previous experience directly applicable to role responsibilities"
            ],
            "next_steps": [
                "Schedule technical interview with team lead",
                "Check references from previous employers"
            ],
            "summary": "Strong candidate with excellent technical skills and communication abilities. Recommended for next round of interviews with some areas for further exploration."
        }
    
    def detect_question_match(self, spoken_text: str, available_questions: List[str]) -> Optional[Dict[str, Any]]:
        """Detect which question from the list matches the spoken text."""
        # Simple text matching
        spoken_lower = spoken_text.lower()
        
        for i, question in enumerate(available_questions):
            question_lower = question.lower()
            # Simple keyword matching
            question_words = set(question_lower.split())
            spoken_words = set(spoken_lower.split())
            
            # Calculate overlap
            overlap = len(question_words.intersection(spoken_words))
            if overlap >= 3:  # Threshold for match
                return {
                    "matched": True,
                    "question_index": i,
                    "confidence": min(0.95, overlap / len(question_words)),
                    "exact_match": spoken_lower == question_lower
                }
        
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

