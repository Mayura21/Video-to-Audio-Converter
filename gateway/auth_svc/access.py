import os, requests


def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)
    
    basicAuth = (auth.username, auth.password)

    try:
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
            auth=basicAuth
        )

        if response.status_code == 200:
            return response.text, None
        else:
            return None, (response.text, response.status_code)
    except requests.exceptions.RequestException as e:
        return None, ("auth service unavailable", 503)
