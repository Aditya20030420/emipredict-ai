# Data Quality Report

- Rows: **404,800**  |  Columns: **27**
- Duplicate rows: **0**

## Missing values
- `bank_balance`: 2,440 (0.60%)
- `monthly_rent`: 2,426 (0.60%)
- `credit_score`: 2,420 (0.60%)
- `education`: 2,404 (0.59%)
- `emergency_fund`: 2,351 (0.58%)

## Class balance (`emi_eligibility`)
- Not_Eligible: 77.29%
- Eligible: 18.39%
- High_Risk: 4.32%

## Out-of-range numeric values
- `age` outside [25, 60]: 0
- `credit_score` outside [300, 850]: 4,776
- `monthly_salary` outside [15,000, 200,000]: 10,065
- `max_monthly_emi` outside [500, 50,000]: 458

## Per-scenario `requested_amount` / `requested_tenure` violations
- E-commerce Shopping EMI (n=80,948): amount OOB 0, tenure OOB 0
- Home Appliances EMI (n=80,988): amount OOB 0, tenure OOB 0
- Vehicle EMI (n=80,942): amount OOB 0, tenure OOB 0
- Personal Loan EMI (n=80,980): amount OOB 0, tenure OOB 0
- Education EMI (n=80,942): amount OOB 0, tenure OOB 0
