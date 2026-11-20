import json, os
import requests


class Telegram:
    def __init__(self, token=None, chat_id=None):
        self.token = (token or os.environ["TELEGRAM_BOT_TOKEN"]).strip()
        self.chat_id = str(chat_id or os.environ["TELEGRAM_CHAT_ID"]).strip()
        self.base = f"https://api.telegram.org/bot{self.token}"

    def _call(self, method, files=None, http_timeout=60, **params):
        # http_timeout = requests timeout; Telegram's own "timeout" parameter (long polling) stays in params
        r = requests.post(f"{self.base}/{method}", data=params, files=files, timeout=http_timeout)
        j = r.json()
        if not j.get("ok"):
            raise RuntimeError(f"telegram {method}: {j}")
        return j["result"]

    def send_message(self, text, **kw):
        return self._call("sendMessage", chat_id=self.chat_id, text=text[:4096], **kw)

    def send_video_for_approval(self, path, caption, key):
        kb = {"inline_keyboard": [[{"text": "✅ Paylaş", "callback_data": f"ok|{key}"},
                                   {"text": "❌ Reddet", "callback_data": f"no|{key}"}]]}
        with open(path, "rb") as f:
            return self._call("sendVideo", files={"video": ("video.mp4", f, "video/mp4")}, http_timeout=300,
                              chat_id=self.chat_id, caption=caption[:1024], supports_streaming="true",
                              reply_markup=json.dumps(kb))

    def get_updates(self, offset):
        return self._call("getUpdates", offset=offset, timeout=0, allowed_updates=json.dumps(["callback_query", "message"]))

    def webhook_info(self):
        return self._call("getWebhookInfo")

    def answer_callback(self, cb_id, text=""):
        try:
            self._call("answerCallbackQuery", callback_query_id=cb_id, text=text)
        except Exception:
            pass  # callbacks older than ~15 min can no longer be answered; harmless

    def clear_buttons(self, message_id):
        try:
            self._call("editMessageReplyMarkup", chat_id=self.chat_id, message_id=message_id,
                       reply_markup=json.dumps({"inline_keyboard": []}))
        except Exception:
            pass

    def download(self, file_id):
        f = self._call("getFile", file_id=file_id)
        r = requests.get(f"https://api.telegram.org/file/bot{self.token}/{f['file_path']}", timeout=300)
        r.raise_for_status()
        return r.content
