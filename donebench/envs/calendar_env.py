from __future__ import annotations

from donebench.envs.base import BaseEnv


class CalendarEnv(BaseEnv):
    domain = "calendar"

    def list_calendars(self) -> dict:
        return self.call("calendar.list_calendars")

    def check_availability(self, participants: list[str]) -> dict:
        return self.call("calendar.search_availability", {"participants": participants})

    def create_draft_event(self, event: dict) -> dict:
        self.state.setdefault("objects", {}).setdefault("calendar_event", []).append(event | {"status": "draft"})
        return self.call("calendar.create_draft_event", event, mutating=True)

    def send_invite(self, event_id: str, to: list[str]) -> dict:
        self.state.setdefault("sent", []).append({"message_type": "invite", "to": to, "event_id": event_id})
        return self.call("send_invites", {"event_id": event_id, "to": to}, mutating=True)
