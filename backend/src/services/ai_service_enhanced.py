import json
import re
from typing import List, Dict, Any, Optional

class EnhancedAIService:
    def __init__(self):
        self.client = None
        self.provider = 'simple'
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AI client based on configured provider."""
        try:
            from src.routes.settings import get_current_api_keys
            keys = get_current_api_keys()
            
            if keys.get('ai_provider') == 'openai' and keys.get('openai'):
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=keys['openai'])
                    self.provider = 'openai'
                except Exception as e:
                    print(f"Failed to initialize OpenAI client: {str(e)}")
                    self.provider = 'simple'
            else:
                # Fallback to simple implementation
                self.provider = 'simple'
        except Exception as e:
            print(f"Failed to get API keys: {str(e)}")
            self.provider = 'simple'
    
    def analyze_response_star(self, question: str, response_text: str) -> Dict[str, Any]:
        """Analyze candidate response for STAR components and generate follow-up questions."""
        
        if not self.client or self.provider != 'openai':
            # Fallback to simple analysis
            return self._simple_star_analysis(response_text)
        
        try:
            prompt = f"""
            Analyze the following interview response using the STAR method (Situation, Task, Action, Result).
            
            Question: {question}
            
            Candidate Response: {response_text}
            
            Provide a detailed analysis in JSON format with:
            1. star_breakdown: Break down the response into STAR components (extract exact quotes where possible)
            2. missing_components: List which STAR components are missing or weak
            3. follow_up_questions: Generate 2-3 specific follow-up questions targeting missing STAR components
            4. strengths: List 2-3 strengths demonstrated in the response
            5. improvements: List 2-3 areas where the response could be improved
            
            JSON format:
            {{
                "star_breakdown": {{
                    "situation": {{
                        "present": boolean,
                        "content": "extracted content or null",
                        "quality": "strong/adequate/weak/missing"
                    }},
                    "task": {{
                        "present": boolean,
                        "content": "extracted content or null",
                        "quality": "strong/adequate/weak/missing"
                    }},
                    "action": {{
                        "present": boolean,
                        "content": "extracted content or null",
                        "quality": "strong/adequate/weak/missing"
                    }},
                    "result": {{
                        "present": boolean,
                        "content": "extracted content or null",
                        "quality": "strong/adequate/weak/missing"
                    }}
                }},
                "missing_components": ["list of missing/weak components"],
                "follow_up_questions": [
                    "Specific follow-up question 1",
                    "Specific follow-up question 2",
                    "Specific follow-up question 3"
                ],
                "strengths": ["strength 1", "strength 2"],
                "improvements": ["improvement 1", "improvement 2"],
                "overall_quality": "excellent/good/adequate/needs_improvement"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert HR interviewer analyzing responses using the STAR method."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Add summary points
            result['summary_points'] = self._extract_summary_points(response_text)
            
            return result
            
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            # Fallback to simple analysis
            return self._simple_star_analysis(response_text)
    
    def generate_star_follow_ups(self, star_analysis: Dict[str, Any]) -> List[str]:
        """Generate specific follow-up questions based on missing STAR components."""
        
        follow_ups = []
        star_breakdown = star_analysis.get('star_breakdown', {})
        
        # Check each STAR component
        if not star_breakdown.get('situation', {}).get('present'):
            follow_ups.append("Can you provide more context about the situation? What was happening at the time, and what made this challenging?")
        elif star_breakdown.get('situation', {}).get('quality') == 'weak':
            follow_ups.append("Could you elaborate on the background? What specific circumstances led to this situation?")
        
        if not star_breakdown.get('task', {}).get('present'):
            follow_ups.append("What was your specific role or responsibility in this situation? What were you tasked with accomplishing?")
        elif star_breakdown.get('task', {}).get('quality') == 'weak':
            follow_ups.append("Can you clarify what your specific objectives were? What were you personally responsible for?")
        
        if not star_breakdown.get('action', {}).get('present'):
            follow_ups.append("What specific actions did you take to address this challenge? Walk me through your approach step by step.")
        elif star_breakdown.get('action', {}).get('quality') == 'weak':
            follow_ups.append("Could you provide more detail about the specific steps you took? What was your personal contribution?")
        
        if not star_breakdown.get('result', {}).get('present'):
            follow_ups.append("What was the outcome of your actions? Can you share any specific results or metrics?")
        elif star_breakdown.get('result', {}).get('quality') == 'weak':
            follow_ups.append("Can you quantify the impact of your actions? What changed as a result of your efforts?")
        
        # Limit to 3 most relevant follow-ups
        return follow_ups[:3]
    
    def _simple_star_analysis(self, response_text: str) -> Dict[str, Any]:
        """Simple STAR analysis fallback when API is not available."""
        words = response_text.lower().split()
        
        # Keywords for each STAR component
        situation_keywords = ["situation", "when", "time", "project", "company", "team", "context", "background"]
        task_keywords = ["task", "responsibility", "goal", "objective", "needed", "required", "assigned", "role"]
        action_keywords = ["action", "did", "implemented", "created", "developed", "led", "managed", "approached", "decided"]
        result_keywords = ["result", "outcome", "achieved", "improved", "increased", "successful", "impact", "saved", "reduced"]
        
        def extract_content(keywords, text):
            """Extract sentences containing keywords."""
            sentences = text.split('.')
            relevant = []
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in keywords):
                    relevant.append(sentence.strip())
            return '. '.join(relevant[:2]) if relevant else None
        
        def assess_quality(content, keywords, word_count):
            """Assess the quality of a STAR component."""
            if not content:
                return "missing"
            if len(content.split()) < 10:
                return "weak"
            if len(content.split()) < 30:
                return "adequate"
            return "strong"
        
        situation_content = extract_content(situation_keywords, response_text)
        task_content = extract_content(task_keywords, response_text)
        action_content = extract_content(action_keywords, response_text)
        result_content = extract_content(result_keywords, response_text)
        
        star_breakdown = {
            "situation": {
                "present": bool(situation_content),
                "content": situation_content,
                "quality": assess_quality(situation_content, situation_keywords, len(words))
            },
            "task": {
                "present": bool(task_content),
                "content": task_content,
                "quality": assess_quality(task_content, task_keywords, len(words))
            },
            "action": {
                "present": bool(action_content),
                "content": action_content,
                "quality": assess_quality(action_content, action_keywords, len(words))
            },
            "result": {
                "present": bool(result_content),
                "content": result_content,
                "quality": assess_quality(result_content, result_keywords, len(words))
            }
        }
        
        # Identify missing components
        missing_components = []
        for component, data in star_breakdown.items():
            if not data["present"] or data["quality"] in ["missing", "weak"]:
                missing_components.append(component)
        
        # Generate follow-up questions
        follow_up_questions = self.generate_star_follow_ups({"star_breakdown": star_breakdown})
        
        # Assess overall quality
        present_count = sum(1 for c in star_breakdown.values() if c["present"])
        if present_count == 4:
            overall_quality = "good"
        elif present_count >= 2:
            overall_quality = "adequate"
        else:
            overall_quality = "needs_improvement"
        
        return {
            "star_breakdown": star_breakdown,
            "missing_components": missing_components,
            "follow_up_questions": follow_up_questions,
            "strengths": [
                "Provided a response to the question",
                "Demonstrated communication skills"
            ],
            "improvements": [
                f"Could elaborate more on {missing_components[0]}" if missing_components else "Could provide more specific details",
                "Could include more quantifiable results"
            ],
            "overall_quality": overall_quality,
            "summary_points": self._extract_summary_points(response_text)
        }
    
    def _extract_summary_points(self, text: str) -> List[str]:
        """Extract key summary points from the response."""
        sentences = text.split('.')
        # Return first 3 sentences as summary points
        return [s.strip() for s in sentences[:3] if s.strip()][:3]