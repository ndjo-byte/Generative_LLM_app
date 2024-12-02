import requests

def test_landing_page():
    url = 'http://127.0.0.1:8000/'  
    response = requests.get(url)
    assert response.status_code == 200


def test_generate_plan_endpoint():
    url = 'http://127.0.0.1:8000/generate-plan/'  
    data = {
        "name": "Learn Python",
        "description": "Learn Python programming in-depth to become proficient.",
        "deadline": "2024-12-31"
    }
    response = requests.post(url, data=data)
    assert response.status_code == 200
    assert "goal" in response.text


def test_get_goal_endpoint():
    url = 'http://127.0.0.1:8000/get-goal/1'  
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text  # Ensure there's content in the response
    assert "goal" in response.text