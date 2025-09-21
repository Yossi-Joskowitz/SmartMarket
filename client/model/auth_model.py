from dataclasses import dataclass
from typing import Dict
import requests
import http.server, socketserver, webbrowser, threading, urllib.parse, time


API_KEY = "AIzaSyDT2ctW7S1NlNj0G9QRbA8zmugn44ZiLE4"
GOOGLE_CLIENT_ID = "1054940845073-eflpktmnpshcigdg6gg67ipc4sad7d71.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = "openid email profile"

def _post_json(url: str, payload: dict, timeout: float = 15.0) -> dict:
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def google_oauth_loopback(port: int = 8765) -> dict:
    """
    Opens the user's browser to Google consent screen.
    Receives the authorization code on a local HTTP server and exchanges it for tokens.
    Returns: dict containing at least 'id_token'.
    """
    redirect_uri = f"http://127.0.0.1:{port}"
    code_holder = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            if "code" in params:
                code_holder["code"] = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<html><body>Login successful. You may close this window.</body></html>")
            else:
                self.send_response(400); self.end_headers()
        def log_message(self, *args):  # quiet server logs
            pass

    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        threading.Thread(target=httpd.serve_forever, daemon=True).start()

        auth_url = (
            f"{GOOGLE_AUTH}"
            f"?client_id={urllib.parse.quote(GOOGLE_CLIENT_ID)}"
            f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
            f"&response_type=code"
            f"&scope={urllib.parse.quote(GOOGLE_SCOPES)}"
            f"&access_type=offline"
            f"&prompt=select_account"
        )
        webbrowser.open(auth_url)

        # Wait for code (timeout ~120s)
        for _ in range(1200):
            if "code" in code_holder:
                break
            time.sleep(0.1)
        httpd.shutdown()

    if "code" not in code_holder:
        raise RuntimeError("Google OAuth timed out or was cancelled")

    data = {
        "code": code_holder["code"],
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    r = requests.post(GOOGLE_TOKEN, data=data, timeout=15)
    r.raise_for_status()
    tokens = r.json()
    if "id_token" not in tokens:
        raise RuntimeError("Google OAuth did not return id_token")
    return tokens


def firebase_sign_in_with_google_idtoken(google_id_token: str) -> dict:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={API_KEY}"
    payload = {
        "postBody": f"id_token={google_id_token}&providerId=google.com",
        "requestUri": "http://localhost",
        "returnIdpCredential": True,
        "returnSecureToken": True
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()

def refresh_id_token(refresh_token: str) -> dict:
    """
    Exchange a refresh_token for a fresh id_token (OAuth token endpoint uses form-encoded body).
    Returns: dict with id_token, maybe rotated refresh_token, expires_in, etc.
    """
    url = f"https://securetoken.googleapis.com/v1/token?key={API_KEY}"
    r = requests.post(url, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }, timeout=15)
    r.raise_for_status()
    return r.json()

@dataclass
class AuthResult:
    id_token: str
    refresh_token: str
    email: str

class AuthModel:
    # def __init__(self):
        # Lazy import so unit tests can stub easily
        # self._auth = importlib.import_module("model.auth")

    # ---- Email/Password ----
    def sign_up(self, email: str, password: str) -> Dict:
        """
        Create a new Firebase user with email/password.
        Returns: dict containing idToken, refreshToken, localId, etc.
        """
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        return _post_json(url, payload)

    def send_verification(self, id_token: str) -> Dict:
        """
        Send verification email to the newly created user.
        """
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
        payload = {"requestType": "VERIFY_EMAIL", "idToken": id_token}
        return _post_json(url, payload)


    def sign_in(self, email: str, password: str) -> AuthResult:
        """
        Sign in with email/password and return AuthResult (typed), not a raw dict.
        """
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        data = _post_json(url, payload)  # dict מה-REST
        return AuthResult(
            id_token=data["idToken"],
            refresh_token=data["refreshToken"],
            email=data.get("email", email),
        )

    def get_user_info(self, id_token: str) -> Dict:
        """
        Lookup user record to check email verification status and other metadata.
        Returns: the first user object from the response.
        """
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={API_KEY}"
        data = _post_json(url, {"idToken": id_token})
        return data["users"][0]
    
    def send_password_reset(self, email: str) -> Dict:
        """
        Trigger password reset email.
        """
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
        payload = {"requestType": "PASSWORD_RESET", "email": email}
        return _post_json(url, payload)

    # ---- Google Sign-In (optional) ----
    def sign_in_with_google(self) -> AuthResult:
        """
        Fully functional Google OAuth (loopback) + Firebase IdP sign-in.
        REQUIREMENTS:
            - model/oauth_google.py: fill GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET.
            - model/firebase_identity.py: uses your Firebase API key in model/auth.py
            - pip install requests
        """
        # google = importlib.import_module("model.oauth_google")
        # idp    = importlib.import_module("model.firebase_identity")

        google_tokens = google_oauth_loopback()
        firebase_data = firebase_sign_in_with_google_idtoken(google_tokens["id_token"])
        return AuthResult(
            id_token=firebase_data["idToken"],
            refresh_token=firebase_data["refreshToken"],
            email=firebase_data.get("email", ""),
        )
