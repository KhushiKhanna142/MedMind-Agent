"""
Tool: Generate clinical simulation questions
"""

from typing import List, Dict, Optional
import random
import logging

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """
    Generate clinical simulation questions for testing medical AI models
    """
    
    def __init__(self, config=None):
        """
        Initialize Question Generator
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.question_templates = self._load_question_templates()
        logger.info("QuestionGenerator initialized")
    
    def generate(
        self,
        num_questions: int = 50,
        difficulty: str = "varied",
        domains: Optional[List[str]] = None,
        model_type: str = "general"
    ) -> List[Dict]:
        """
        Generate clinical questions
        
        Args:
            num_questions: Number of questions to generate
            difficulty: "easy", "medium", "hard", or "varied"
            domains: List of medical domains to cover
            model_type: Type of model being tested
            
        Returns:
            List of question dictionaries
        """
        logger.info(f"Generating {num_questions} questions")
        
        questions = []
        
        # Set domains
        if domains is None:
            domains = ["cardiology", "neurology", "oncology", "pediatrics", "emergency_medicine"]
        
        # Set difficulty distribution
        if difficulty == "varied":
            difficulties = ["easy", "medium", "hard"]
            difficulty_weights = [0.3, 0.5, 0.2]  # 30% easy, 50% medium, 20% hard
        else:
            difficulties = [difficulty]
            difficulty_weights = [1.0]
        
        # Generate questions
        for i in range(num_questions):
            # Select domain and difficulty
            domain = random.choice(domains)
            selected_difficulty = random.choices(difficulties, difficulty_weights)[0]
            
            # Generate question
            question = self._generate_single_question(
                question_id=f"Q{i+1:03d}",
                domain=domain,
                difficulty=selected_difficulty,
                model_type=model_type
            )
            
            questions.append(question)
        
        logger.info(f"Generated {len(questions)} questions successfully")
        return questions
    
    def _generate_single_question(
        self,
        question_id: str,
        domain: str,
        difficulty: str,
        model_type: str
    ) -> Dict:
        """
        Generate a single clinical question
        
        Args:
            question_id: Unique question ID
            domain: Medical domain
            difficulty: Question difficulty
            model_type: Model type
            
        Returns:
            Question dictionary
        """
        # Get template for domain and difficulty
        template = self._get_template(domain, difficulty)
        
        # Generate question text
        question_text = template.get("question", "")
        
        # Generate options if multiple choice
        options = template.get("options", [])
        
        # Get correct answer
        correct_answer = template.get("correct_answer", "")
        
        # Get explanation
        explanation = template.get("explanation", "")
        
        question = {
            "question_id": question_id,
            "question_text": question_text,
            "domain": domain,
            "difficulty": difficulty,
            "question_type": template.get("type", "multiple_choice"),
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "metadata": {
                "model_type": model_type,
                "template_id": template.get("template_id")
            }
        }
        
        return question
    
    def _load_question_templates(self) -> Dict:
        """
        Load question templates for different domains and difficulties
        
        Returns:
            Dictionary of question templates
        """
        # In production, load from database or file
        # For now, return sample templates
        templates = {
            "cardiology": {
                "easy": [
                    {
                        "template_id": "cardio_001",
                        "type": "multiple_choice",
                        "question": "A 55-year-old male presents with chest pain. ECG shows ST elevation in leads V1-V4. What is the most likely diagnosis?",
                        "options": [
                            "A) Unstable angina",
                            "B) Anterior STEMI",
                            "C) Pericarditis",
                            "D) Pulmonary embolism"
                        ],
                        "correct_answer": "B) Anterior STEMI",
                        "explanation": "ST elevation in V1-V4 indicates anterior wall myocardial infarction involving the left anterior descending artery."
                    }
                ],
                "medium": [
                    {
                        "template_id": "cardio_002",
                        "type": "multiple_choice",
                        "question": "A patient with heart failure shows signs of volume overload. Which medication adjustment is most appropriate?",
                        "options": [
                            "A) Increase beta-blocker dose",
                            "B) Increase diuretic dose",
                            "C) Add calcium channel blocker",
                            "D) Discontinue ACE inhibitor"
                        ],
                        "correct_answer": "B) Increase diuretic dose",
                        "explanation": "Volume overload in heart failure is best managed by increasing diuretics to reduce fluid retention."
                    }
                ],
                "hard": [
                    {
                        "template_id": "cardio_003",
                        "type": "multiple_choice",
                        "question": "A patient develops cardiogenic shock post-MI despite PCI. BP 80/50, CI 1.8. Next step?",
                        "options": [
                            "A) Intra-aortic balloon pump",
                            "B) Increase fluid resuscitation",
                            "C) Start beta-blocker",
                            "D) Observe and monitor"
                        ],
                        "correct_answer": "A) Intra-aortic balloon pump",
                        "explanation": "Cardiogenic shock with low cardiac index requires mechanical circulatory support like IABP."
                    }
                ]
            },
            # Add more domains...
        }
        
        return templates
    
    def _get_template(self, domain: str, difficulty: str) -> Dict:
        """
        Get a question template for specified domain and difficulty
        
        Args:
            domain: Medical domain
            difficulty: Question difficulty
            
        Returns:
            Question template dictionary
        """
        domain_templates = self.question_templates.get(domain, {})
        difficulty_templates = domain_templates.get(difficulty, [])
        
        if difficulty_templates:
            return random.choice(difficulty_templates)
        
        # Fallback to a generic template
        return {
            "template_id": "generic_001",
            "type": "multiple_choice",
            "question": f"Clinical question for {domain} - {difficulty} level",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "A) Option 1",
            "explanation": "Sample explanation"
        }