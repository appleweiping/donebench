from __future__ import annotations

from donebench.envs.base import BaseEnv


class SheetEnv(BaseEnv):
    domain = "sheet_db"

    def query_rows(self, table: str, filters: dict) -> dict:
        return self.call("sheet.query_rows", {"table": table, "filters": filters})

    def update_row(self, row_id: str, values: dict) -> dict:
        return self.call("sheet.update_row", {"row_id": row_id, "values": values}, mutating=True)

    def append_audit_log(self, values: dict) -> dict:
        return self.call("sheet.append_audit_log", values, mutating=True)

    def export_csv(self, table: str) -> dict:
        return self.call("sheet.export_csv", {"table": table}, mutating=False)
