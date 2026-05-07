from __future__ import annotations

from donebench.envs.base import BaseEnv
from donebench.envs.calendar_env import CalendarEnv
from donebench.envs.crm_env import CRMEnv
from donebench.envs.email_env import EmailEnv
from donebench.envs.file_env import FileEnv
from donebench.envs.sheet_env import SheetEnv


ENV_REGISTRY: dict[str, type[BaseEnv]] = {
    "calendar": CalendarEnv,
    "email": EmailEnv,
    "sheet_db": SheetEnv,
    "crm_workflow": CRMEnv,
    "file_doc": FileEnv,
}


def make_env(domain: str, initial_state: dict) -> BaseEnv:
    return ENV_REGISTRY[domain](initial_state)
