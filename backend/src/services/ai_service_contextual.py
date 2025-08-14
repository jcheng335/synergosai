"""
Contextual AI service that generates questions based on actual resume and job description content.
"""
import json
import re
from typing import List, Dict, Any, Optional

class ContextualQuestionGenerator:
    def __init__(self):
        self.provider = 'contextual'
        
    def extract_key_info(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """Extract key information from resume and job description."""
        
        # Extract skills from resume
        resume_skills = self._extract_skills(resume_text)
        
        # Extract requirements from job description
        job_requirements = self._extract_requirements(job_text)
        
        # Find gaps and matches
        matching_skills = list(set(resume_skills) & set(job_requirements))
        missing_skills = list(set(job_requirements) - set(resume_skills))
        
        # Extract experience mentions
        experience_years = self._extract_experience_years(resume_text)
        
        # Extract specific projects or achievements
        achievements = self._extract_achievements(resume_text)
        
        return {
            'resume_skills': resume_skills,
            'job_requirements': job_requirements,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'experience_years': experience_years,
            'achievements': achievements,
            'job_title': self._extract_job_title(job_text),
            'company_name': self._extract_company_name(job_text)
        }
    
    def generate_contextual_questions(self, resume_text: str, job_text: str) -> List[Dict[str, str]]:
        """Generate interview questions based on resume and job description."""
        
        info = self.extract_key_info(resume_text, job_text)
        questions = []
        
        # Extract more specific details from resume
        companies = self._extract_companies(resume_text)
        projects = self._extract_projects(resume_text)
        metrics = self._extract_metrics(resume_text)
        
        # Question about specific skills match with company context
        if info['matching_skills'] and companies:
            skill = info['matching_skills'][0] if info['matching_skills'] else 'technical skills'
            company = companies[0] if companies else 'your previous role'
            questions.append({
                'text': f"I noticed you used {skill} at {company}. Can you walk me through a specific challenge you faced using {skill} and how you overcame it, particularly as it relates to the {info.get('job_title', 'position')} we're discussing?",
                'category': 'technical',
                'rationale': f'Assesses practical application of {skill} from {company} experience, directly relevant to job requirements'
            })
        
        # Question about skill gaps
        if info['missing_skills']:
            skill = info['missing_skills'][0] if info['missing_skills'] else 'new technologies'
            questions.append({
                'text': f"This role requires experience with {skill}. While it's not explicitly mentioned in your resume, how would you approach learning and applying {skill} in this position?",
                'category': 'technical',
                'rationale': f'Evaluates learning ability and approach to {skill} required for the role'
            })
        
        # Question about specific achievement with metrics
        if info['achievements']:
            achievement = info['achievements'][0] if info['achievements'] else 'your most significant achievement'
            # Try to find related metrics
            related_metric = None
            for metric in metrics:
                if any(word in metric.lower() for word in achievement.lower().split()):
                    related_metric = metric
                    break
            
            if related_metric:
                questions.append({
                    'text': f"Your resume mentions '{achievement}' with {related_metric}. Can you break down the specific strategies you employed to achieve these results, and how you measured success?",
                    'category': 'behavioral',
                    'rationale': f'Deep dive into quantifiable achievement: {achievement} with metrics'
                })
            else:
                questions.append({
                    'text': f"You mentioned '{achievement}' in your resume. What was the business impact of this achievement, and how did you measure its success?",
                    'category': 'behavioral',
                    'rationale': f'Explores specific achievement from resume with focus on measurable impact'
                })
        
        # Role-specific situational question
        job_title = info.get('job_title', 'this role')
        questions.append({
            'text': f"Given your background and the requirements for {job_title}, how would you prioritize your first 90 days in this position? What specific initiatives would you focus on?",
            'category': 'situational',
            'rationale': f'Assesses strategic thinking and understanding of {job_title} requirements'
        })
        
        # Experience-based leadership question
        if info['experience_years'] and info['experience_years'] > 3:
            questions.append({
                'text': f"With {info['experience_years']} years of experience, you've likely mentored or led others. Describe a time when you had to guide a team member through a challenging technical problem.",
                'category': 'behavioral',
                'rationale': 'Evaluates leadership and mentoring capabilities based on experience level'
            })
        else:
            questions.append({
                'text': "Describe a situation where you had to collaborate with a difficult team member or stakeholder. How did you handle it and what was the outcome?",
                'category': 'behavioral',
                'rationale': 'Assesses interpersonal skills and conflict resolution'
            })
        
        # Company culture fit question
        company = info.get('company_name', 'our company')
        questions.append({
            'text': f"Based on what you know about {company} and this role, what interests you most about this opportunity, and how do you see yourself contributing to our team?",
            'category': 'cultural',
            'rationale': f'Evaluates motivation and cultural fit with {company}'
        })
        
        # Technical deep-dive with project context
        if resume_text and len(resume_text) > 100:
            # Look for specific technologies or methodologies
            tech_keywords = self._extract_technologies(resume_text)
            if tech_keywords and projects:
                tech = tech_keywords[0]
                project = projects[0] if projects else 'a recent project'
                # Check if this tech is required for the job
                is_required = tech.lower() in job_text.lower()
                
                if is_required:
                    questions.append({
                        'text': f"Since {tech} is a key requirement for this role and you used it in {project}, can you describe the architecture decisions you made and any performance optimizations you implemented?",
                        'category': 'technical',
                        'rationale': f'Technical deep-dive into {tech} (required skill) with specific project context from resume'
                    })
                else:
                    questions.append({
                        'text': f"You worked with {tech} on {project}. How would you apply the lessons learned from that experience to the challenges in this {info.get('job_title', 'role')}?",
                        'category': 'technical',
                        'rationale': f'Explores transferable skills from {tech} experience to new role requirements'
                    })
        
        return questions[:7]  # Return top 7 most relevant questions
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        skills = []
        # Common skill keywords
        skill_patterns = [
            r'Python', r'Java', r'JavaScript', r'React', r'Node\.js', r'SQL', r'AWS', r'Docker',
            r'Kubernetes', r'Machine Learning', r'Data Analysis', r'Project Management',
            r'Agile', r'Scrum', r'Git', r'CI/CD', r'REST API', r'Microservices'
        ]
        
        text_lower = text.lower()
        for pattern in skill_patterns:
            if re.search(pattern.lower(), text_lower):
                skills.append(pattern.replace('\\', ''))
        
        return skills
    
    def _extract_requirements(self, job_text: str) -> List[str]:
        """Extract requirements from job description."""
        requirements = []
        # Look for requirements section
        req_patterns = [
            r'required', r'must have', r'requirements', r'qualifications',
            r'looking for', r'experience with', r'knowledge of'
        ]
        
        # Extract skills mentioned in job description
        requirements = self._extract_skills(job_text)
        
        return requirements
    
    def _extract_experience_years(self, resume_text: str) -> int:
        """Extract years of experience from resume."""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:\s*(\d+)\+?\s*years?',
            r'(\d+)\s*years?\s*in'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
    
    def _extract_achievements(self, resume_text: str) -> List[str]:
        """Extract achievements from resume."""
        achievements = []
        
        # Look for achievement indicators
        achievement_patterns = [
            r'[Ii]ncreased .+ by \d+%',
            r'[Rr]educed .+ by \d+%',
            r'[Ll]ed .+ team',
            r'[Mm]anaged .+ project',
            r'[Ii]mplemented .+',
            r'[Dd]eveloped .+',
            r'[Aa]chieved .+'
        ]
        
        for pattern in achievement_patterns:
            matches = re.findall(pattern, resume_text)
            achievements.extend(matches[:2])  # Take first 2 of each type
        
        return achievements[:5]  # Return top 5 achievements
    
    def _extract_job_title(self, job_text: str) -> str:
        """Extract job title from job description."""
        # Simple extraction - look for common patterns
        lines = job_text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if len(line) > 5 and len(line) < 100:
                # Likely a title
                return line.strip()
        
        return "this position"
    
    def _extract_company_name(self, job_text: str) -> str:
        """Extract company name from job description."""
        # Look for company name patterns
        patterns = [
            r'at\s+([A-Z][A-Za-z\s]+(?:Inc|LLC|Corp|Company))',
            r'([A-Z][A-Za-z\s]+(?:Inc|LLC|Corp|Company))',
            r'join\s+([A-Z][A-Za-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_text)
            if match:
                return match.group(1).strip()
        
        return "our organization"
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract specific technologies mentioned."""
        tech_patterns = [
            r'Python', r'Java(?!Script)', r'JavaScript', r'TypeScript', r'React', r'Angular', r'Vue',
            r'Node\.js', r'Express', r'Django', r'Flask', r'Spring', r'\.NET', r'C\+\+', r'C#',
            r'MongoDB', r'PostgreSQL', r'MySQL', r'Redis', r'Elasticsearch',
            r'AWS', r'Azure', r'GCP', r'Docker', r'Kubernetes', r'Jenkins',
            r'TensorFlow', r'PyTorch', r'Scikit-learn', r'Pandas', r'NumPy'
        ]
        
        found_tech = []
        text_lower = text.lower()
        
        for pattern in tech_patterns:
            if re.search(pattern.lower(), text_lower):
                found_tech.append(pattern.replace('\\', ''))
        
        return found_tech
    
    def _extract_companies(self, resume_text: str) -> List[str]:
        """Extract company names from resume."""
        companies = []
        # Look for company patterns
        patterns = [
            r'at\s+([A-Z][A-Za-z0-9\s&]+(?:Inc|LLC|Corp|Company|Technologies|Software|Systems|Solutions|Services|Group|Labs|Digital|Global|International))',
            r'([A-Z][A-Za-z0-9\s&]+(?:Inc|LLC|Corp|Company))\s*[-–—]',
            r'\n([A-Z][A-Za-z0-9\s&]+)\s*\n[A-Za-z\s]+\d{4}',  # Company name above date
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, resume_text)
            companies.extend([m.strip() for m in matches if len(m.strip()) > 2])
        
        return list(set(companies))[:3]  # Return unique top 3
    
    def _extract_projects(self, resume_text: str) -> List[str]:
        """Extract project names or descriptions from resume."""
        projects = []
        # Look for project indicators
        patterns = [
            r'(?:project|Product|Platform|System|Application|Tool|Service)\s*[:-]?\s*([A-Z][A-Za-z0-9\s]+)',
            r'(?:developed|built|created|designed|implemented)\s+(?:a\s+)?([A-Za-z0-9\s]+(?:system|platform|application|tool|service))',
            r'(?:Led|Managed)\s+(?:the\s+)?([A-Z][A-Za-z0-9\s]+(?:project|initiative|implementation))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            projects.extend([m.strip() for m in matches if len(m.strip()) > 5])
        
        return list(set(projects))[:3]
    
    def _extract_metrics(self, resume_text: str) -> List[str]:
        """Extract quantifiable metrics from resume."""
        metrics = []
        # Look for metrics patterns
        patterns = [
            r'\d+%\s+[a-z]+',  # 50% increase
            r'[a-z]+\s+(?:by|of)\s+\d+%',  # increased by 50%
            r'\$[\d,]+(?:K|M)?',  # $100K, $1.5M
            r'\d+(?:K|M)?\s+(?:users|customers|clients|transactions|requests)',  # 10K users
            r'\d+x\s+[a-z]+',  # 3x improvement
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            metrics.extend(matches)
        
        return metrics[:5]