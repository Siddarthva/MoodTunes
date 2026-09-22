import requests

url = 'http://127.0.0.1:8001/api/analyze'

# Test 1: No intent field
try:
    files = {'image': ('test.jpg', b'FAKEIMAGE', 'image/jpeg')}
    response = requests.post(url, files=files)
    print("Test 1 (No intent):", response.status_code, response.text)
except Exception as e:
    print(e)

# Test 2: Proper request but still fails?
try:
    files = {'image': ('test.jpg', b'FAKEIMAGE', 'image/jpeg')}
    data = {'intent': 'match_me'}
    response = requests.post(url, files=files, data=data)
    print("Test 2 (With intent):", response.status_code, response.text)
except Exception as e:
    print(e)
