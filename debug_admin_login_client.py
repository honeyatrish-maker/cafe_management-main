import os
from app import app, init_admin_user

os.environ.pop('DB_HOST', None)
os.environ.pop('DB_USER', None)
os.environ.pop('DB_PASSWORD', None)
os.environ.pop('DB_NAME', None)

with app.test_client() as client:
    try:
        init_admin_user()
        response = client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=False)
        print('status:', response.status_code)
        print('headers:', response.headers)
        print('data snippet:', response.data[:500])
    except Exception:
        import traceback
        traceback.print_exc()
