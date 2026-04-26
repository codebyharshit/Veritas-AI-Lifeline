"""Mock data for local API testing when Databricks is not available."""

# Sample facilities with realistic Indian healthcare data
MOCK_FACILITIES = [
    {
        "facility_id": "f001",
        "facility_name": "Apollo Hospital Delhi",
        "state": "Delhi",
        "district": "New Delhi",
        "pin_code": "110001",
        "latitude": 28.5672,
        "longitude": 77.2100,
        "facility_type": "Hospital",
        "bed_count": 500,
        "unstructured_notes": "Multi-specialty hospital with 24/7 emergency services. Equipped with advanced cardiac care unit, neurology department, and oncology center. Has 50 ICU beds with ventilator support.",
    },
    {
        "facility_id": "f002",
        "facility_name": "Fortis Hospital Mumbai",
        "state": "Maharashtra",
        "district": "Mumbai",
        "pin_code": "400001",
        "latitude": 19.0176,
        "longitude": 72.8562,
        "facility_type": "Hospital",
        "bed_count": 300,
        "unstructured_notes": "Leading healthcare provider with specialization in cardiac surgery and orthopedics. 24/7 trauma center available. Dialysis unit with 20 machines.",
    },
    {
        "facility_id": "f003",
        "facility_name": "AIIMS Patna",
        "state": "Bihar",
        "district": "Patna",
        "pin_code": "801507",
        "latitude": 25.6093,
        "longitude": 85.1376,
        "facility_type": "Government Hospital",
        "bed_count": 750,
        "unstructured_notes": "Premier government medical institute. Emergency surgery available. Limited staff on weekends. Oncology department under construction.",
    },
    {
        "facility_id": "f004",
        "facility_name": "City Care Clinic",
        "state": "Rajasthan",
        "district": "Jaipur",
        "pin_code": "302001",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "facility_type": "Clinic",
        "bed_count": 20,
        "unstructured_notes": "Small clinic offering dental and dermatology services. Dr. Sharma available Mon-Sat. X-ray machine under repair.",
    },
    {
        "facility_id": "f005",
        "facility_name": "Rural Health Center Varanasi",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "pin_code": "221001",
        "latitude": 25.3176,
        "longitude": 82.9739,
        "facility_type": "Primary Health Center",
        "bed_count": 30,
        "unstructured_notes": "Basic healthcare services for rural population. Maternity ward available. No surgical facilities. Nearest emergency surgery 85km away.",
    },
    {
        "facility_id": "f006",
        "facility_name": "CMC Vellore",
        "state": "Tamil Nadu",
        "district": "Vellore",
        "pin_code": "632004",
        "latitude": 12.9249,
        "longitude": 79.1325,
        "facility_type": "Hospital",
        "bed_count": 2700,
        "unstructured_notes": "One of India's premier medical institutions. Multi-organ transplant facility. Advanced neurosurgery and cardiology departments. 24/7 emergency services with trauma center.",
    },
    {
        "facility_id": "f007",
        "facility_name": "Manipal Hospital Bangalore",
        "state": "Karnataka",
        "district": "Bangalore",
        "pin_code": "560017",
        "latitude": 12.9352,
        "longitude": 77.6245,
        "facility_type": "Hospital",
        "bed_count": 600,
        "unstructured_notes": "Multi-specialty hospital with robotic surgery capabilities. Oncology center with radiation therapy. Pediatric ICU with 20 beds.",
    },
    {
        "facility_id": "f008",
        "facility_name": "District Hospital Muzaffarpur",
        "state": "Bihar",
        "district": "Muzaffarpur",
        "pin_code": "842001",
        "latitude": 26.1209,
        "longitude": 85.3647,
        "facility_type": "Government Hospital",
        "bed_count": 200,
        "unstructured_notes": "Government district hospital. Basic emergency services. No dialysis facility. Nearest dialysis center 120km away in Patna.",
    },
]

# Sample trust scores with debate transcripts
MOCK_TRUST_SCORES = {
    "f001": {
        "trust_score": 85,
        "advocate_argument": "Apollo Hospital Delhi demonstrates strong healthcare capabilities with comprehensive multi-specialty services. The facility has '24/7 emergency services' as stated in their notes, supported by '50 ICU beds with ventilator support.' The presence of advanced cardiac care, neurology, and oncology departments indicates a well-equipped tertiary care center.",
        "skeptic_argument": "While the facility claims comprehensive services, I found some gaps: The notes mention advanced departments but don't specify the number of specialists available. -5 points for unverified specialist count. The bed count of 500 seems adequate but ICU ratio (50/500 = 10%) is on the lower end for a multi-specialty hospital. -5 points. No mention of accreditation status. -5 points.",
        "judge_reasoning": "Apollo Hospital Delhi shows strong evidence of comprehensive care capabilities. The advocate's points about 24/7 emergency and ICU capacity are well-supported. The skeptic raises valid concerns about specialist verification and accreditation, but these are minor gaps. Score: 85/100 - a trustworthy facility with minor documentation gaps.",
    },
    "f002": {
        "trust_score": 78,
        "advocate_argument": "Fortis Hospital Mumbai is a leading healthcare provider with clear specializations in cardiac surgery and orthopedics. The '24/7 trauma center' claim is significant for emergency care. The dialysis unit with 20 machines shows investment in critical care infrastructure.",
        "skeptic_argument": "The facility claims cardiac surgery specialization but doesn't list any cardiac surgeons by name. -8 points. 'Leading healthcare provider' is a vague claim without supporting evidence. -5 points. The bed count of 300 seems low for the range of services claimed. -4 points. Dialysis capacity is good.",
        "judge_reasoning": "Fortis Mumbai has solid infrastructure claims but lacks specific evidence for its surgical capabilities. The dialysis unit is well-documented. Score: 78/100 - reliable for dialysis and trauma, verify cardiac surgery capabilities before referral.",
    },
    "f003": {
        "trust_score": 62,
        "advocate_argument": "AIIMS Patna is a premier government medical institute with a large 750-bed capacity. Emergency surgery is available, indicating surgical capabilities. As a government institution, it serves a critical role in Bihar's healthcare infrastructure.",
        "skeptic_argument": "Major concerns: 'Limited staff on weekends' directly contradicts emergency surgery availability claims. -15 points for this critical gap. 'Oncology department under construction' means cancer care is not actually available. -10 points for misleading capability claim. Government hospitals often face resource constraints not mentioned here. -8 points.",
        "judge_reasoning": "AIIMS Patna has significant credibility issues. The weekend staffing limitation is a serious concern for emergency care. The oncology claim is misleading since the department is incomplete. Score: 62/100 - use for weekday emergencies only, verify oncology status before referral.",
    },
    "f004": {
        "trust_score": 45,
        "advocate_argument": "City Care Clinic provides specialized dental and dermatology services. Dr. Sharma's availability Mon-Sat indicates consistent care. The clinic serves a focused niche rather than attempting to be a general hospital.",
        "skeptic_argument": "The facility claims to be a clinic but only has 20 beds, which is unusual for a dental/dermatology practice. -5 points for unclear facility type. 'X-ray machine under repair' means diagnostic capabilities are compromised. -15 points. No mention of qualifications or specializations for Dr. Sharma. -10 points. Very limited scope of services. -10 points.",
        "judge_reasoning": "City Care Clinic has significant gaps between claims and evidence. The non-functional X-ray is a major concern. Limited information about practitioner qualifications. Score: 45/100 - suitable only for minor dental/skin consultations, not reliable for diagnostics.",
    },
    "f005": {
        "trust_score": 55,
        "advocate_argument": "Rural Health Center Varanasi honestly states its limitations and serves the rural population with basic healthcare. The maternity ward availability is valuable for the community. The facility is transparent about lacking surgical facilities.",
        "skeptic_argument": "The facility acknowledges 'nearest emergency surgery 85km away' which is a medical desert situation. -20 points for access gap. 'No surgical facilities' severely limits emergency response capability. -15 points. Only 30 beds for a rural area suggests capacity constraints. -5 points.",
        "judge_reasoning": "This facility is honest about its limitations, which is commendable. However, the 85km distance to emergency surgery is a critical gap for the community. Score: 55/100 - good for basic care and maternity, but patients needing surgery face serious access challenges.",
    },
    "f006": {
        "trust_score": 92,
        "advocate_argument": "CMC Vellore is one of India's most prestigious medical institutions with an extraordinary 2700-bed capacity. Multi-organ transplant facility indicates highest-level surgical capabilities. The combination of advanced neurosurgery, cardiology, and 24/7 trauma services makes this a comprehensive tertiary care center.",
        "skeptic_argument": "The claims are strong but the facility's reputation is well-documented externally. Minor point: specific department capacities not listed. -3 points. No mention of waiting times which can be significant at such institutions. -5 points.",
        "judge_reasoning": "CMC Vellore's reputation is well-established and the claims align with known capabilities. The facility demonstrates comprehensive high-end care. Minor gaps in operational details don't significantly impact trustworthiness. Score: 92/100 - highly trustworthy for complex medical needs.",
    },
}

# Sample contradictions
MOCK_CONTRADICTIONS = {
    "f003": [
        {
            "claim": "Emergency surgery available",
            "evidence_gap": "Limited staff on weekends contradicts 24/7 surgical capability",
            "trust_impact": -15,
            "severity": "high",
        },
        {
            "claim": "Oncology center",
            "evidence_gap": "Department is under construction, not operational",
            "trust_impact": -10,
            "severity": "high",
        },
    ],
    "f004": [
        {
            "claim": "Diagnostic services",
            "evidence_gap": "X-ray machine under repair",
            "trust_impact": -15,
            "severity": "medium",
        },
    ],
    "f005": [
        {
            "claim": "Healthcare access",
            "evidence_gap": "Nearest emergency surgery 85km away - medical desert",
            "trust_impact": -20,
            "severity": "high",
        },
    ],
}

# Sample structured extractions
MOCK_STRUCTURED = {
    "f001": {
        "verified_capabilities": [
            {"capability": "Emergency Surgery", "confidence": 0.9, "evidence_sentence": "24/7 emergency services with advanced cardiac care unit"},
            {"capability": "Cardiac Care", "confidence": 0.95, "evidence_sentence": "advanced cardiac care unit"},
            {"capability": "Neurology", "confidence": 0.85, "evidence_sentence": "neurology department"},
            {"capability": "Oncology", "confidence": 0.85, "evidence_sentence": "oncology center"},
            {"capability": "ICU", "confidence": 0.95, "evidence_sentence": "50 ICU beds with ventilator support"},
        ],
        "staff": [
            {"role": "Cardiologist", "specialty": "Cardiac Surgery"},
            {"role": "Neurologist", "specialty": "Neurosurgery"},
            {"role": "Oncologist", "specialty": "Medical Oncology"},
        ],
        "equipment": [
            {"item": "Ventilator", "quantity": 50, "functional": True},
            {"item": "CT Scanner", "functional": True},
            {"item": "MRI Machine", "functional": True},
        ],
    },
    "f002": {
        "verified_capabilities": [
            {"capability": "Cardiac Surgery", "confidence": 0.85, "evidence_sentence": "specialization in cardiac surgery"},
            {"capability": "Orthopedics", "confidence": 0.9, "evidence_sentence": "specialization in orthopedics"},
            {"capability": "Trauma Care", "confidence": 0.95, "evidence_sentence": "24/7 trauma center available"},
            {"capability": "Dialysis", "confidence": 0.95, "evidence_sentence": "Dialysis unit with 20 machines"},
        ],
        "staff": [
            {"role": "Orthopedic Surgeon", "specialty": "Joint Replacement"},
            {"role": "Trauma Specialist", "specialty": "Emergency Medicine"},
        ],
        "equipment": [
            {"item": "Dialysis Machine", "quantity": 20, "functional": True},
            {"item": "X-Ray", "functional": True},
        ],
    },
    "f003": {
        "verified_capabilities": [
            {"capability": "Emergency Surgery", "confidence": 0.6, "evidence_sentence": "Emergency surgery available"},
            {"capability": "Oncology", "confidence": 0.3, "evidence_sentence": "Oncology department under construction"},
        ],
        "staff": [],
        "equipment": [],
    },
}

# Sample geo lookup data
MOCK_GEO_LOOKUP = [
    {"pin_code": "110001", "capability": "emergency_surgery", "nearest_facility_id": "f001", "distance_km": 2.3, "desert_severity": "green", "nearest_trust_score": 85},
    {"pin_code": "110001", "capability": "dialysis", "nearest_facility_id": "f002", "distance_km": 45.0, "desert_severity": "green", "nearest_trust_score": 78},
    {"pin_code": "400001", "capability": "emergency_surgery", "nearest_facility_id": "f002", "distance_km": 1.5, "desert_severity": "green", "nearest_trust_score": 78},
    {"pin_code": "400001", "capability": "dialysis", "nearest_facility_id": "f002", "distance_km": 1.5, "desert_severity": "green", "nearest_trust_score": 78},
    {"pin_code": "801507", "capability": "emergency_surgery", "nearest_facility_id": "f003", "distance_km": 5.0, "desert_severity": "green", "nearest_trust_score": 62},
    {"pin_code": "801507", "capability": "oncology", "nearest_facility_id": "f006", "distance_km": 180.0, "desert_severity": "red", "nearest_trust_score": 92},
    {"pin_code": "221001", "capability": "emergency_surgery", "nearest_facility_id": "f003", "distance_km": 85.0, "desert_severity": "yellow", "nearest_trust_score": 62},
    {"pin_code": "221001", "capability": "dialysis", "nearest_facility_id": "f002", "distance_km": 120.0, "desert_severity": "red", "nearest_trust_score": 78},
    {"pin_code": "842001", "capability": "dialysis", "nearest_facility_id": "f003", "distance_km": 120.0, "desert_severity": "red", "nearest_trust_score": 62},
    {"pin_code": "842001", "capability": "emergency_surgery", "nearest_facility_id": "f008", "distance_km": 5.0, "desert_severity": "green", "nearest_trust_score": 55},
]

# Helper function to check if we're running locally
def is_local_mode():
    """Check if running locally (no PySpark available)."""
    try:
        from pyspark.sql import SparkSession
        return False
    except ImportError:
        return True
