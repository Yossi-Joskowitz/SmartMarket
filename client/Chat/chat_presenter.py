from __future__ import annotations
from typing import Optional
from .chat_model import ChatModel
from .chat_view import ChatView
from thread_manager import run_in_worker

class ChatPresenter:
    def __init__(self, view: ChatView, model: ChatModel):
        self.view = view
        self.model = model
        self._pending_question: Optional[str] = None  

        # Wire UI signal
        self.view.sendRequested.connect(self._on_send_requested)


    def _on_send_requested(self, question: str, force_mode: Optional[str], max_rows: int) -> None:
        # UI updates (display-only)
        self.view.appendRequested.emit("You", question)
        self.view.clear_input()

        if self._pending_question and question.strip().lower() in {"yes", "y", "ok"}:
            pending = self._pending_question  
            self._pending_question = None    

            @run_in_worker
            def do_confirm():
                return self.model.chat(pending, confirm_write=True)

            def done_confirm(data):
                # אחרי אישור: מציגים רק את ה-message (או ברירת מחדל)
                msg = self.create_message(data)
                self.view.appendRequested.emit("Assistant", msg)

            def on_error_confirm(e: Exception) -> None:
                self.view.appendRequested.emit("Error", f"❌ Error: {type(e).__name__}: {e}")

            do_confirm(on_result=done_confirm, on_error=on_error_confirm)
            return

        @run_in_worker
        def do():
            return self.model.chat(question)

        def done(data):
            if data.get("is_write_query") and not data.get("executed"):
                self._pending_question = data.get("question")

            msg = self.create_message(data)
            self.view.appendRequested.emit("Assistant", msg)

        def on_error(e: Exception) -> None:
            self.view.appendRequested.emit("Error", f"❌ Error: {type(e).__name__}: {e}")

        do(on_result=done, on_error=on_error)

    def create_message(self, data: dict) -> str:
        if data.get("is_write_query") and not data.get("executed"):
            msg_lines = [f"🧠 Question: {data.get('question', '')}"]

            message = data.get("message") or "Confirmation required to execute write query."
            msg_lines.append(f"⚠️ {message}")

            if data.get("sql"):
                msg_lines.append("\n📄 SQL to be executed:")
                msg_lines.append(data["sql"])

            return "\n".join(msg_lines)

        if data.get("is_write_query") and data.get("executed"):
            return data.get("message") or (
                f"Done. Rows affected: {data.get('rows_affected')}"
                if data.get("rows_affected") is not None else "Done."
            )

        msg_lines = [f"🧠 Question: {data.get('question', '')}"]
        if data.get("sql"):
            msg_lines.append(f"📄 SQL:\n{data['sql']}")

        results = data.get("results") or []
        count = len(results)
        msg_lines.append(f"✅ Query executed. Returned {count} rows.")
        if count > 0:
            msg_lines.append("\n📊 Results:")
            for i, row in enumerate(results, 1):
                if isinstance(row, dict):
                    row_str = ", ".join(f"{k}={v}" for k, v in row.items())
                else:
                    row_str = str(row)
                msg_lines.append(f"  {i}. {row_str}")
        return "\n".join(msg_lines)

def create_chat_page() -> ChatView:
    view = ChatView()
    model = ChatModel()
    view.presenter = ChatPresenter(view, model)
    return view
