from pathlib import Path
from fastapi.testclient import TestClient

from app.db.session import reset_database
from app.main import app

PAYLOAD = {
    'business_name':'ABC Manufacturing Pvt Ltd','business_type':'PRIVATE_LIMITED','industry':'Manufacturing',
    'business_vintage_years':7,'registration_number':'DEMO-REG-001','tax_identifier':'DEMO-TAX-001',
    'declared_annual_revenue':35000000,'declared_existing_obligations':4000000,
    'loan_request':{'requested_amount':5000000,'currency':'INR','tenure_months':60,'purpose':'Purchase of machinery','proposed_interest_rate':11.5,'collateral_offered':True},
    'consent_confirmed':True,
}


def test_complete_underwriting_flow():
    reset_database()
    with TestClient(app) as client:
        created = client.post('/applications', json=PAYLOAD)
        assert created.status_code == 201
        aid = created.json()['application_id']
        folder = Path(__file__).resolve().parents[1] / 'data' / 'synthetic' / 'strong_case'
        for path in sorted(folder.glob('*.txt')):
            with path.open('rb') as f:
                response = client.post(f'/applications/{aid}/documents', files={'file':(path.name,f,'text/plain')})
            assert response.status_code == 201
        analyzed = client.post(f'/applications/{aid}/analyze')
        assert analyzed.status_code == 200
        bundle = client.get(f'/applications/{aid}/analysis').json()
        assert bundle['policy']['overall_result'] == 'PASS'
        assert bundle['recommendation']['status'] == 'APPROVE'
        assert bundle['recommendation']['requires_human_review'] is True
        assert float(bundle['risk']['score']) >= 80
        assert float(bundle['metrics']['dscr']) > 1.2
        assert bundle['recommendation']['evidence_ids']

        simulation = client.post(f'/applications/{aid}/simulate', json={'amount':4000000,'currency':'INR','interest_rate':11.5,'tenure_months':60})
        assert simulation.status_code == 200
        assert float(simulation.json()['emi']) > 0

        final = client.post(f'/applications/{aid}/decision', headers={'X-User-ID':'tester'},
                            json={'action':'APPROVE','comments':'Reviewed synthetic evidence','conditions':[],'override_reason':None})
        assert final.status_code == 200
        assert final.json()['action'] == 'APPROVE'
        audit = client.get(f'/applications/{aid}/audit').json()
        assert any(x['event_type'] == 'FINAL_DECISION' for x in audit)


def test_duplicate_document_rejected():
    reset_database()
    with TestClient(app) as client:
        aid = client.post('/applications', json=PAYLOAD).json()['application_id']
        content = b'BANK STATEMENT\nAverage Monthly Inflow: 100000'
        one = client.post(f'/applications/{aid}/documents', files={'file':('bank.txt',content,'text/plain')})
        two = client.post(f'/applications/{aid}/documents', files={'file':('bank_copy.txt',content,'text/plain')})
        assert one.status_code == 201
        assert two.status_code == 409
