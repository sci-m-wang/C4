from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ccb.io_utils import read_json, write_json

TASK_ORDER = {task: index for index, task in enumerate(("H0", "H1", "H4", "E0", "E1"))}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def hub_image_path(local_path: str) -> str:
    path = Path(local_path)
    if path.parts[:3] == ("data", "human", "images"):
        return (Path("images/human") / path.name).as_posix()
    if path.parts[:3] == ("data", "synthetic", "images"):
        return (Path("images/synthetic") / path.name).as_posix()
    raise ValueError(f"Unsupported image path: {local_path}")


def hub_image_url(dataset_repo: str, image_path: str) -> str:
    encoded_path = quote(image_path, safe="/")
    return f"https://huggingface.co/datasets/{dataset_repo}/resolve/main/{encoded_path}"


def task_row(view: dict[str, Any], dataset_repo: str) -> dict[str, Any]:
    image_path = hub_image_path(view["image_path"])
    return {
        "instance_id": f"{view['item_id']}__{view['eval_task']}",
        "item_id": view["item_id"],
        "origin": view["origin"],
        "image": hub_image_url(dataset_repo, image_path),
        "image_path": image_path,
        "task": view["eval_task"],
        "task_name": view["task_name"],
        "question": view["prompt"],
        "answer": view["expected_answer"],
        "answer_aliases": view.get("answer_aliases", []),
        "candidates": view.get("candidates", []),
        "level": view.get("level", ""),
        "level_mode": view.get("level_mode", ""),
        "explanation_reference": json.dumps(view.get("explanation_reference", {}), ensure_ascii=False),
    }


def item_rows(repo_root: Path, dataset_repo: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in read_json(repo_root / "data/human/annotations.json"):
        image_path = hub_image_path(item["image_file"])
        rows.append(
            {
                "item_id": item["item_id"],
                "origin": "human_seed_figure",
                "image": hub_image_url(dataset_repo, image_path),
                "image_path": image_path,
                "answer": item["gold_idiom"],
                "level": "",
                "level_mode": "",
                "metadata": json.dumps(item, ensure_ascii=False),
            }
        )
    synthetic = read_json(repo_root / "artifacts/synthetic_items.json")["items"]
    for item in synthetic:
        local_path = f"data/synthetic/images/{item['item_id']}.png"
        image_path = hub_image_path(local_path)
        rows.append(
            {
                "item_id": item["item_id"],
                "origin": "synthetic_bridge_prompt",
                "image": hub_image_url(dataset_repo, image_path),
                "image_path": image_path,
                "answer": item["source_idiom"],
                "level": item["level"],
                "level_mode": item["level_mode"],
                "metadata": json.dumps(item, ensure_ascii=False),
            }
        )
    return sorted(rows, key=lambda row: row["item_id"])


def export_hf_dataset(repo_root: Path, output_dir: Path, dataset_repo: str) -> dict[str, Any]:
    artifacts = repo_root / "artifacts"
    human_views = read_json(artifacts / "human_eval_views.json")
    synthetic_views = read_json(artifacts / "synthetic_eval_views.json")
    tasks = [task_row(view, dataset_repo) for view in human_views + synthetic_views]
    tasks.sort(key=lambda row: (row["item_id"], TASK_ORDER[row["task"]]))
    items = item_rows(repo_root, dataset_repo)

    write_jsonl(output_dir / "data/eval.jsonl", tasks)
    write_jsonl(output_dir / "data/items.jsonl", items)
    write_json(output_dir / "data/task_templates.json", read_json(artifacts / "eval_task_templates.json"))

    report = {
        "schema": "c4_huggingface_export_v1",
        "dataset_repo": dataset_repo,
        "task_rows": len(tasks),
        "item_rows": len(items),
        "tasks": dict(sorted(Counter(row["task"] for row in tasks).items())),
    }
    write_json(output_dir / "export_report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Export C4 Bench as task-level Hugging Face dataset rows.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--dataset-repo", default="anonymous/C4-Eval")
    args = parser.parse_args()
    report = export_hf_dataset(args.repo.resolve(), args.output.resolve(), args.dataset_repo)
    print(report)


if __name__ == "__main__":
    main()
