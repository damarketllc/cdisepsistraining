class SepsisGradingEngine:
    """
    Automated grading engine for sepsis CDI training cases.
    Uses a 100-point rubric across 5 sections.
    """
    
    def __init__(self, case_data):
        self.case_data = case_data
        self.rubric = {
            'sepsis2_assessment': {
                'max_points': 25,
                'keywords': {
                    'Sepsis': ['sepsis', 'sirs', 'infection'],
                    'Severe Sepsis': ['severe sepsis', 'organ dysfunction', 'lactate', 'aki', 'thrombocytopenia'],
                    'Septic Shock': ['septic shock', 'hypotension', 'vasopressor', 'fluid refractory']
                }
            },
            'sepsis3_assessment': {
                'max_points': 25,
                'keywords': {
                    'Sepsis': ['sepsis', 'sofa', 'qsofa', 'organ dysfunction'],
                    'Septic Shock': ['septic shock', 'vasopressor', 'lactate >2', 'elevated lactate']
                }
            },
            'documentation_status': {
                'max_points': 25,
                'keywords': {
                    'Correctly Documented': ['correct', 'accurate', 'supported'],
                    'Misdocumented': ['misdocumented', 'unsupported', 'not supported'],
                    'Undocumented': ['undocumented', 'missing', 'not documented'],
                    'Unsupported': ['unsupported', 'no evidence']
                }
            },
            'recommendations': {
                'max_points': 15,
                'keywords': {
                    'Query': ['query', 'ask provider', 'clarify'],
                    'Flag': ['flag', 'audit', 'review'],
                    'Update': ['update', 'document', 'add']
                }
            },
            'clinical_reasoning': {
                'max_points': 10,
                'keywords': {
                    'Sound Logic': ['because', 'therefore', 'evidence', 'indicates', 'supports'],
                    'Professional': ['clinical', 'appropriate', 'justified']
                }
            }
        }
    
    def grade(self, trainee_response):
        """
        Grade trainee response against answer key.
        
        Args:
            trainee_response: Dictionary with trainee's answers
        
        Returns:
            Grading report with scores, feedback, and recommendations
        """
        
        report = {
            'total_score': 0,
            'percentage': 0,
            'letter_grade': 'F',
            'section_feedback': {},
            'strengths': [],
            'areas_for_improvement': []
        }
        
        # Grade each section
        sections = [
            ('sepsis2_assessment', trainee_response.get('sepsis2_classification', '')),
            ('sepsis3_assessment', trainee_response.get('sepsis3_classification', '')),
            ('documentation_status', trainee_response.get('documentation_status', '')),
            ('recommendations', trainee_response.get('recommendations', '')),
            ('clinical_reasoning', trainee_response.get('clinical_reasoning', ''))
        ]
        
        for section_name, trainee_answer in sections:
            section_score = self._grade_section(section_name, trainee_answer)
            max_points = self.rubric[section_name]['max_points']
            
            report['section_feedback'][section_name] = {
                'score': section_score,
                'max_points': max_points,
                'feedback': self._get_section_feedback(section_name, trainee_answer, section_score, max_points)
            }
            
            report['total_score'] += section_score
        
        # Calculate percentage and letter grade
        report['percentage'] = (report['total_score'] / 100) * 100
        report['letter_grade'] = self._calculate_letter_grade(report['percentage'])
        
        # Generate strengths and areas for improvement
        report['strengths'] = self._identify_strengths(trainee_response)
        report['areas_for_improvement'] = self._identify_improvements(trainee_response)
        
        return report
    
    def _grade_section(self, section_name, trainee_answer):
        """Grade a single section"""
        max_points = self.rubric[section_name]['max_points']
        
        if not trainee_answer or trainee_answer == 'Select...':
            return 0
        
        # Get expected answer from case data
        expected_answer = self._get_expected_answer(section_name)
        
        # Compare answers
        if self._answers_match(trainee_answer, expected_answer):
            return max_points
        elif self._answers_partially_match(trainee_answer, expected_answer):
            return int(max_points * 0.7)
        else:
            return 0
    
    def _get_expected_answer(self, section_name):
        """Get expected answer from case data"""
        if section_name == 'sepsis2_assessment':
            return self.case_data.get('sepsis2_status', '')
        elif section_name == 'sepsis3_assessment':
            return self.case_data.get('sepsis3_status', '')
        elif section_name == 'documentation_status':
            return self.case_data.get('documentation_status', '')
        elif section_name == 'recommendations':
            return self.case_data.get('cdi_action', '')
        elif section_name == 'clinical_reasoning':
            return 'Sound clinical logic'
        return ''
    
    def _answers_match(self, trainee_answer, expected_answer):
        """Check if answers match exactly"""
        return trainee_answer.lower().strip() == expected_answer.lower().strip()
    
    def _answers_partially_match(self, trainee_answer, expected_answer):
        """Check if answers partially match (keyword matching)"""
        trainee_lower = trainee_answer.lower()
        expected_lower = expected_answer.lower()
        
        # Check for key terms
        key_terms = expected_lower.split()
        matches = sum(1 for term in key_terms if term in trainee_lower)
        
        return matches >= len(key_terms) * 0.5
    
    def _get_section_feedback(self, section_name, trainee_answer, score, max_points):
        """Generate feedback for a section"""
        expected = self._get_expected_answer(section_name)
        
        if score == max_points:
            return f"Correct! You identified {expected}."
        elif score > 0:
            return f"Partially correct. Expected: {expected}. Your answer: {trainee_answer}."
        else:
            return f"Incorrect. Expected: {expected}. Your answer: {trainee_answer}."
    
    def _calculate_letter_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def _identify_strengths(self, trainee_response):
        """Identify trainee strengths"""
        strengths = []
        
        if trainee_response.get('sepsis2_classification') == self.case_data.get('sepsis2_status'):
            strengths.append("Accurate Sepsis 2 classification")
        
        if trainee_response.get('sepsis3_classification') == self.case_data.get('sepsis3_status'):
            strengths.append("Accurate Sepsis 3 classification")
        
        if trainee_response.get('documentation_status') == self.case_data.get('documentation_status'):
            strengths.append("Correct documentation status assessment")
        
        if len(trainee_response.get('clinical_reasoning', '')) > 100:
            strengths.append("Thorough clinical reasoning provided")
        
        if len(trainee_response.get('recommendations', '')) > 50:
            strengths.append("Detailed CDI recommendations")
        
        if not strengths:
            strengths.append("Review case details and compare with answer key")
        
        return strengths
    
    def _identify_improvements(self, trainee_response):
        """Identify areas for improvement"""
        improvements = []
        
        if trainee_response.get('sepsis2_classification') != self.case_data.get('sepsis2_status'):
            improvements.append(f"Review Sepsis 2 criteria: Expected {self.case_data.get('sepsis2_status')}")
        
        if trainee_response.get('sepsis3_classification') != self.case_data.get('sepsis3_status'):
            improvements.append(f"Review Sepsis 3 criteria: Expected {self.case_data.get('sepsis3_status')}")
        
        if trainee_response.get('documentation_status') != self.case_data.get('documentation_status'):
            improvements.append(f"Review documentation assessment: Expected {self.case_data.get('documentation_status')}")
        
        if len(trainee_response.get('clinical_reasoning', '')) &lt; 50:
            improvements.append("Provide more detailed clinical reasoning")
        
        if len(trainee_response.get('recommendations', '')) &lt; 30:
            improvements.append("Provide more specific CDI recommendations")
        
        if not improvements:
            improvements.append("Excellent work! Continue practicing with more cases.")
        
        return improvements
