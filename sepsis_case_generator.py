import random
from datetime import datetime, timedelta
import json

class SepsisCaseGenerator:
    """
    Generates realistic mock sepsis cases for CDI training.
    Supports Sepsis 2 and Sepsis 3 dual-criteria framework.
    """
    
    def __init__(self):
        self.infection_sources = {
            "pneumonia": {
                "description": "Community-acquired pneumonia",
                "cultures": ["Sputum culture", "Blood culture"],
                "imaging": "Chest X-ray showing infiltrates"
            },
            "urosepsis": {
                "description": "Urinary tract infection progressing to sepsis",
                "cultures": ["Urine culture", "Blood culture"],
                "imaging": "Renal ultrasound showing hydronephrosis"
            },
            "bloodstream": {
                "description": "Primary bloodstream infection",
                "cultures": ["Blood culture (multiple sets)"],
                "imaging": "CT chest/abdomen for source control"
            },
            "surgical_site": {
                "description": "Post-operative surgical site infection",
                "cultures": ["Wound culture", "Blood culture"],
                "imaging": "CT abdomen/pelvis showing abscess"
            },
            "intra_abdominal": {
                "description": "Intra-abdominal infection (peritonitis, appendicitis)",
                "cultures": ["Blood culture", "Peritoneal fluid culture"],
                "imaging": "CT abdomen/pelvis showing perforation/abscess"
            }
        }
        
        self.clinical_thresholds = {
            "sirs_temp_high": 38.5,
            "sirs_temp_low": 36.0,
            "sirs_hr": 90,
            "sirs_rr": 20,
            "sirs_wbc_high": 12,
            "sirs_wbc_low": 4,
            "lactate_normal": 2.0,
            "lactate_elevated": 4.0,
            "creatinine_normal": 1.2,
            "creatinine_aki": 2.5,
            "bilirubin_normal": 1.2,
            "bilirubin_elevated": 3.0,
            "platelets_normal": 150,
            "platelets_low": 100,
            "map_normal": 65,
            "map_hypotensive": 55
        }
    
    def generate_case(self, difficulty, case_type, infection_source, include_answer_key=True, include_teaching_points=True):
        """
        Main method to generate a mock sepsis case.
        
        Args:
            difficulty: "1", "2", or "3" (Straightforward, Intermediate, Advanced)
            case_type: Type of case (e.g., "Missed Severity", "Denial Trap", "Random Mix")
            infection_source: Infection source (e.g., "pneumonia", "urosepsis", "Random")
            include_answer_key: Include answer key for instructors
            include_teaching_points: Include teaching points
        
        Returns:
            Dictionary containing complete case data
        """
        
        # Normalize inputs
        difficulty_map = {"Level 1 (Straightforward)": "1", "Level 2 (Intermediate)": "2", "Level 3 (Advanced)": "3"}
        difficulty = difficulty_map.get(difficulty, difficulty)
        
        # Select infection source
        if infection_source.lower() == "random":
            infection_source = random.choice(list(self.infection_sources.keys()))
        
        # Generate case based on type
        case_builders = {
            "Missed Severity (RULE_01)": self._build_missed_severity_case,
            "Denial Trap (RULE_02)": self._build_denial_trap_case,
            "Sepsis Only": self._build_sepsis_only_case,
            "Sepsis 2 Only": self._build_s2_only_case,
            "Sepsis 3 Only": self._build_s3_only_case,
            "Undocumented": self._build_undocumented_case,
            "Misdocumented": self._build_misdocumented_case,
            "Shock Misclassification": self._build_shock_misclassification_case,
            "Resolved Sepsis": self._build_resolved_sepsis_case,
            "Random Mix": self._build_random_case
        }
        
        builder = case_builders.get(case_type, self._build_random_case)
        case_data = builder(difficulty, infection_source)
        
        # Add metadata
        case_data['case_id'] = f"CDI-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        case_data['difficulty_level'] = difficulty
        case_data['case_type'] = case_type
        case_data['infection_source'] = infection_source
        
        # Generate answer key and teaching points
        if include_answer_key:
            case_data['answer_key'] = self._generate_answer_key(case_data)
        
        if include_teaching_points:
            case_data['teaching_points'] = self._generate_teaching_points(case_data)
        
        return case_data
    
    def _build_missed_severity_case(self, difficulty, infection_source):
        """RULE_01: Provider documents 'Sepsis' when patient has organ dysfunction (lactate >2.0)"""
        case = self._base_case(difficulty, infection_source)
        
        # Set up RULE_01 scenario
        case['vitals']['temperature'] = 39.2
        case['vitals']['heart_rate'] = 115
        case['vitals']['respiratory_rate'] = 24
        case['labs']['wbc'] = 18.5
        case['labs']['lactate'] = 3.5  # Elevated - indicates organ dysfunction
        case['labs']['creatinine'] = 2.1  # AKI
        case['labs']['platelets'] = 95  # Thrombocytopenia
        
        case['clinical_timeline'] = f"Patient admitted with {self.infection_sources[infection_source]['description']}. Initial vitals show fever (39.2°C), tachycardia (115 bpm), tachypnea (24 breaths/min). Labs reveal elevated lactate (3.5 mmol/L), acute kidney injury (Cr 2.1), and thrombocytopenia (95 K/µL). Provider documented 'Sepsis' but failed to recognize organ dysfunction indicators."
        
        case['documented_diagnoses'] = "- Sepsis\n- Pneumonia (or other infection source)\n- Acute kidney injury"
        
        case['sepsis2_status'] = "Severe Sepsis"  # Should be documented as this
        case['sepsis3_status'] = "Sepsis"
        case['documentation_status'] = "Misdocumented"
        case['cdi_action'] = "Query provider: Does patient meet criteria for Severe Sepsis (Sepsis 2)?"
        
        return case
    
    def _build_denial_trap_case(self, difficulty, infection_source):
        """RULE_02: Provider documents 'Septic Shock' (valid S2) but fails S3 criteria (requires vasopressor + lactate >2.0)"""
        case = self._base_case(difficulty, infection_source)
        
        # Set up RULE_02 scenario
        case['vitals']['temperature'] = 38.8
        case['vitals']['heart_rate'] = 120
        case['vitals']['respiratory_rate'] = 26
        case['vitals']['blood_pressure'] = "85/52"
        case['vitals']['map'] = 63
        case['labs']['wbc'] = 16.2
        case['labs']['lactate'] = 1.8  # NOT elevated (critical for RULE_02)
        case['labs']['creatinine'] = 1.9
        
        case['clinical_timeline'] = f"Patient with {self.infection_sources[infection_source]['description']} presents with hypotension (85/52 mmHg). Fluid resuscitation initiated but patient remains hypotensive. Provider documents 'Septic Shock' based on hypotension. However, lactate is 1.8 mmol/L (not elevated) and no vasopressor documented."
        
        case['interventions'] = "- Fluid resuscitation (30 mL/kg)\n- Broad-spectrum antibiotics\n- No vasopressor documented"
        
        case['documented_diagnoses'] = "- Septic Shock\n- Infection source\n- Hypotension"
        
        case['sepsis2_status'] = "Septic Shock"  # Valid under Sepsis 2 (hypotension + fluid refractory)
        case['sepsis3_status'] = "Sepsis (NOT Septic Shock)"  # Invalid under Sepsis 3 (requires vasopressor + lactate >2.0)
        case['documentation_status'] = "Unsupported (Sepsis 3)"
        case['cdi_action'] = "Flag for audit denial risk: Septic Shock documented but does not meet Sepsis 3 criteria (no vasopressor, lactate &lt;2.0). High risk for payor denial."
        
        return case
    
    def _build_sepsis_only_case(self, difficulty, infection_source):
        """Case meeting sepsis criteria without organ dysfunction"""
        case = self._base_case(difficulty, infection_source)
        
        case['vitals']['temperature'] = 38.5
        case['vitals']['heart_rate'] = 95
        case['vitals']['respiratory_rate'] = 22
        case['labs']['wbc'] = 13.5
        case['labs']['lactate'] = 1.5  # Normal
        case['labs']['creatinine'] = 1.0  # Normal
        
        case['clinical_timeline'] = f"Patient with {self.infection_sources[infection_source]['description']}. SIRS criteria met (fever, tachycardia, tachypnea, elevated WBC). No organ dysfunction indicators present."
        
        case['sepsis2_status'] = "Sepsis"
        case['sepsis3_status'] = "Sepsis"
        case['documentation_status'] = "Correctly Documented"
        
        return case
    
    def _build_s2_only_case(self, difficulty, infection_source):
        """Case meeting Sepsis 2 but not Sepsis 3 criteria"""
        case = self._base_case(difficulty, infection_source)
        
        case['vitals']['temperature'] = 39.0
        case['vitals']['heart_rate'] = 110
        case['vitals']['respiratory_rate'] = 25
        case['labs']['wbc'] = 17.0
        case['labs']['lactate'] = 1.9  # Just below threshold
        case['labs']['creatinine'] = 2.2  # AKI
        
        case['clinical_timeline'] = f"Patient with {self.infection_sources[infection_source]['description']}. Meets SIRS criteria and has organ dysfunction (AKI). Lactate borderline at 1.9 mmol/L."
        
        case['sepsis2_status'] = "Severe Sepsis"
        case['sepsis3_status'] = "Not Sepsis 3"  # SOFA &lt;2
        case['documentation_status'] = "Correctly Documented (Sepsis 2 Only)"
        
        return case
    
    def _build_s3_only_case(self, difficulty, infection_source):
        """Case meeting Sepsis 3 but not Sepsis 2 criteria"""
        case = self._base_case(difficulty, infection_source)
        
        case['vitals']['temperature'] = 37.8
        case['vitals']['heart_rate'] = 88
        case['vitals']['respiratory_rate'] = 18
        case['labs']['wbc'] = 11.0  # Just below SIRS threshold
        case['labs']['lactate'] = 2.5  # Elevated
        case['labs']['creatinine'] = 2.0  # AKI
        
        case['clinical_timeline'] = f"Patient with {self.infection_sources[infection_source]['description']}. Does not meet full SIRS criteria (WBC 11.0) but has elevated lactate and AKI, meeting SOFA criteria."
        
        case['sepsis2_status'] = "Not Sepsis 2"  # Doesn't meet SIRS
        case['sepsis3_status'] = "Sepsis"  # Meets SOFA
        case['documentation_status'] = "Correctly Documented (Sepsis 3 Only)"
        
        return case
    
    def _build_undocumented_case(self, difficulty, infection_source):
        """Case where sepsis criteria are met but not documented"""
        case = self._base_case(difficulty, infection_source)
        
        case['vitals']['temperature'] = 39.1
        case['vitals']['heart_rate'] = 118
        case['vitals']['respiratory_rate'] = 24
        case['labs']['wbc'] = 16.8
        case['labs']['lactate'] = 3.2
        case['labs']['creatinine'] = 2.3
        
        case['clinical_timeline'] = f"Patient with {self.infection_sources[infection_source]['description']}. Clear sepsis presentation with organ dysfunction."
        
        case['documented_diagnoses'] = "- Infection source only\n- No sepsis documented"
        
        case['sepsis2_status'] = "Severe Sepsis"
        case['sepsis3_status'] = "Sepsis"
        case['documentation_status'] = "Undocumented"
        case['cdi_action'] = "Query provider: Patient meets criteria for Sepsis/Severe Sepsis. Please document."
        
        return case
    
    def _build_misdocumented_case(self, difficulty, infection_source):
        """Case where sepsis is documented but criteria are not met"""
        case = self._base_case(difficulty, infection_source)
        
        case['vitals']['temperature'] = 37.5
        case['vitals']['heart_rate'] = 82
        case['vitals']['respiratory_rate'] = 18
        case['labs']['wbc'] = 10.5
        case['labs']['lactate'] = 1.2
        case['labs']['creatinine'] = 0.9
        
        case['clinical_timeline'] = f"Patient with {self.infection_sources[infection_source]['description']}. Stable vital signs, no organ dysfunction."
        
        case['documented_diagnoses'] = "- Sepsis\n- Infection source"
        
        case['sepsis2_status'] = "Not Sepsis 2"
        case['sepsis3_status'] = "Not Sepsis 3"
        case['documentation_status'] = "Misdocumented"
        case['cdi_action'] = "Query provider: Sepsis documented but criteria not met. Please clarify or remove diagnosis."
        
        return case
    
    def _build_shock_misclassification_case(self, difficulty, infection_source):
        """Case with shock documentation errors"""
        case = self._base_case(difficulty, infection_source)
        
        case['vitals']['temperature'] = 39.5
        case['vitals']['heart_rate'] = 125
        case['vitals']['respiratory_rate'] = 28
        case['vitals']['blood_pressure'] = "78/48"
        case['vitals']['map'] = 58
        case['labs']['wbc'] = 19.0
        case['labs']['lactate'] = 4.5
        case['labs']['creatinine'] = 2.8
        case['interventions'] = "- Fluid resuscitation\n- Vasopressor (norepinephrine) initiated\n- Broad-spectrum antibiotics"
        
        case['documented_diagnoses'] = "- Sepsis (NOT Septic Shock)\n- Hypotension\n- Infection source"
        
        case['sepsis2_status'] = "Septic Shock"
        case['sepsis3_status'] = "Septic Shock"
        case['documentation_status'] = "Undocumented"
        case['cdi_action'] = "Query provider: Patient on vasopressor with elevated lactate. Meets criteria for Septic Shock. Please document."
        
        return case
    
    def _build_resolved_sepsis_case(self, difficulty, infection_source):
        """Case where sepsis has resolved"""
        case = self._base_case(difficulty, infection_source)
        
        case['hospital_day'] = 5
        case['vitals']['temperature'] = 37.2
        case['vitals']['heart_rate'] = 78
        case['vitals']['respiratory_rate'] = 16
        case['labs']['wbc'] = 9.5
        case['labs']['lactate'] = 1.1
        case['labs']['creatinine'] = 1.3
        
        case['clinical_timeline'] = f"Patient admitted with {self.infection_sources[infection_source]['description']} on Day 1. Treated with antibiotics and supportive care. By Day 5, vital signs normalized, labs improved, patient clinically stable."
        
        case['documented_diagnoses'] = "- Sepsis (from Day 1)\n- Infection source (resolved)"
        
        case['sepsis2_status'] = "Resolved"
        case['sepsis3_status'] = "Resolved"
        case['documentation_status'] = "Incomplete"
        case['cdi_action'] = "Query provider: Sepsis documented from admission but patient now clinically resolved. Please clarify current status."
        
        return case
    
    def _build_random_case(self, difficulty, infection_source):
        """Generate a random case type"""
        case_types = [
            "Missed Severity (RULE_01)",
            "Denial Trap (RULE_02)",
            "Sepsis Only",
            "Sepsis 2 Only",
            "Sepsis 3 Only",
            "Undocumented",
            "Misdocumented",
            "Shock Misclassification",
            "Resolved Sepsis"
        ]
        random_type = random.choice(case_types)
        builder = getattr(self, f"_build_{random_type.lower().replace(' ', '_').replace('(', '').replace(')', '')}_case", None)
        
        if builder:
            return builder(difficulty, infection_source)
        else:
            return self._build_sepsis_only_case(difficulty, infection_source)
    
    def _base_case(self, difficulty, infection_source):
        """Generate base case structure"""
        admission_date = datetime.now() - timedelta(days=random.randint(1, 5))
        hospital_day = random.randint(1, 4)
        
        return {
            'patient_name': random.choice(['John Smith', 'Mary Johnson', 'Robert Davis', 'Patricia Miller', 'Michael Wilson']),
            'age': random.randint(45, 85),
            'sex': random.choice(['Male', 'Female']),
            'admission_date': admission_date.strftime('%Y-%m-%d'),
            'hospital_day': hospital_day,
            'comorbidities': random.sample(['Diabetes', 'Hypertension', 'COPD', 'Heart Disease', 'Renal Disease'], k=random.randint(1, 3)),
            'vitals': {
                'temperature': 37.5,
                'heart_rate': 80,
                'respiratory_rate': 16,
                'blood_pressure': '120/80',
                'map': 93,
                'gcs': 15
            },
            'labs': {
                'wbc': 10.0,
                'lactate': 1.5,
                'creatinine': 1.0,
                'bilirubin': 0.8,
                'platelets': 200,
                'inr': 1.0,
                'aptt': 28,
                'pao2_fio2': 400
            },
            'clinical_timeline': '',
            'imaging_findings': f"Imaging consistent with {self.infection_sources[infection_source]['description']}",
            'interventions': '- Broad-spectrum antibiotics\n- Fluid resuscitation\n- Supportive care',
            'documented_diagnoses': '',
            'sepsis2_status': '',
            'sepsis3_status': '',
            'documentation_status': '',
            'cdi_action': ''
        }
    
    def _generate_answer_key(self, case_data):
        """Generate the correct answer key"""
        return {
            'sepsis2_classification': case_data['sepsis2_status'],
            'sepsis3_classification': case_data['sepsis3_status'],
            'documentation_status': case_data['documentation_status'],
            'cdi_action': case_data['cdi_action'],
            'regulatory_notes': self._determine_regulatory_notes(case_data)
        }
    
    def _generate_teaching_points(self, case_data):
        """Generate teaching points for the case"""
        points = []
        
        if 'RULE_01' in case_data['case_type'] or case_data['sepsis2_status'] == 'Severe Sepsis':
            points.append("RULE_01 (Missed Severity): Always assess for organ dysfunction indicators (lactate, AKI, thrombocytopenia, altered mental status) when documenting sepsis.")
        
        if 'RULE_02' in case_data['case_type']:
            points.append("RULE_02 (Audit Denial Trap): Septic Shock under Sepsis 2 (hypotension + fluid refractory) differs from Sepsis 3 (requires vasopressor + lactate >2.0). Verify both criteria before documenting shock.")
        
        if case_data['sepsis2_status'] != case_data['sepsis3_status']:
            points.append(f"Dual-Criteria Awareness: This case meets {case_data['sepsis2_status']} under Sepsis 2 but {case_data['sepsis3_status']} under Sepsis 3. Document both standards for clarity.")
        
        if case_data['documentation_status'] == 'Undocumented':
            points.append("Documentation Gap: Clinical evidence supports sepsis diagnosis, but it was not documented. Always query provider when criteria are met but diagnosis is missing.")
        
        if case_data['documentation_status'] == 'Misdocumented':
            points.append("Misdocumentation: Sepsis was documented without supporting clinical evidence. Query provider to clarify or remove unsupported diagnosis.")
        
        return points
    
    def _determine_regulatory_notes(self, case_data):
        """Determine regulatory implications"""
        notes = []
        
        if case_data['sepsis2_status'] != case_data['sepsis3_status']:
            notes.append("CMS (Sepsis 2) vs. Payor (Sepsis 3) discrepancy detected. Ensure documentation supports both standards.")
        
        if 'RULE_02' in case_data['case_type']:
            notes.append("HIGH AUDIT RISK: Septic Shock documented but does not meet Sepsis 3 criteria. Prepare for potential claim denial.")
        
        return notes
