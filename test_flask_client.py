import os
import sys
import traceback

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from backend.app import app
    client = app.test_client()
    
    print("Testing GET /api/start...")
    response = client.get("/api/start")
    print("Status Code:", response.status_code)
    print("Response Data:", response.data.decode("utf-8")[:1000]) # First 1000 chars of response
    
except Exception as e:
    tb = traceback.format_exc()
    print("Exception occurred:")
    print(tb)
    with open("flask_test_error.txt", "w") as f:
        f.write(tb)
