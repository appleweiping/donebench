from __future__ import annotations

from donebench.envs.base import BaseEnv


class EmailEnv(BaseEnv):
    domain = "email"

    def search_inbox(self, query: str) -> dict:
        return self.call("email.search_inbox", {"query": query})

    def draft_email(self, message: dict) -> dict:
        self.state.setdefault("objects", {}).setdefault("email_message", []).append(message | {"status": "draft"})
        return self.call("email.draft_email", message, mutating=True)

    def attach_file(self, message_id: str, file_id: str) -> dict:
        return self.call("email.attach_file", {"message_id": message_id, "file_id": file_id}, mutating=True)

    def send_email(self, to: list[str], subject: str) -> dict:
        self.state.setdefault("sent", []).append({"message_type": "email", "to": to, "subject": subject})
        return self.call("send_email", {"to": to, "subject": subject}, mutating=True)
