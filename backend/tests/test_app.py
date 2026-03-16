import pytest
import os
import json
from backend.app import app
from backend.document_parser import extract_text
from backend.nlp_engine.analyzer import analyze_contract

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'test_uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.test_client() as client:
        yield client
    # Cleanup
    import shutil
    shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)

def test_health(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'healthy'
    assert 'features' in data

def test_register(client):
    rv = client.post('/register', json={'api_key': 'testkey123'})
    assert rv.status_code == 201

def test_login(client):
    client.post('/register', json={'api_key': 'testlogin'})
    rv = client.post('/login', json={'api_key': 'testlogin'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'access_token' in data

def test_upload_no_file(client):
    rv = client.post('/upload')
    assert rv.status_code == 400

def test_ml_analysis():
    # Test analyzer with mock text
    text = "external call transfer balance"
    result = analyze_contract(text)
    assert 'reentrancy_risk' in result['clauses_detected']
    assert result['risk_score'] > 0

if __name__ == '__main__':
    pytest.main([__file__])

