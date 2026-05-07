from __future__ import annotations

from donebench.envs.base import BaseEnv


class FileEnv(BaseEnv):
    domain = "file_doc"

    def list_files(self, folder: str) -> dict:
        return self.call("file.list_files", {"folder": folder})

    def write_file(self, path: str, content: str) -> dict:
        return self.call("file.write_file", {"path": path, "content": content}, mutating=True)

    def move_file(self, src: str, dst: str) -> dict:
        return self.call("file.move_file", {"src": src, "dst": dst}, mutating=True)

    def share_file(self, path: str, audience: list[str]) -> dict:
        return self.call("file.share", {"path": path, "audience": audience}, mutating=True)
