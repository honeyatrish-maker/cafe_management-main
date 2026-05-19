import os
from app import app, init_admin_user

os.environ.pop('DB_HOST', None)
os.environ.pop('DB_USER', None)
os.environ.pop('DB_PASSWORD', None)
os.environ.pop('DB_NAME', None)

with app.test_request_context('/admin/login', method='POST', data={'username': 'admin', 'password': 'admin123'}):
    try:
        init_admin_user()
        response = app.view_functions['admin_login']()
        print('response type:', type(response))
        print(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
