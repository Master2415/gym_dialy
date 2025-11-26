import unittest
from app import create_app
from app.db import get_connection

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.secret_key = 'test_secret'
        self.client = self.app.test_client()
        
        # Create test user
        self.conn = get_connection()
        self.cur = self.conn.cursor()
        self.cur.execute("INSERT INTO users (username, password, full_name, email) VALUES ('TEST_USER', 'hash', 'Test User', 'test@example.com')")
        self.conn.commit()
        self.user_id = self.cur.lastrowid
        
        # Mock session
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
            sess['username'] = 'TEST_USER'

    def tearDown(self):
        # Clean up user (and cascading data)
        self.cur.execute("DELETE FROM users WHERE id=%s", (self.user_id,))
        self.conn.commit()
        self.conn.close()

    def test_analytics_filter(self):
        # Test default (30 days)
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="30_days"', response.data)
        
        # Test 'today' filter
        response = self.client.get('/analytics?time_range=today')
        self.assertEqual(response.status_code, 200)
        # Check if the select option is selected
        self.assertIn(b'value="today"', response.data)

    def test_settings_page(self):
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Configuraci', response.data)
        self.assertIn(b'Perfil', response.data)

    def test_new_exercise_group(self):
        # Test adding a new exercise with a new group
        response = self.client.post('/exercises/new', data={
            'nombre': 'Test Exercise New Group',
            'grupo_muscular': 'Otro',
            'new_group_name': 'New Muscle Group'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ejercicio creado correctamente', response.data)
        
        # Verify in DB
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM exercises WHERE nombre='Test Exercise New Group'")
        ex = cur.fetchone()
        self.assertIsNotNone(ex)
        self.assertEqual(ex[2], 'New Muscle Group')
        
        # Clean up
        cur.execute("DELETE FROM exercises WHERE id=%s", (ex[0],))
        conn.commit()
        conn.close()

if __name__ == '__main__':
    unittest.main()
