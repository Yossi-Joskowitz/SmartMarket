from PySide6.QtCore import QRunnable, QThreadPool, QObject, Signal
from functools import wraps

# --- קטן: מזניק קריאות על ה-UI thread ---
class _UiInvoker(QObject):
    call = Signal(object)
UI = _UiInvoker()
UI.call.connect(lambda fn: fn())

def run_on_ui(fn):
    """קרא לפונקציה על ה-UI thread (בטוח ל-Qt)."""
    UI.call.emit(fn)

class _Runner(QRunnable):
    def __init__(self, fn, args, kwargs, on_result=None, on_error=None):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.on_result = on_result
        self.on_error = on_error

    def run(self):
        try:
            res = self.fn(*self.args, **self.kwargs)  
            if self.on_result:
                UI.call.emit(lambda r=res: self.on_result(r))  
        except Exception as e:
            # print("Worker error:", e)
            if self.on_error:
                UI.call.emit(lambda err=e: self.on_error(err))    

def run_in_worker(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        on_result = kwargs.pop("on_result", None)
        on_error  = kwargs.pop("on_error", None)
        QThreadPool.globalInstance().start(_Runner(fn, args, kwargs, on_result, on_error))
    return wrapper
