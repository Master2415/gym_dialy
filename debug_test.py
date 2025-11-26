from app import create_app

app = create_app()
app.secret_key = 'test_secret'
client = app.test_client()

with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['username'] = 'TEST_USER'

print("--- Testing /settings ---")
response = client.get('/settings')
print(f"Status: {response.status_code}")
if response.status_code == 500:
    print(response.data.decode('utf-8'))

print("\n--- Testing /exercises/new ---")
response = client.post('/exercises/new', data={
    'nombre': 'Test Debug',
    'grupo_muscular': 'Otro',
    'new_group_name': 'Debug Group'
}, follow_redirects=True)
print(f"Status: {response.status_code}")
if response.status_code == 500:
    print(response.data.decode('utf-8'))
