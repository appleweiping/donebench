# DoneBench Human Calibration Form

给审核人的说明：你不需要会代码，也不需要理解整篇论文。你只需要判断这些任务本身是否合理：题目、完成标准、正确答案、错误样例是否对得上。

## 你要打开的位置

项目文件夹：

```text
D:\Research\DoneBench
```

任务清单：

```text
D:\Research\DoneBench\reports\calibration_packets\items.jsonl
```

具体任务文件都在：

```text
D:\Research\DoneBench\data\tasks\
```

下面每个任务都写了完整路径。你按顺序打开对应的 `.json` 文件，看里面这些字段：

```text
user_goal
criteria_atoms
gold_donespec
reference_solution
near_miss_final_states
```

含义：

- `user_goal`：用户想让 agent 做什么。
- `criteria_atoms`：这件事怎么算完成。
- `gold_donespec`：机器可执行的完成标准；不用完全看懂代码，只看它是不是在检查正确的东西。
- `reference_solution`：标准答案，包括正确步骤和正确最终状态。
- `near_miss_final_states`：差一点完成但其实没完成的错误例子。

## 重要规则

- 不要修改 `data/tasks/` 里的 JSON 文件。
- 不要修改 `annotation/human_audit_queue.jsonl`。
- 不要看模型跑分结果。
- 不要为了让论文好看而放水。
- 不确定就选 `warn`，并在备注里写哪里不确定。
- 建议先做前 3 个任务，发回确认理解没问题后再继续。

## 怎么填

每个任务有 5 个检查项。每项把一个 `[ ]` 改成 `[x]`。

可选项：

```text
pass = 没问题
warn = 有点问题，但还能用或不确定
fail = 明显有问题，要修或删
```

最后给一个总判断：

```text
accept = 可以用
revise = 修一下能用
reject = 不建议用
```

信心分：

```text
5 = 很确定
3 = 一般确定
1 = 不确定
```

5 个检查项的意思：

1. `criteria_complete`：用户要求的关键事情，完成标准有没有都覆盖？
2. `donespec_matches_criteria`：`gold_donespec` 和完成标准是否一致？
3. `near_misses_are_valid`：near misses 是不是真的“差一点但没完成”？
4. `reference_trace_is_plausible`：标准答案步骤是否合理，是否没有凭空跳到最终结果？
5. `not_too_templated`：任务是否不是过度机械换皮？

备注短句即可，例如：

```text
criteria misses email confirmation
near miss 2 is actually acceptable
reference trace jumps to final state
task feels templated
looks reasonable
not sure about DoneSpec
```

---

## Quick Start: 先做这 3 个

### Task 1: calendar_021

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_021.json
```

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### Task 2: crm_workflow_021

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_021.json
```

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### Task 3: email_021

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_021.json
```

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

---

## Full 50-Task Form

### calendar_021

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_021.json
```

Pattern: `calendar_focus_block`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_022

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_022.json
```

Pattern: `calendar_schedule_sync`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_023

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_023.json
```

Pattern: `calendar_reschedule_review`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_024

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_024.json
```

Pattern: `calendar_focus_block`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_025

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_025.json
```

Pattern: `calendar_schedule_sync`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_026

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_026.json
```

Pattern: `calendar_reschedule_review`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_027

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_027.json
```

Pattern: `calendar_focus_block`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_028

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_028.json
```

Pattern: `calendar_schedule_sync`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_029

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_029.json
```

Pattern: `calendar_reschedule_review`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### calendar_030

Path:

```text
D:\Research\DoneBench\data\tasks\calendar\calendar_030.json
```

Pattern: `calendar_focus_block`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_021

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_021.json
```

Pattern: `crm_reopen_sla`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_022

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_022.json
```

Pattern: `crm_close_escalation`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_023

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_023.json
```

Pattern: `crm_route_refund`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_024

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_024.json
```

Pattern: `crm_reopen_sla`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_025

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_025.json
```

Pattern: `crm_close_escalation`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_026

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_026.json
```

Pattern: `crm_route_refund`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_027

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_027.json
```

Pattern: `crm_reopen_sla`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_028

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_028.json
```

Pattern: `crm_close_escalation`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_029

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_029.json
```

Pattern: `crm_route_refund`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### crm_workflow_030

Path:

```text
D:\Research\DoneBench\data\tasks\crm_workflow\crm_workflow_030.json
```

Pattern: `crm_reopen_sla`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_021

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_021.json
```

Pattern: `email_forward_digest`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_022

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_022.json
```

Pattern: `email_weekly_summary`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_023

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_023.json
```

Pattern: `email_customer_reply`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_024

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_024.json
```

Pattern: `email_forward_digest`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_025

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_025.json
```

Pattern: `email_weekly_summary`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_026

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_026.json
```

Pattern: `email_customer_reply`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_027

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_027.json
```

Pattern: `email_forward_digest`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_028

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_028.json
```

Pattern: `email_weekly_summary`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_029

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_029.json
```

Pattern: `email_customer_reply`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### email_030

Path:

```text
D:\Research\DoneBench\data\tasks\email\email_030.json
```

Pattern: `email_forward_digest`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_021

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_021.json
```

Pattern: `file_share_packet`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_022

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_022.json
```

Pattern: `file_revise_document`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_023

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_023.json
```

Pattern: `file_archive_contract`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_024

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_024.json
```

Pattern: `file_share_packet`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_025

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_025.json
```

Pattern: `file_revise_document`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_026

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_026.json
```

Pattern: `file_archive_contract`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_027

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_027.json
```

Pattern: `file_share_packet`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_028

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_028.json
```

Pattern: `file_revise_document`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_029

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_029.json
```

Pattern: `file_archive_contract`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### file_doc_030

Path:

```text
D:\Research\DoneBench\data\tasks\file_doc\file_doc_030.json
```

Pattern: `file_share_packet`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_021

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_021.json
```

Pattern: `sheet_append_forecast`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_022

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_022.json
```

Pattern: `sheet_update_account`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_023

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_023.json
```

Pattern: `sheet_dedupe_contact`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_024

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_024.json
```

Pattern: `sheet_append_forecast`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_025

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_025.json
```

Pattern: `sheet_update_account`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_026

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_026.json
```

Pattern: `sheet_dedupe_contact`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_027

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_027.json
```

Pattern: `sheet_append_forecast`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_028

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_028.json
```

Pattern: `sheet_update_account`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_029

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_029.json
```

Pattern: `sheet_dedupe_contact`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

### sheet_db_030

Path:

```text
D:\Research\DoneBench\data\tasks\sheet_db\sheet_db_030.json
```

Pattern: `sheet_append_forecast`; difficulty: `L2`

- criteria_complete: [ ] pass [ ] warn [ ] fail
- donespec_matches_criteria: [ ] pass [ ] warn [ ] fail
- near_misses_are_valid: [ ] pass [ ] warn [ ] fail
- reference_trace_is_plausible: [ ] pass [ ] warn [ ] fail
- not_too_templated: [ ] pass [ ] warn [ ] fail
- Final decision: [ ] accept [ ] revise [ ] reject
- Confidence: [ ] 5 [ ] 3 [ ] 1
- Notes:

```text

```

## 填完后发回

请把这个 Markdown 文件填好后发回。不要改其他文件。收到后我们会把你的填写结果整理进正式 annotation 文件。
