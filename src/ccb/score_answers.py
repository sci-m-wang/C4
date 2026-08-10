from __future__ import annotations

import json
import re
from typing import Any

PUNCT_RE = re.compile(r"[\s\n\r\t，,。.!！?？:：;；、'\"“”‘’`·]+")
EXPLANATION_TASKS = {"E0", "E1"}
PRIMARY_TASKS = {"H0", "H1", "H4", "E0"}
ANSWER_PATTERNS = (
    re.compile(r'["\']?answer["\']?\s*[:：]\s*["“”\']?([\u4e00-\u9fff]{4})', re.IGNORECASE),
    re.compile(r"(?:答案|成语)\s*(?:是|为|[:：])\s*[\"“”']?([\u4e00-\u9fff]{4})"),
)


def normalize_answer(text: str) -> str:
    return PUNCT_RE.sub("", text or "").strip()


def score_answer(prediction: str, gold: str, aliases: list[str] | None = None) -> dict[str, Any]:
    normalized_prediction = normalize_answer(prediction)
    normalized_gold = normalize_answer(gold)
    normalized_aliases = [normalize_answer(alias) for alias in (aliases or [])]
    accepted = [normalized_gold, *normalized_aliases]
    exact = normalized_prediction in accepted
    contains = any(answer and answer in normalized_prediction for answer in accepted)
    return {
        "exact_match": exact,
        "contains_gold": contains,
        "score": 1.0 if exact else (0.5 if contains else 0.0),
        "normalized_prediction": normalized_prediction,
        "normalized_gold": normalized_gold,
    }


def strip_code_fence(text: str) -> str:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def recover_explicit_answer(text: str) -> str:
    for pattern in ANSWER_PATTERNS:
        matches = pattern.findall(text or "")
        if matches:
            return matches[-1]
    lines = [line.strip().strip('"“”') for line in (text or "").splitlines() if line.strip()]
    if lines and re.fullmatch(r"[\u4e00-\u9fff]{4}", lines[-1]):
        return lines[-1]
    return ""


def parse_task_answer(task: str, output: str) -> tuple[str, bool | None, str | None]:
    if task in EXPLANATION_TASKS:
        try:
            parsed = json.loads(strip_code_fence(output))
        except (json.JSONDecodeError, TypeError) as exc:
            return recover_explicit_answer(output), False, str(exc)
        if not isinstance(parsed, dict):
            return "", False, "JSON output must be an object"
        return str(parsed.get("answer", "")).strip(), True, None
    lines = [line.strip() for line in (output or "").splitlines() if line.strip()]
    answer = lines[0].strip('"“”') if len(lines) == 1 else recover_explicit_answer(output)
    return answer, None, None


def score_task_output(
    task: str,
    output: str,
    gold: str,
    aliases: list[str] | None = None,
) -> dict[str, Any]:
    answer, valid_json, error = parse_task_answer(task, output)
    result = score_answer(answer, gold, aliases)
    return {
        "task": task,
        "parsed_answer": answer,
        "valid_json": valid_json,
        "parse_error": error,
        **result,
    }


def primary_score(records: list[dict[str, Any]]) -> dict[str, Any]:
    included = [record for record in records if record.get("eval_task") in PRIMARY_TASKS]
    exact = sum(bool(record.get("exact_match")) for record in included)
    return {
        "exact": exact,
        "total": len(included),
        "score": exact / len(included) if included else 0.0,
        "included_tasks": sorted(PRIMARY_TASKS),
    }
