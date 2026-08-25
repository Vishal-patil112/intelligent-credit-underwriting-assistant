"""Run the complete synthetic workflow in-process.

No external FastAPI server is required.

When Gemini is configured, the workflow uses Gemini for supported AI tasks.
When Gemini is unavailable, deterministic fallback logic is used.

"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient

from app.db.session import reset_database
from app.main import app

PAYLOAD = {
    'business_name':'ABC Manufacturing Pvt Ltd', 'business_type':'PRIVATE_LIMITED', 'industry':'Manufacturing',
    'business_vintage_years':7, 'registration_number':'DEMO-REG-001', 'tax_identifier':'DEMO-TAX-001',
    'declared_annual_revenue':35000000, 'declared_existing_obligations':4000000,
    'loan_request':{'requested_amount':5000000,'currency':'INR','tenure_months':60,'purpose':'Purchase of machinery',
                    'proposed_interest_rate':11.5,'collateral_offered':True},
    'consent_confirmed':True,
}


def main():
    reset_database()
    with TestClient(app) as client:
        app_response = client.post('/applications', json=PAYLOAD)
        app_response.raise_for_status()
        application_id = app_response.json()['application_id']
        print('Application:', application_id)
        folder = Path(__file__).resolve().parents[1] / 'data' / 'synthetic' / 'strong_case'
        for path in sorted(folder.glob('*.txt')):
            with path.open('rb') as handle:
                response = client.post(f'/applications/{application_id}/documents', files={'file':(path.name, handle, 'text/plain')})
            response.raise_for_status(); print('Uploaded:', path.name)
        response = client.post(f'/applications/{application_id}/analyze'); response.raise_for_status()
        print('Workflow:', response.json()['status'])
        bundle = client.get(f'/applications/{application_id}/analysis').json()
        print('Risk:', bundle['risk']['score'], bundle['risk']['risk_grade'])
        print('Policy:', bundle['policy']['overall_result'])
        print('Recommendation:', bundle['recommendation']['status'])
        print('DSCR:', bundle['metrics']['dscr'])
        print('Human review required:', bundle['recommendation']['requires_human_review'])
        decision = client.post(f'/applications/{application_id}/decision', headers={'X-User-ID':'demo-underwriter'},
                               json={'action':'APPROVE','comments':'Synthetic demo approval after evidence review','conditions':[],'override_reason':None})
        decision.raise_for_status(); print('Final human action:', decision.json()['action'])
        print('E2E_DEMO_OK')

if __name__ == '__main__':
    main()
