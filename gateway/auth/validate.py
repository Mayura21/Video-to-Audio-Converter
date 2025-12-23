import os, requests


def token(request):
    if not "Authorization" in request.headers:
        return None, ("missing credentials",  401)
    
    token = request.headers["Authorization"]

    if not token:
        return None, ("missing credentials", 401)
    
    try:
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
            headers={"Authorization": token}
        )
        if response.status_code == 200:
            return response.text, None
        else:
            return None, (response.text, response.status_code)
    except requests.exceptions.RequestException as e:
        return None, ("auth service unavailable", 503)