import streamlit as st
from sepsis_case_generator import SepsisCaseGenerator
from sepsis_grading_engine import SepsisGradingEngine
import json

# Page config
st.set_page_config(
    page_title="Sepsis CDI Expert Training",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'case_data' not in st.session_state:
    st.session_state.case_data = None
if 'grading_report' not in st.session_state:
    st.session_state.grading_report = None

# Title
st.title("🏥 Sepsis CDI Expert Training System")
st.markdown("**Dual-Criteria Framework: Sepsis 2 & Sepsis 3**")

# Sidebar: Case Generation
with st.sidebar:
    st.header("📋 Generate Case")
    
    difficulty = st.selectbox(
        "Difficulty Level",
        ["Level 1 (Straightforward)", "Level 2 (Intermediate)", "Level 3 (Advanced)"]
    )
    
    case_type = st.selectbox(
        "Case Type",
        [
            "Random Mix",
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
    )
    
    infection_source = st.selectbox(
        "Infection Source",
        ["Random", "Pneumonia", "Urosepsis", "Bloodstream", "Surgical Site", "Intra-abdominal"]
    )
    
    include_answer_key = st.checkbox("Include Answer Key", value=True)
    include_teaching_points = st.checkbox("Include Teaching Points", value=True)
    
    if st.button("🎲 Generate Case", use_container_width=True):
        generator = SepsisCaseGenerator()
        st.session_state.case_data = generator.generate_case(
            difficulty=difficulty.split()[1].strip("()"),
            case_type=case_type,
            infection_source=infection_source,
            include_answer_key=include_answer_key,
            include_teaching_points=include_teaching_points
        )
        st.session_state.grading_report = None
        st.rerun()

# Main content
if st.session_state.case_data:
    case = st.session_state.case_data
    
    # Case header
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Case ID", case['case_id'])
    with col2:
        st.metric("Difficulty", case['difficulty_level'])
    with col3:
        st.metric("Type", case['case_type'])
    with col4:
        st.metric("Hospital Day", case['hospital_day'])
    
    st.divider()
    
    # Case presentation
    st.header("📝 Case Presentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Patient Demographics")
        st.write(f"**Name:** {case['patient_name']}")
        st.write(f"**Age:** {case['age']} years")
        st.write(f"**Sex:** {case['sex']}")
        st.write(f"**Admission Date:** {case['admission_date']}")
        st.write(f"**Comorbidities:** {', '.join(case['comorbidities'])}")
    
    with col2:
        st.subheader("Vital Signs")
        st.write(f"**Temperature:** {case['vitals']['temperature']}°C")
        st.write(f"**Heart Rate:** {case['vitals']['heart_rate']} bpm")
        st.write(f"**Respiratory Rate:** {case['vitals']['respiratory_rate']} breaths/min")
        st.write(f"**Blood Pressure:** {case['vitals']['blood_pressure']} mmHg")
        st.write(f"**MAP:** {case['vitals']['map']} mmHg")
        st.write(f"**GCS:** {case['vitals']['gcs']}")
    
    st.subheader("Clinical Timeline")
    st.info(case['clinical_timeline'])
    
    st.subheader("Laboratory Values")
    lab_cols = st.columns(4)
    labs = case['labs']
    lab_items = [
        ("WBC", f"{labs['wbc']} K/µL"),
        ("Lactate", f"{labs['lactate']} mmol/L"),
        ("Creatinine", f"{labs['creatinine']} mg/dL"),
        ("Bilirubin", f"{labs['bilirubin']} mg/dL"),
        ("Platelets", f"{labs['platelets']} K/µL"),
        ("INR", f"{labs['inr']}"),
        ("aPTT", f"{labs['aptt']} sec"),
        ("PaO₂/FiO₂", f"{labs['pao2_fio2']}")
    ]
    
    for idx, (label, value) in enumerate(lab_items):
        with lab_cols[idx % 4]:
            st.metric(label, value)
    
    st.subheader("Imaging & Diagnostics")
    st.write(case['imaging_findings'])
    
    st.subheader("Medications & Interventions")
    st.write(case['interventions'])
    
    st.subheader("Provider Documentation (From Chart)")
    st.warning(case['documented_diagnoses'])
    
    st.divider()
    
    # Trainee assessment
    st.header("✍️ Your Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sepsis2_answer = st.selectbox(
            "1. Sepsis 2 Classification",
            ["Select...", "Sepsis", "Severe Sepsis", "Septic Shock", "Not Sepsis 2"],
            key="sepsis2"
        )
    
    with col2:
        sepsis3_answer = st.selectbox(
            "2. Sepsis 3 Classification",
            ["Select...", "Sepsis", "Septic Shock", "Not Sepsis 3"],
            key="sepsis3"
        )
    
    doc_status = st.selectbox(
        "3. Documentation Status",
        ["Select...", "Correctly Documented", "Misdocumented", "Unsupported", "Undocumented", "Incomplete/Ambiguous"],
        key="doc_status"
    )
    
    recommendations = st.text_area(
        "4. Recommendations (CDI Action)",
        placeholder="What CDI action would you recommend?",
        height=100,
        key="recommendations"
    )
    
    clinical_reasoning = st.text_area(
        "5. Clinical Reasoning",
        placeholder="Explain your assessment and reasoning...",
        height=120,
        key="clinical_reasoning"
    )
    
    if st.button("📊 Submit & Grade", use_container_width=True):
        if sepsis2_answer == "Select..." or sepsis3_answer == "Select..." or doc_status == "Select...":
            st.error("Please complete all required fields before submitting.")
        else:
            # Grade the response
            grading_engine = SepsisGradingEngine(case)
            trainee_response = {
                "sepsis2_classification": sepsis2_answer,
                "sepsis3_classification": sepsis3_answer,
                "documentation_status": doc_status,
                "recommendations": recommendations,
                "clinical_reasoning": clinical_reasoning
            }
            st.session_state.grading_report = grading_engine.grade(trainee_response)
            st.rerun()
    
    st.divider()
    
    # Grading report
    if st.session_state.grading_report:
        report = st.session_state.grading_report
        
        st.header("📊 Grading Report")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Score", f"{report['total_score']}/100")
        with col2:
            st.metric("Percentage", f"{report['percentage']:.1f}%")
        with col3:
            grade_color = "🟢" if report['letter_grade'] in ['A', 'B'] else "🟡" if report['letter_grade'] == 'C' else "🔴"
            st.metric("Grade", f"{grade_color} {report['letter_grade']}")
        with col4:
            st.metric("Status", "Pass" if report['percentage'] >= 70 else "Review")
        
        st.divider()
        
        # Detailed feedback
        with st.expander("📋 Detailed Feedback", expanded=True):
            for section, feedback in report['section_feedback'].items():
                st.subheader(section)
                st.write(f"**Score:** {feedback['score']}/{feedback['max_points']}")
                st.write(f"**Feedback:** {feedback['feedback']}")
        
        # Strengths
        st.subheader("✅ Strengths")
        for strength in report['strengths']:
            st.write(f"• {strength}")
        
        # Areas for improvement
        st.subheader("📈 Areas for Improvement")
        for area in report['areas_for_improvement']:
            st.write(f"• {area}")
        
        # Answer key (if included)
        if case.get('answer_key'):
            with st.expander("🔑 Answer Key (Instructor Only)"):
                st.json(case['answer_key'])
        
        # Teaching points (if included)
        if case.get('teaching_points'):
            with st.expander("📚 Teaching Points (Instructor Only)"):
                for point in case['teaching_points']:
                    st.write(f"• {point}")

else:
    st.info("👈 Generate a case from the sidebar to begin training.")
