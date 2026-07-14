# Sepsis CDI Expert Training System

A web-based training platform for Clinical Documentation Integrity (CDI) professionals using the **Sepsis 2 & Sepsis 3 dual-criteria framework**.

## Overview

This system generates realistic mock sepsis cases at three difficulty levels and automatically grades trainee responses using a comprehensive 100-point rubric. It's designed for:

- **CDI Teams** — Training and competency validation
- **Residency Programs** — Sepsis documentation curriculum
- **Hospital Systems** — Standardized CDI education
- **Self-Paced Learning** — Individual skill development

## Features

✅ **Mock Case Generation**
- 3 difficulty levels (Straightforward, Intermediate, Advanced)
- 9 case types (missed severity, denial trap, undocumented, misdocumented, etc.)
- Randomized infection sources (pneumonia, urosepsis, bloodstream, surgical site, intra-abdominal)
- Realistic patient demographics, vitals, labs, and clinical timelines

✅ **Dual-Criteria Framework**
- **Sepsis 2 (CMS Standard)** — SIRS-based criteria with organ dysfunction indicators
- **Sepsis 3 (Current Standard)** — SOFA/qSOFA-based criteria
- Validates cases against both standards; flags when documentation meets only one

✅ **Automated Grading**
- 100-point rubric across 5 sections:
  - Sepsis 2 Assessment (25 pts)
  - Sepsis 3 Assessment (25 pts)
  - Documentation Status (25 pts)
  - Recommendations (15 pts)
  - Clinical Reasoning (10 pts)
- Instant feedback with section-by-section breakdown
- Identifies strengths and areas for improvement

✅ **Instructor Tools**
- Answer keys for each case
- Teaching points and clinical pearls
- Regulatory implications and CDI actions

## Quick Start

### Deploy to Streamlit Cloud (Recommended)

1. **Fork or clone this repository**
```bash
   git clone https://github.com/YOUR_USERNAME/sepsis-cdi-training.git
   cd sepsis-cdi-training
