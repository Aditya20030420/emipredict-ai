"""Central config: paths, feature lists, and data-quality bounds.

Values here reflect the ACTUAL dataset (404,800 rows x 27 cols) profiled on
2026-08-26, cross-checked against the project brief. Where the real data
diverges from the brief it is noted inline.
"""
from pathlib import Path

# --- Paths ---------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw" / "emi_prediction_dataset.csv"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
MLRUNS_DIR = ROOT / "mlruns"

# MLflow 3.x deprecated the file store; use SQLite backend (also required for
# the model registry). Artifacts default to ./mlartifacts.
MLFLOW_TRACKING_URI = f"sqlite:///{(ROOT / 'mlflow.db').as_posix()}"

# --- Targets -------------------------------------------------------------
TARGET_CLF = "emi_eligibility"          # 3 classes (imbalanced)
TARGET_REG = "max_monthly_emi"          # continuous, INR

# Class order (rarest last). Real distribution: Not_Eligible 77.3%,
# Eligible 18.4%, High_Risk 4.3% -> SEVERE imbalance. Lead with macro-F1
# and per-class recall (esp. High_Risk), not accuracy alone.
CLF_CLASSES = ["Not_Eligible", "Eligible", "High_Risk"]

# --- Columns needing cleaning before use ---------------------------------
# Stored as object dtype due to corrupted decimal suffixes e.g. "58.0.0",
# "64300.0.0.0". Strip to first valid float then cast numeric.
DIRTY_NUMERIC_COLS = ["age", "monthly_salary", "bank_balance"]

# gender has 8 raw variants -> collapse to Male / Female.
GENDER_MAP = {
    "male": "Male", "m": "Male",
    "female": "Female", "f": "Female",
}

# --- Feature groups (excludes targets) -----------------------------------
NUMERIC_FEATURES = [
    "age", "monthly_salary", "years_of_employment", "monthly_rent",
    "family_size", "dependents", "school_fees", "college_fees",
    "travel_expenses", "groceries_utilities", "other_monthly_expenses",
    "current_emi_amount", "credit_score", "bank_balance", "emergency_fund",
    "requested_amount", "requested_tenure",
]
CATEGORICAL_FEATURES = [
    "gender", "marital_status", "employment_type", "company_type",
    "house_type", "existing_loans", "emi_scenario",
]
ORDINAL_FEATURES = {
    "education": ["High School", "Graduate", "Post Graduate", "Professional"],
}

# Columns with missing values (impute): education, monthly_rent,
# credit_score, bank_balance, emergency_fund (~0.6% each).

# --- Data-quality bounds -------------------------------------------------
# Numeric plausible ranges (brief-documented; real max_monthly_emi exceeds
# the brief's 50K cap -> use as flag, not hard clip).
NUMERIC_BOUNDS = {
    "age": (25, 60),
    "credit_score": (300, 850),
    "monthly_salary": (15_000, 200_000),
    "max_monthly_emi": (500, 50_000),  # brief; real max ~91K (flag outliers)
}

# Per-scenario requested_amount / requested_tenure bounds (validate each
# emi_scenario separately; also a strong EDA angle).
SCENARIO_BOUNDS = {
    "E-commerce Shopping EMI": {"amount": (10_000, 200_000), "tenure": (3, 24)},
    "Home Appliances EMI":     {"amount": (20_000, 300_000), "tenure": (6, 36)},
    "Vehicle EMI":             {"amount": (80_000, 1_500_000), "tenure": (12, 84)},
    "Personal Loan EMI":       {"amount": (50_000, 1_000_000), "tenure": (12, 60)},
    "Education EMI":           {"amount": (50_000, 500_000), "tenure": (6, 48)},
}

# --- Category options (single source of truth for the app forms) ---------
CATEGORY_OPTIONS = {
    "gender": ["Male", "Female"],
    "marital_status": ["Single", "Married"],
    "employment_type": ["Private", "Government", "Self-employed"],
    "company_type": ["Large Indian", "MNC", "Mid-size", "Startup", "Small"],
    "house_type": ["Rented", "Own", "Family"],
    "existing_loans": ["No", "Yes"],
    "emi_scenario": list(SCENARIO_BOUNDS.keys()),
    "education": ORDINAL_FEATURES["education"],
}

# Sensible numeric defaults + (min, max, step) for app number inputs.
NUMERIC_INPUT_SPEC = {
    "age": (35, 25, 60, 1),
    "monthly_salary": (50_000, 5_000, 300_000, 1_000),
    "years_of_employment": (5, 0, 40, 1),
    "monthly_rent": (10_000, 0, 100_000, 500),
    "family_size": (3, 1, 12, 1),
    "dependents": (1, 0, 10, 1),
    "school_fees": (0, 0, 100_000, 500),
    "college_fees": (0, 0, 300_000, 1_000),
    "travel_expenses": (3_000, 0, 50_000, 500),
    "groceries_utilities": (8_000, 0, 100_000, 500),
    "other_monthly_expenses": (3_000, 0, 100_000, 500),
    "current_emi_amount": (0, 0, 100_000, 500),
    "credit_score": (700, 300, 850, 5),
    "bank_balance": (100_000, 0, 5_000_000, 5_000),
    "emergency_fund": (50_000, 0, 5_000_000, 5_000),
    "requested_amount": (200_000, 5_000, 1_500_000, 5_000),
    "requested_tenure": (24, 3, 84, 1),
}

# --- Human-readable field labels + help (for the app forms) --------------
FIELD_LABELS = {
    "age": "Age (years)",
    "gender": "Gender",
    "marital_status": "Marital status",
    "education": "Education level",
    "monthly_salary": "Monthly salary (₹)",
    "employment_type": "Employment type",
    "years_of_employment": "Years of employment",
    "company_type": "Company type",
    "house_type": "Housing",
    "monthly_rent": "Monthly rent (₹)",
    "family_size": "Family size",
    "dependents": "Dependents",
    "school_fees": "School fees (₹/month)",
    "college_fees": "College fees (₹/month)",
    "travel_expenses": "Travel expenses (₹/month)",
    "groceries_utilities": "Groceries & utilities (₹/month)",
    "other_monthly_expenses": "Other expenses (₹/month)",
    "existing_loans": "Has existing loans?",
    "current_emi_amount": "Current EMI paid (₹/month)",
    "credit_score": "Credit score (300–850)",
    "bank_balance": "Bank balance (₹)",
    "emergency_fund": "Emergency fund (₹)",
    "emi_scenario": "Loan purpose",
    "requested_amount": "Requested loan amount (₹)",
    "requested_tenure": "Repayment period (months)",
}

FIELD_HELP = {
    "monthly_salary": "Gross monthly income before deductions.",
    "years_of_employment": "Total work experience; higher usually means more stable.",
    "credit_score": "Creditworthiness. 300 is poor, 850 is excellent.",
    "current_emi_amount": "Total EMIs the applicant already pays each month.",
    "emergency_fund": "Savings set aside for emergencies.",
    "bank_balance": "Current account balance.",
    "requested_amount": "How much the applicant wants to borrow.",
    "requested_tenure": "Over how many months the loan is repaid.",
    "dependents": "People who rely on the applicant financially.",
    "house_type": "Rented, owned, or living with family.",
}

# One-line guidance shown under each form section.
GROUP_HELP = {
    "Demographics": "Basic personal details of the applicant.",
    "Employment & Income": "Where the money comes from and how stable it is.",
    "Housing & Family": "Living situation and household size.",
    "Monthly Obligations": "Recurring monthly costs the applicant already has.",
    "Credit & Status": "Credit history, savings, and existing debt.",
    "Loan Request": "What the applicant is applying for.",
}

# Plain-language meaning of each eligibility class.
ELIGIBILITY_MEANING = {
    "Eligible": "Low risk — the applicant can comfortably afford this EMI.",
    "High_Risk": "Marginal — approve only with caution (e.g. higher interest "
                 "rate, smaller amount, or longer tenure).",
    "Not_Eligible": "High risk — this loan is not recommended.",
}

# --- Split ---------------------------------------------------------------
RANDOM_STATE = 42
TEST_SIZE = 0.15
VAL_SIZE = 0.15  # of the full dataset -> 70/15/15

# --- Grading targets -----------------------------------------------------
TARGET_ACCURACY = 0.90       # classification (but watch macro-F1)
TARGET_RMSE = 2000           # regression, INR
