"""
LoginPresenter – THREAD-SAFE version
- Tracks all Worker threads to prevent "QThread: Destroyed while thread '' is still running".
- Shuts down workers when the dialog finishes (Accepted/Rejected).
"""
from typing import Optional, Dict, Callable, List
from PySide6.QtCore import QObject, QThread, Signal

from model.auth_model import AuthModel, AuthResult
from view.login_view import LoginView


class Worker(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kw = kwargs

    def run(self):
        try:
            res = self.fn(*self.args, **self.kw)
            self.finished_ok.emit(res)
        except Exception as e:
            self.failed.emit(friendly_error_message(e))


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
        self._workers: List[Worker] = []

        # Connect view signals
        view.request_login.connect(self.on_login)
        view.request_signup.connect(self.on_signup)
        view.request_send_verification.connect(self.on_send_verification)
        view.request_forgot_password.connect(self.on_forgot_password)
        view.request_google_login.connect(self.on_google_login)

        # When the dialog finishes (Accepted/Rejected), shut down all threads
        view.finished.connect(lambda _code: self.shutdown())

    # ---------- Thread management ----------
    def _start_worker(self, fn: Callable, on_ok=None, *args, **kwargs):
        w = Worker(fn, *args, **kwargs)
        self._workers.append(w)

        def _cleanup():
            try:
                if w in self._workers:
                    self._workers.remove(w)
                w.deleteLater()
            except Exception:
                pass

        if on_ok is not None:
            w.finished_ok.connect(on_ok)
        w.finished_ok.connect(_cleanup)
        w.failed.connect(self._error)
        w.failed.connect(lambda _msg: _cleanup())
        w.start()
        return w

    def shutdown(self):
        """Gracefully stop/join all workers to avoid QThread destructor crash."""
        for w in list(self._workers):
            try:
                # disconnect to avoid late signals
                try:
                    w.finished_ok.disconnect()
                except Exception:
                    pass
                try:
                    w.failed.disconnect()
                except Exception:
                    pass
                if w.isRunning():
                    w.quit()
                    w.wait(5000)  # up to 5s
            finally:
                try:
                    w.deleteLater()
                except Exception:
                    pass
        self._workers.clear()

    # ---------- Email/Password sign in ----------
    def on_login(self, email: str, password: str):
        if not email or not password:
            self.view.show_error("Please enter email and password.")
            return
        self.view.set_busy(True, "Signing in…")
        self._start_worker(self.model.sign_in, self._after_login, email, password)

    def _after_login(self, auth_res: AuthResult):
        # After sign-in, check email verification
        self._start_worker(self.model.get_user_info, lambda info: self._after_lookup(info, auth_res), auth_res.id_token)

    def _after_lookup(self, info: Dict, auth_res: AuthResult):
        if not info.get("emailVerified", False):
            self.view.set_busy(False)
            self.view.show_error("Email not verified. Check your inbox or resend from the Sign Up tab.")
            return
        self.result = auth_res
        self.view.accept()

    # ---------- Sign up + verification ----------
    def on_signup(self, email: str, password: str):
        if not email or not password:
            self.view.show_error("Please enter email and password.")
            return
        self.view.set_busy(True, "Creating account…")
        self._start_worker(self.model.sign_up, lambda data: self._after_signup(data, email), email, password)

    def _after_signup(self, data: Dict, email: str):
        self.view.remember_signup_context(data["idToken"], email)
        self._start_worker(self.model.send_verification, lambda _ok: self._after_send_verif(email), data["idToken"])

    def _after_send_verif(self, email: str):
        self.view.set_busy(False)
        self.view.show_info(f"A verification email was sent to {email}. Please verify, then sign in.")

    def on_send_verification(self):
        token = self.view.consume_signup_id_token()
        email = self.view.last_signup_email() or ""
        if not token:
            self.view.show_error("No pending verification token. Please sign up first.")
            return
        self.view.set_busy(True, "Sending verification email…")
        self._start_worker(self.model.send_verification, lambda _ok: self._after_send_verif(email), token)

    def on_forgot_password(self, email: str):
        if not email:
            self.view.show_error("Enter an email to reset password.")
            return
        self.view.set_busy(True, "Sending reset email…")
        self._start_worker(self.model.send_password_reset, lambda _ok: self._after_reset(email), email)

    def _after_reset(self, email: str):
        self.view.set_busy(False)
        self.view.show_info(f"Password reset email sent to {email}.")

    # ---------- Google sign in ----------
    def on_google_login(self):
        self.view.set_busy(True, "Signing in with Google…")
        self._start_worker(self.model.sign_in_with_google, self._after_google)

    def _after_google(self, auth_res: AuthResult):
        self.result = auth_res
        self.view.accept()

    # ---------- Generic error handler ----------
    def _error(self, message: str):
        self.view.set_busy(False)
        self.view.show_error(message)
