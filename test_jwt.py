import requests
import json
import sys

def test_jwt_flow():
    """Test the JWT authentication flow"""
    base_url = "http://localhost:8000/api/v1"

    print("\n----- Testing JWT Authentication Flow -----")

    # Step 1: Try to login
    print("\n1. Attempting to login with test credentials...")

    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            data={
                "username": "testuser@example.com",
                "password": "password"
            },
        )

        if login_response.status_code == 200:
            print(" Login successful!")
            token_data = login_response.json()
            print(f"Token type: {token_data['token_type']}")
            print(f"Access token received: {token_data['access_token'][:20]}...")

            # Step 2: Test the token
            print("\n2. Testing the received token...")

            test_response = requests.get(
                "http://localhost:8000/api/test-token",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )

            if test_response.status_code == 200:
                print(" Token verification successful!")
                print(f"Response: {test_response.json()}")
            else:
                print(f" Token verification failed. Status: {test_response.status_code}")
                print(f"Response: {test_response.text}")
                return False
        else:
            print(f" Login failed. Status: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False

    except Exception as e:
        print(f" Error during test: {e}")
        return False

    print("\n JWT Authentication flow tested successfully!")
    return True

if __name__ == "__main__":
    print("Starting JWT authentication test...")
    success = test_jwt_flow()
    if success:
        sys.exit(0)
    else:
        print("Test failed!")
        sys.exit(1)
