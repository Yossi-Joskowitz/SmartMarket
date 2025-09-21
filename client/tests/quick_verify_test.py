"""
Quick script to verify that Firebase email verification is being sent.
Run from a terminal:
    python quick_verify_test.py

WHAT IT DOES
1) Tries to sign up with EMAIL/PASSWORD. If the user already exists, it falls back to sign in.
2) Sends the VERIFY_EMAIL out-of-band (OOB) message.
3) Looks up the user record and prints whether the email is verified.
4) Prints detailed HTTP errors if something goes wrong.

REQUIREMENTS
    pip install requests
    (No npm needed. This is pure Python/REST.)

IMPORTANT
- Replace EMAIL and PASSWORD below with a real address you can check.
- If you later add a 'continueUrl', ensure its domain is listed under
  Firebase Console → Authentication → Settings → Authorized domains.
"""

import requests

# --- Replace with your details ---
API_KEY = "AIzaSyDT2ctW7S1NlNj0G9QRbA8zmugn44ZiLE4"  # Your Firebase Web API Key
EMAIL = "yossijosko@gmail.com"            # <-- change me
PASSWORD = "556355"             # <-- change me

# Optional advanced parameters (leave None for a simple test)
CONTINUE_URL = None          # e.g. "https://smartmarket-76949.web.app/finishSignUp"
DYNAMIC_LINK_DOMAIN = None   # e.g. "smartmarket-76949.page.link" if you use Firebase Dynamic Links


def post_json(url, payload, timeout=20):
    r = requests.post(url, json=payload, timeout=timeout)
    try:
        r.raise_for_status()
    except Exception:
        print("HTTP ERROR:", r.status_code)
        try:
            print("Response JSON:", r.json())
        except Exception:
            print("Response TEXT:", r.text[:500])
        raise
    return r.json()


def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    return post_json(url, {"email": email, "password": password, "returnSecureToken": True})


def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    return post_json(url, {"email": email, "password": password, "returnSecureToken": True})


def send_verify_email(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
    payload = {"requestType": "VERIFY_EMAIL", "idToken": id_token}
    if CONTINUE_URL:
        payload["continueUrl"] = CONTINUE_URL
    if DYNAMIC_LINK_DOMAIN:
        payload["dynamicLinkDomain"] = DYNAMIC_LINK_DOMAIN
    return post_json(url, payload)


def lookup_user(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={API_KEY}"
    return post_json(url, {"idToken": id_token})


def main():
    assert API_KEY and EMAIL and PASSWORD, "Please set API_KEY, EMAIL and PASSWORD"

    print("== Firebase email verification quick test ==")
    print("Signing up or signing in...")

    try:
        su = sign_up(EMAIL, PASSWORD)
        id_token = su["idToken"]
        print("signUp OK (new user)")
    except Exception:
        si = sign_in(EMAIL, PASSWORD)
        id_token = si["idToken"]
        print("signIn OK (existing user)")

    print("Sending verification email...")
    ver = send_verify_email(id_token)
    print("sendOobCode VERIFY_EMAIL response:", ver)

    print("Looking up user record...")
    lk = lookup_user(id_token)
    user = lk["users"][0]
    print("email:", user.get("email"))
    print("emailVerified:", user.get("emailVerified"))

    print("\nIf you didn't receive the email:")
    print("- Check Spam/Promotions, search for noreply@<your-project>.firebaseapp.com")
    print("- Verify 'Project support email' and 'Public-facing name' in Project settings → General → Public settings")
    print("- Check 'Authorized domains' in Authentication → Settings")
    print("- Try a different mailbox (Gmail/Outlook) to rule out filtering")

if __name__ == "__main__":
    main()
