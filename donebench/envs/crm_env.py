from __future__ import annotations

from donebench.envs.base import BaseEnv


class CRMEnv(BaseEnv):
    domain = "crm_workflow"

    def search_ticket(self, query: str) -> dict:
        return self.call("crm.search_ticket", {"query": query})

    def add_note(self, ticket_id: str, note: str) -> dict:
        return self.call("crm.add_note", {"ticket_id": ticket_id, "note": note}, mutating=True)

    def update_status(self, ticket_id: str, status: str) -> dict:
        return self.call("crm.update_status", {"ticket_id": ticket_id, "status": status}, mutating=True)

    def send_notification(self, to: list[str]) -> dict:
        self.state.setdefault("sent", []).append({"message_type": "notification", "to": to})
        return self.call("send_notification", {"to": to}, mutating=True)
