# Feature Dictionary

## Raw input features (25)

**Demographics:** `age`, `gender`, `marital_status`, `education` (ordinal)
**Employment/income:** `monthly_salary`, `employment_type`, `years_of_employment`, `company_type`
**Housing/family:** `house_type`, `monthly_rent`, `family_size`, `dependents`
**Monthly obligations:** `school_fees`, `college_fees`, `travel_expenses`, `groceries_utilities`, `other_monthly_expenses`
**Credit/status:** `existing_loans`, `current_emi_amount`, `credit_score`, `bank_balance`, `emergency_fund`
**Loan details:** `emi_scenario`, `requested_amount`, `requested_tenure`

## Derived features (9) — `add_derived_features()`

| Feature | Definition | Rationale |
|---|---|---|
| `total_monthly_expenses` | sum(rent, school/college fees, travel, groceries, other, current EMI) | Total monthly outflow |
| `disposable_income` | monthly_salary − total_monthly_expenses | Slack available for a new EMI |
| `expense_to_income` | total_monthly_expenses / monthly_salary | Spending pressure |
| `debt_to_income` | current_emi_amount / monthly_salary | Existing debt burden |
| `requested_to_income` | requested_amount / monthly_salary | Loan size vs earning power |
| `requested_to_balance` | requested_amount / bank_balance | Loan size vs liquidity |
| `emergency_fund_months` | emergency_fund / total_monthly_expenses | Months of runway |
| `affordability` | disposable_income / monthly_salary | Normalized headroom |
| `risk_score` | 0.5·credit_risk + 0.2·employment_newness + 0.3·DTI | Composite risk (higher = riskier) |

## Preprocessing pipeline (`build_preprocessor`)

One serializable sklearn `Pipeline` — trains and serves identically:

1. **derive** — `FunctionTransformer(add_derived_features)`
2. **prep** — `ColumnTransformer`:
   - *numeric* (raw + derived): median impute → `StandardScaler`
   - *categorical* (gender, marital_status, employment_type, company_type, house_type, existing_loans, emi_scenario): most-frequent impute → `OneHotEncoder(handle_unknown="ignore")`
   - *ordinal* (education): most-frequent impute → `OrdinalEncoder` (High School < Graduate < Post Graduate < Professional) → scale

**Output:** dense 49-column numeric matrix.

## Regression target note

Model **`log1p(max_monthly_emi)`** and back-transform (target is right-skewed with
26% of rows on the 500 floor — see [eda.md](eda.md)).
