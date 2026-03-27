# AI-Assisted Store-to-Corporate Exception Resolution Workflow System (Flask)

## Run locally (VS Code friendly)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python run.py
```

Base URL: `http://127.0.0.1:5000`

## Seeded users

- `store_mgr / password123` (STORE_MANAGER)
- `regional_mgr / password123` (REGIONAL_MANAGER)
- `finance_user / password123` (FINANCE)
- `supply_user / password123` (SUPPLY_CHAIN)
- `audit_user / password123` (AUDIT)

## Implemented APIs

- Auth: `/api/auth/login`, `/api/auth/me`
- Exceptions: list/get/create/update/submit + timeline + per-exception opportunities
- Approvals: pending approvals + action endpoint
- Comments: list/add comments
- Attachments: list/add attachments
- Opportunities: list all opportunities
- AI (simulated): improve justification, summary generation, missing field check

## Notes

- Uses SQLite via SQLAlchemy.
- Only the required 9 tables are used.
- Enums are stored as TEXT values.
- Full activity timeline is recorded in `activity_logs`.
- Opportunity insights are auto-generated at submission via rules in `OpportunityService`.
- SQLite foreign-key checks are enabled at connection level in the Flask app.
- For governance, only `STORE_MANAGER` can create exceptions; only the owner can update/submit.
