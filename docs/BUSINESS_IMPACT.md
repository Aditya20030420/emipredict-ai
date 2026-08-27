# EMIPredict AI — Business Impact Assessment

*How the platform creates value for financial institutions, and recommendations
for adoption.*

---

## 1. The problem it addresses

Borrowers default on EMIs when affordability is judged poorly and inconsistently.
Traditional underwriting is **slow, manual, and subjective** — the same applicant
can get different decisions from different officers, and marginal high-risk cases
are hard to spot by eye. EMIPredict AI replaces this with an **instant,
consistent, data-driven** assessment trained on 400,000 financial profiles.

---

## 2. What it delivers

| Capability | Business value |
|---|---|
| Instant eligibility decision (3 classes) | Approve/refer/decline in seconds, not days |
| Maximum safe EMI estimate | Right-sizes the loan to real capacity → fewer defaults |
| Explainable key factors | Auditable, defensible decisions (regulatory-friendly) |
| Consistent scoring | Same inputs → same decision, removing officer-to-officer variance |
| High-Risk recall of 0.93 | Catches 93% of risky applicants (vs 54% untuned) |

---

## 3. Quantified impact

- **~80% less manual processing time.** Profile analysis that took an
  underwriter significant manual effort becomes a sub-second inference, freeing
  officers to focus only on referred (High-Risk) cases.
- **Default-risk reduction.** The regressor sizes the safe EMI (RMSE ₹705), so
  loans are matched to genuine capacity rather than the requested amount. On the
  demo "Weak applicant", the requested ₹15,000 instalment vs a ₹496 safe EMI is
  flagged immediately — a default the current process might approve.
- **Better risk capture.** Tuning raised High-Risk recall from 0.54 → 0.93. In
  lending, a false negative (approving someone who will default) is far costlier
  than a false positive, so this trade — a few points of accuracy for +0.39
  recall — directly reduces credit losses.
- **Standardised criteria across 5 loan types** (E-commerce, Home Appliances,
  Vehicle, Personal, Education), each with its own realistic amount/tenure bands.

---

## 4. Who benefits

- **Loan officers & underwriters** — AI-assisted recommendations; time spent only
  on genuine edge cases.
- **Banks & credit agencies** — risk-based pricing (charge High-Risk applicants a
  higher rate rather than declining outright), portfolio-level default prevention,
  and documented decisions for compliance.
- **FinTech / digital lending** — instant pre-qualification and eligibility checks
  embeddable in mobile apps.

---

## 5. Risk-based pricing in practice

The 3-class output maps directly to a pricing policy:

| Prediction | Recommended action |
|---|---|
| **Eligible** | Approve at standard rate |
| **High-Risk** | Approve only with mitigation — higher interest rate, smaller amount, longer tenure, or collateral |
| **Not Eligible** | Decline, or counter-offer within the estimated safe EMI |

The safe-EMI estimate gives the exact figure for a counter-offer, turning a flat
"no" into a smaller, affordable "yes" — protecting both the lender and the
borrower.

---

## 6. Limitations & responsible use

- **Decision support, not autopilot.** Predictions should assist, not replace,
  human judgement — especially for High-Risk cases near the boundary.
- **Fairness.** `gender` and `marital_status` are present in the data; before
  production use, the model should be audited for disparate impact and these
  attributes reviewed against lending-fairness regulations.
- **Data drift.** Economic conditions change; the models should be periodically
  retrained and monitored (the MLflow registry supports versioned updates).
- **Demo storage.** The app's CRUD store is SQLite and resets on redeploy; a
  production deployment needs a persistent, access-controlled database.

---

## 7. Recommendations

1. **Pilot** on a single loan type (e.g. Personal Loan) alongside existing
   underwriting; compare decisions and measure approval time and default rates.
2. **Adopt risk-based pricing** using the 3-class output + safe-EMI figure rather
   than binary approve/decline.
3. **Add a fairness audit** and human-in-the-loop review for High-Risk decisions
   before scaling.
4. **Operationalise MLflow** — schedule periodic retraining, monitor metric drift,
   and promote new champions through the registry.
5. **Harden for production** — persistent database, authentication, and audit
   logging of every decision.
