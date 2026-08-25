from __future__ import annotations

import os

import requests
import streamlit as st

st.set_page_config(page_title='Intelligent Credit Underwriting', layout='wide')
API_URL = st.sidebar.text_input('FastAPI URL', os.getenv('API_URL', 'http://localhost:8000')).rstrip('/')
st.title('Intelligent Small Business Credit Underwriting Assistant')
st.caption('Gemini-assisted document intelligence + deterministic financial/risk/policy engines + human review')


def api(method: str, path: str, **kwargs):
    response = requests.request(method, f'{API_URL}{path}', timeout=120, **kwargs)
    if response.status_code >= 400:
        st.error(f'{response.status_code}: {response.text}')
        return None
    return response.json()


tab1, tab2, tab3 = st.tabs(['1. Create / Upload', '2. Analyze / Review', '3. What-if Simulator'])

with tab1:
    st.subheader('Create loan application')
    c1, c2, c3 = st.columns(3)
    business_name = c1.text_input('Business name', 'ABC Manufacturing Pvt Ltd')
    industry = c2.text_input('Industry', 'Manufacturing')
    vintage = c3.number_input('Business vintage (years)', min_value=0.0, value=7.0)
    c1, c2, c3 = st.columns(3)
    requested_amount = c1.number_input('Requested amount', min_value=1.0, value=5000000.0, step=100000.0)
    tenure = c2.number_input('Tenure months', min_value=1, value=60)
    rate = c3.number_input('Interest rate %', min_value=0.0, value=11.5)
    purpose = st.text_input('Purpose', 'Purchase of machinery')
    declared_revenue = st.number_input('Declared annual revenue', min_value=0.0, value=35000000.0)
    declared_debt = st.number_input('Declared existing debt/obligations', min_value=0.0, value=4000000.0)
    if st.button('Create application', type='primary'):
        payload = {
            'business_name': business_name, 'industry': industry, 'business_vintage_years': vintage,
            'declared_annual_revenue': declared_revenue, 'declared_existing_obligations': declared_debt,
            'loan_request': {'requested_amount': requested_amount, 'currency': 'INR', 'tenure_months': tenure,
                             'purpose': purpose, 'proposed_interest_rate': rate, 'collateral_offered': True},
            'consent_confirmed': True,
        }
        result = api('POST', '/applications', json=payload)
        if result:
            st.session_state['application_id'] = result['application_id']
            st.success(f"Created {result['application_id']}")

    app_id = st.text_input('Application ID', value=st.session_state.get('application_id', ''), key='upload_app_id')
    uploads = st.file_uploader('Upload bank/financial/tax/credit/loan/collateral files', accept_multiple_files=True,
                               type=['pdf','png','jpg','jpeg','txt','csv','json'])
    if st.button('Upload selected documents') and app_id and uploads:
        for item in uploads:
            result = api('POST', f'/applications/{app_id}/documents', files={'file': (item.name, item.getvalue(), item.type or 'application/octet-stream')})
            if result:
                st.write(f"✓ {item.name} → {result['document_id']}")

with tab2:
    app_id2 = st.text_input('Application ID', value=st.session_state.get('application_id', ''), key='analysis_app_id')
    if st.button('Run LangGraph underwriting workflow', type='primary') and app_id2:
        result = api('POST', f'/applications/{app_id2}/analyze')
        if result:
            st.success(f"Workflow recommendation: {result['status']}")
    if app_id2:
        bundle = api('GET', f'/applications/{app_id2}/analysis')
        if bundle:
            rec = bundle['recommendation']; risk = bundle['risk']; metrics = bundle['metrics']; policy = bundle['policy']
            a,b,c,d = st.columns(4)
            a.metric('Recommendation', rec['status'])
            b.metric('Risk grade', risk['risk_grade'])
            c.metric('Risk score', risk['score'])
            d.metric('Policy', policy['overall_result'])
            m1,m2,m3,m4 = st.columns(4)
            m1.metric('DSCR', metrics.get('dscr') or 'N/A')
            m2.metric('Debt / EBITDA', metrics.get('debt_to_ebitda') or 'N/A')
            m3.metric('Current ratio', metrics.get('current_ratio') or 'N/A')
            m4.metric('LTV', metrics.get('loan_to_value') or 'N/A')
            st.subheader('AI / grounded credit memo')
            st.info(rec['explanation'])
            st.subheader('Anomalies')
            st.json(bundle['anomalies'])
            st.subheader('Policy results')
            st.dataframe(policy['rules'], use_container_width=True)
            st.subheader('Evidence IDs')
            st.write(rec['evidence_ids'][:30])

            st.subheader('Human underwriter decision')
            action = st.selectbox('Action', ['APPROVE','CONDITIONALLY_APPROVE','REJECT','REQUEST_MORE_DOCUMENTS','ESCALATE','OVERRIDE_AI_RECOMMENDATION'])
            comments = st.text_area('Comments')
            override_reason = st.text_area('Override reason (required for override)')
            if st.button('Submit final decision'):
                result = api('POST', f'/applications/{app_id2}/decision', json={
                    'action': action, 'comments': comments or None, 'conditions': [], 'override_reason': override_reason or None
                }, headers={'X-User-ID':'demo-underwriter'})
                if result:
                    st.success(f"Decision recorded: {result['action']}")
            with st.expander('Audit trail'):
                trail = api('GET', f'/applications/{app_id2}/audit')
                if trail is not None:
                    st.dataframe(trail, use_container_width=True)

with tab3:
    app_id3 = st.text_input('Application ID', value=st.session_state.get('application_id', ''), key='sim_app_id')
    c1,c2,c3 = st.columns(3)
    sim_amount = c1.number_input('Scenario amount', min_value=1.0, value=4000000.0)
    sim_rate = c2.number_input('Scenario rate %', min_value=0.0, value=11.5)
    sim_tenure = c3.number_input('Scenario tenure months', min_value=1, value=60)
    if st.button('Run what-if simulation') and app_id3:
        result = api('POST', f'/applications/{app_id3}/simulate', json={
            'amount': sim_amount, 'currency':'INR', 'interest_rate': sim_rate, 'tenure_months': sim_tenure
        })
        if result:
            st.metric('Scenario EMI', result['emi'])
            st.metric('Scenario DSCR', result['metrics'].get('dscr') or 'N/A')
            st.metric('Scenario policy', result['policy_result'])
            st.metric('Scenario recommendation', result['recommendation'])
            st.json(result)
