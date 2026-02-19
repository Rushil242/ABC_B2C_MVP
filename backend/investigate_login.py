
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_login_multipart_with_wrong_header(username, password):
    url = f"{BASE_URL}/api/auth/login"
    
    # Manual multipart construction
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="username"\r\n\r\n'
        f'{username}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="password"\r\n\r\n'
        f'{password}\r\n'
        f'--{boundary}--\r\n'
    )
    
    # But set the header to application/x-www-form-urlencoded (simulating the bug)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(url, data=body, headers=headers)
        print(f"Login attempt (Multipart Body + UrlEncoded Header) for {username}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_login_correct_header(username, password):
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": username,
        "password": password
    }
    # requests automatically sets application/x-www-form-urlencoded
    try:
        response = requests.post(url, data=data) 
        print(f"\nLogin attempt (Correct) for {username}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("Testing Login with Frontend Bug Reproduction...")
    test_login_multipart_with_wrong_header("ABCDE1234F", "demo123")
    
    print("Testing Correct Login...")
    test_login_correct_header("ABCDE1234F", "demo123")
