# Calibration Packet

This packet prepares a balanced 50-task calibration set for true human review. It is not a completed human annotation artifact.

- Items: 50
- Target task numbers: 021..030
- Balance: domain-balanced, not difficulty-balanced
- Items file: `items.jsonl`

Rules:

- Do not copy model or Codex opinions into human annotation fields.
- Leave `annotation/human_audit_queue.jsonl` unchanged until true human annotators complete labels.
- Treat this packet as optional semantic calibration, not a paper-readiness gate.
