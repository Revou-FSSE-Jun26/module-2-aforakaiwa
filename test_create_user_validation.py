"""Quick validation script for task 3.1 - create_user route changes."""
import sys
sys.path.insert(0, '.')
from app import create_app
from utils import db
from models import User

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['TESTING'] = True

with app.app_context():
    db.create_all()
    client = app.test_client()

    # Test 1: Missing password field
    resp = client.post('/users', json={'username': 'test', 'full_name': 'Test User', 'email': 'test@test.com'})
    assert resp.status_code == 400, f'Expected 400, got {resp.status_code}'
    assert 'Missing required field' in resp.get_json()['error']
    print('PASS: Missing password returns 400')

    # Test 2: Empty password field
    resp = client.post('/users', json={'username': 'test', 'full_name': 'Test User', 'email': 'test@test.com', 'password': ''})
    assert resp.status_code == 400, f'Expected 400, got {resp.status_code}'
    print('PASS: Empty password returns 400')

    # Test 3: Password too short
    resp = client.post('/users', json={'username': 'test', 'full_name': 'Test User', 'email': 'test@test.com', 'password': 'short'})
    assert resp.status_code == 400, f'Expected 400, got {resp.status_code}'
    assert 'Password must be at least 8 characters long' in resp.get_json()['error']
    print('PASS: Short password returns 400 with correct message')

    # Test 4: Valid registration
    resp = client.post('/users', json={'username': 'testuser', 'full_name': 'Test User', 'email': 'test@test.com', 'password': 'securepass123'})
    assert resp.status_code == 201, f'Expected 201, got {resp.status_code}: {resp.get_json()}'
    data = resp.get_json()
    assert 'password_hash' not in data['user'], 'password_hash should not be in response'
    assert data['message'] == 'User registered successfully'
    print('PASS: Valid registration returns 201 with no password_hash in response')

    # Test 5: Verify hash is stored as bcrypt
    user = User.query.filter_by(username='testuser').first()
    assert user.password_hash.startswith('$2b$'), f'Hash does not start with $2b$: {user.password_hash}'
    assert user.check_password('securepass123'), 'check_password should return True for correct password'
    print('PASS: Password hash is valid bcrypt and check_password works')

    # Test 6: Duplicate user
    resp = client.post('/users', json={'username': 'testuser', 'full_name': 'Test User 2', 'email': 'test2@test.com', 'password': 'securepass123'})
    assert resp.status_code == 409, f'Expected 409, got {resp.status_code}'
    assert 'Username or email already exists' in resp.get_json()['error']
    print('PASS: Duplicate username returns 409')

    print('\nAll tests passed!')
