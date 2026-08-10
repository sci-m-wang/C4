from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from ccb.io_utils import read_json, write_json
from ccb.prompt_renderer import build_full_prompt

META_TERMS = ("成语", "谜底", "答案", "替换短语", "只按照短语")
TEMPLATE_FRAGMENTS = (
    "被安排在同一张桌面",
    "被安排在同一个简洁场景",
    "二者有明确接触",
    "主要元素彼此接触或指向",
    "组合在一起",
    "小场景里",
    "不做分栏拼贴",
)
SERIOUS_FLAGS = {
    "empty_scene",
    "contains_source_idiom",
    "contains_final_substituted_phrase",
    "contains_meta_task_terms",
    "contains_template_fragment",
}


def manual_scene_paths(repo_root: Path) -> list[Path]:
    manual_dir = repo_root / "data" / "manual_scenes"
    if not manual_dir.exists():
        return []
    return sorted(manual_dir.glob("manual_scenes_*.json"))


def normalize_records(data: Any, path: Path) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    raise ValueError(f"Unsupported manual scene JSON shape: {path}")


def repository_path(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def load_manual_scenes(repo_root: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    records_by_id: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, Any]] = []
    for path in manual_scene_paths(repo_root):
        for index, record in enumerate(normalize_records(read_json(path), path)):
            item_id = str(record.get("item_id", "")).strip()
            scene = str(record.get("manual_prompt_scene", "")).strip()
            if not item_id:
                issues.append({"file": repository_path(path, repo_root), "index": index, "issue": "missing_item_id"})
                continue
            if item_id in records_by_id:
                issues.append(
                    {"file": repository_path(path, repo_root), "item_id": item_id, "issue": "duplicate_item_id"}
                )
                continue
            records_by_id[item_id] = {
                "item_id": item_id,
                "manual_prompt_scene": scene,
                "review_notes": record.get("review_notes", ""),
                "file": repository_path(path, repo_root),
            }
    return records_by_id, issues


def review_manual_scene(scene: str, source_idiom: str, final_substituted_phrase: str) -> dict[str, Any]:
    flags: list[str] = []
    if not scene:
        flags.append("empty_scene")
    if source_idiom and source_idiom in scene:
        flags.append("contains_source_idiom")
    if final_substituted_phrase and final_substituted_phrase in scene:
        flags.append("contains_final_substituted_phrase")
    if any(term in scene for term in META_TERMS):
        flags.append("contains_meta_task_terms")
    if any(fragment in scene for fragment in TEMPLATE_FRAGMENTS):
        flags.append("contains_template_fragment")
    if "\n" in scene:
        flags.append("multi_line_scene")
    if len(scene) > 90:
        flags.append("scene_too_long")
    elif len(scene) > 60:
        flags.append("scene_long_but_usable")
    status = "review" if set(flags) & SERIOUS_FLAGS else "pass"
    return {"status": status, "flags": sorted(set(flags)), "length": len(scene)}


def update_item_with_scene(item: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    scene = record["manual_prompt_scene"]
    review = review_manual_scene(scene, item["source_idiom"], item["final_substituted_phrase"])
    if "auto_prompt_scene" not in item:
        item["auto_prompt_scene"] = item.get("prompt_scene")
    item["prompt_scene"] = scene
    item["prompt_scene_source"] = "manual"
    item["manual_scene_file"] = record.get("file")
    if record.get("review_notes"):
        item["manual_scene_notes"] = record.get("review_notes")
    item["prompt_review"] = review
    item["generation_prompt"] = build_full_prompt(scene)
    return item


def update_prompt_with_scene(prompt: dict[str, Any], item: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    scene = record["manual_prompt_scene"]
    if "auto_prompt_scene" not in prompt:
        prompt["auto_prompt_scene"] = prompt.get("prompt_scene")
    prompt["prompt_scene"] = scene
    prompt["prompt_scene_source"] = "manual"
    prompt["manual_scene_file"] = record.get("file")
    if record.get("review_notes"):
        prompt["manual_scene_notes"] = record.get("review_notes")
    prompt["prompt"] = build_full_prompt(scene)
    prompt["prompt_review"] = review_manual_scene(scene, item["source_idiom"], item["final_substituted_phrase"])
    return prompt


def update_queue_with_scene(row: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    row["manual_prompt_scene"] = record["manual_prompt_scene"]
    if record.get("review_notes"):
        row["manual_scene_notes"] = record.get("review_notes")
    row["manual_scene_file"] = record.get("file")
    return row


def apply_manual_scenes_to_outputs(
    synthetic: dict[str, Any],
    generation_prompts: list[dict[str, Any]],
    prompt_edit_queue: list[dict[str, Any]],
    repo_root: Path,
    *,
    strict: bool = False,
) -> dict[str, Any]:
    manual_records, load_issues = load_manual_scenes(repo_root)
    if not manual_records:
        return {
            "schema": "manual_prompt_scene_review_v1",
            "manual_files": [],
            "applied": 0,
            "status": "skipped",
            "message": "No manual scene files found.",
        }

    items = synthetic.get("items", [])
    item_by_id = {item["item_id"]: item for item in items}
    expected_ids = set(item_by_id)
    manual_ids = set(manual_records)
    missing_ids = sorted(expected_ids - manual_ids)
    extra_ids = sorted(manual_ids - expected_ids)

    prompt_by_id = {prompt["item_id"]: prompt for prompt in generation_prompts}
    queue_by_id = {row["item_id"]: row for row in prompt_edit_queue}
    review_by_id: dict[str, dict[str, Any]] = {}
    applied = 0

    for item in items:
        record = manual_records.get(item["item_id"])
        if not record:
            continue
        update_item_with_scene(item, record)
        if item["item_id"] in prompt_by_id:
            update_prompt_with_scene(prompt_by_id[item["item_id"]], item, record)
        if item["item_id"] in queue_by_id:
            update_queue_with_scene(queue_by_id[item["item_id"]], record)
        review_by_id[item["item_id"]] = item["prompt_review"]
        applied += 1

    flag_counts = Counter(flag for review in review_by_id.values() for flag in review.get("flags", []))
    review_ids = sorted(item_id for item_id, review in review_by_id.items() if review.get("status") != "pass")
    by_level = Counter(item["level"] for item in items if item["item_id"] in manual_records)
    report = {
        "schema": "manual_prompt_scene_review_v1",
        "manual_files": [repository_path(path, repo_root) for path in manual_scene_paths(repo_root)],
        "applied": applied,
        "expected": len(expected_ids),
        "missing_ids": missing_ids,
        "extra_ids": extra_ids,
        "load_issues": load_issues,
        "review_ids": review_ids,
        "flag_counts": dict(sorted(flag_counts.items())),
        "by_level": dict(sorted(by_level.items())),
        "status": "pass" if not (missing_ids or extra_ids or load_issues or review_ids) else "review",
    }

    if strict and report["status"] != "pass":
        raise ValueError(
            "Manual scene validation failed: "
            f"missing={len(missing_ids)}, extra={len(extra_ids)}, "
            f"load_issues={len(load_issues)}, review={len(review_ids)}"
        )
    return report


def apply_manual_scenes(repo_root: Path, *, strict: bool = False) -> dict[str, Any]:
    processed_dir = repo_root / "artifacts"
    reports_dir = processed_dir / "reports"
    synthetic = read_json(processed_dir / "synthetic_items.json")
    generation_prompts = read_json(processed_dir / "synthetic_generation_prompts.json")
    prompt_edit_queue = read_json(processed_dir / "synthetic_prompt_edit_queue.json")
    report = apply_manual_scenes_to_outputs(
        synthetic,
        generation_prompts,
        prompt_edit_queue,
        repo_root,
        strict=strict,
    )
    if report.get("status") != "skipped":
        write_json(processed_dir / "synthetic_items.json", synthetic)
        write_json(processed_dir / "synthetic_generation_prompts.json", generation_prompts)
        write_json(processed_dir / "synthetic_prompt_edit_queue.json", prompt_edit_queue)
    write_json(reports_dir / "manual_prompt_scene_review.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply manually refined prompt scenes to generated prompt outputs.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail when any item is missing or needs review")
    args = parser.parse_args()
    report = apply_manual_scenes(args.repo.resolve(), strict=args.strict)
    print(report)


if __name__ == "__main__":
    main()
