from typing import Optional, Dict, Tuple
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from loginWindow.login_model import AuthModel, AuthResult
from loginWindow.login_view import LoginView
from thread_manager import run_in_worker


def friendly_error_message(e: Exception) -> str:
    import requests
    try:
        if isinstance(e, requests.HTTPError) and e.response is not None:
            data = e.response.json()
            code = data.get("error", {}).get("message", "")
            mapping = {
                "EMAIL_EXISTS": "Email already registered.",
                "OPERATION_NOT_ALLOWED": "This sign-in method is not enabled.",
                "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Try later.",
                "EMAIL_NOT_FOUND": "Email not found.",
                "INVALID_PASSWORD": "Invalid password.",
                "USER_DISABLED": "User disabled.",
            }
            return mapping.get(code, f"Error: {code}")
    except Exception:
        pass
    return f"Error: {e}"


class LoginPresenter(QObject):
    def __init__(self, view: LoginView, model: AuthModel):
        super().__init__(view)
        self.view = view
        self.model = model
        self.result: Optional[AuthResult] = None
        self.user_info: Optional[Dict] = None

        # Connect view signals
        view.request_login.connect(self.on_login)
        view.request_signup.connect(self.on_signup)
        view.request_send_verification.connect(self.on_send_verification)
        view.request_forgot_password.connect(self.on_forgot_password)
        view.request_google_login.connect(self.on_google_login)

    # ---------- Email/Password sign in ----------
    def on_login(self, email: str, password: str):
        if not email or not password:
            self.view.show_error("Please enter email and password.")
            return
        self.view.set_busy(True, "Signing in…")

        @run_in_worker
        def sign_in_task():
            return self.model.sign_in(email, password)

        def after_login(auth_res: AuthResult):
            # After sign-in, check email verification
            @run_in_worker
            def get_user_info_task():
                return self.model.get_user_info(auth_res.id_token)

            def after_lookup(info: Dict):
                if not info.get("emailVerified", False):
                    self.view.set_busy(False)
                    self.view.show_error("Email not verified. Check your inbox or resend from the Sign Up tab.")
                    return
                
                # Store user info and update auth result with display name
                self.user_info = info
                self.result = AuthResult(
                    id_token=auth_res.id_token,
                    refresh_token=auth_res.refresh_token,
                    email=auth_res.email,
                    display_name=info.get("displayName") or info.get("email", "").split("@")[0]
                )
                self.view.accept()

            get_user_info_task(on_result=after_lookup, on_error=self._error)

        sign_in_task(on_result=after_login, on_error=self._error)

    # ---------- Sign up + verification ----------
    def on_signup(self, email: str, password: str):
        if not email or not password:
            self.view.show_error("Please enter email and password.")
            return
        self.view.set_busy(True, "Creating account…")

        @run_in_worker
        def signup_task():
            return self.model.sign_up(email, password)

        def after_signup(data: Dict):
            self.view.remember_signup_context(data["idToken"], email)

            @run_in_worker
            def send_verification_task():
                return self.model.send_verification(data["idToken"])

            def after_send_verif(_ok):
                self.view.set_busy(False)
                self.view.show_info(f"A verification email was sent to {email}. Please verify, then sign in.")

            send_verification_task(on_result=after_send_verif, on_error=self._error)

        signup_task(on_result=after_signup, on_error=self._error)

    def on_send_verification(self):
        token = self.view.consume_signup_id_token()
        email = self.view.last_signup_email() or ""
        if not token:
            self.view.show_error("No pending verification token. Please sign up first.")
            return
        self.view.set_busy(True, "Sending verification email…")

        @run_in_worker
        def send_verification_task():
            return self.model.send_verification(token)

        def after_send_verif(_ok):
            self.view.set_busy(False)
            self.view.show_info(f"A verification email was sent to {email}. Please verify, then sign in.")

        send_verification_task(on_result=after_send_verif, on_error=self._error)

    def on_forgot_password(self, email: str):
        if not email:
            self.view.show_error("Enter an email to reset password.")
            return
        self.view.set_busy(True, "Sending reset email…")

        @run_in_worker
        def send_reset_task():
            return self.model.send_password_reset(email)

        def after_reset(_ok):
            self.view.set_busy(False)
            self.view.show_info(f"Password reset email sent to {email}.")

        send_reset_task(on_result=after_reset, on_error=self._error)

    # ---------- Google sign in ----------
    def on_google_login(self):
        self.view.set_busy(True, "Signing in with Google…")

        @run_in_worker
        def google_login_task():
            return self.model.sign_in_with_google()

        def after_google(auth_res: AuthResult):
            # Fetch user info to get display name
            @run_in_worker
            def get_user_info_task():
                return self.model.get_user_info(auth_res.id_token)

            def after_google_lookup(info: Dict):
                # Store user info and update auth result with display name
                self.user_info = info
                self.result = AuthResult(
                    id_token=auth_res.id_token,
                    refresh_token=auth_res.refresh_token,
                    email=auth_res.email,
                    display_name=info.get("displayName") or info.get("email", "").split("@")[0]
                )
                self.view.accept()

            get_user_info_task(on_result=after_google_lookup, on_error=self._error)

        google_login_task(on_result=after_google, on_error=self._error)

    # ---------- Generic error handler ----------
    def _error(self, e: Exception):
        self.view.set_busy(False)
        self.view.show_error(friendly_error_message(e))


def login_page() -> Tuple[bool, Optional[Dict[str, str]]]:
    """
    Create and show the login page.
    Returns: (success: bool, user_info: Optional[Dict[str, str]])
    
    If successful, user_info contains:
    - 'email': user's email address
    - 'display_name': user's display name
    - 'id_token': Firebase ID token
    - 'refresh_token': Firebase refresh token
    """
    view = LoginView()
    model = AuthModel()
    presenter = LoginPresenter(view, model)
    
    ok = (view.exec() == QDialog.DialogCode.Accepted) and (presenter.result is not None)
    
    if ok and presenter.result:
        user_info = {
            'email': presenter.result.email,
            'display_name': presenter.result.display_name or "User",
            'id_token': presenter.result.id_token,
            'refresh_token': presenter.result.refresh_token
        }
        return True, user_info
    else:
        return False, None