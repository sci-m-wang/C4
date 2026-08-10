from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from ccb.bridge_parser import parse_bridge_networks
from ccb.eval_tasks import build_human_eval_views, build_synthetic_eval_views
from ccb.io_utils import read_json, write_json, write_text
from ccb.manual_scenes import apply_manual_scenes_to_outputs
from ccb.synthetic_builder import build_generation_prompts, build_review_markdown, build_synthetic_items


def load_human_explanations(path: Path) -> list[dict[str, Any]]:
    data = read_json(path)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("items"), list):
            return data["items"]
        if isinstance(data.get("data"), list):
            return data["data"]
    raise ValueError(f"Unsupported explanation JSON shape: {path}")


def build_all(repo_root: Path, max_per_level_per_idiom: int = 1) -> dict[str, Any]:
    reviewed_dir = repo_root / "data" / "annotations"
    source_paths = [reviewed_dir / "bridge_annotations_01.md", reviewed_dir / "bridge_annotations_02.md"]
    missing = [str(path) for path in source_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing reviewed label files: " + ", ".join(missing))

    network = parse_bridge_networks(source_paths, repo_root=repo_root)
    synthetic = build_synthetic_items(network, max_per_level_per_idiom=max_per_level_per_idiom)
    generation_prompts = build_generation_prompts(synthetic)
    prompt_edit_queue = [
        {
            "item_id": prompt["item_id"],
            "source_idiom": prompt["source_idiom"],
            "level": prompt["level"],
            "level_mode": prompt["level_mode"],
            "final_substituted_phrase": prompt["final_substituted_phrase"],
            "auto_prompt_scene": prompt.get("prompt_scene"),
            "manual_prompt_scene": prompt.get("prompt_scene_placeholder"),
            "prompt_template": prompt.get("prompt_template"),
            "negative_prompt": prompt.get("negative_prompt"),
        }
        for prompt in generation_prompts
    ]
    manual_scene_report = apply_manual_scenes_to_outputs(synthetic, generation_prompts, prompt_edit_queue, repo_root)
    human_items = load_human_explanations(repo_root / "data" / "human" / "annotations.json")

    answer_pool = sorted(
        {item["idiom"] for item in network.get("items", [])}
        | {item.get("gold_idiom", "") for item in human_items if item.get("gold_idiom")}
    )
    human_views = build_human_eval_views(human_items, answer_pool)
    synthetic_views = build_synthetic_eval_views(synthetic.get("items", []), answer_pool)

    processed_dir = repo_root / "artifacts"
    reports_dir = processed_dir / "reports"
    write_json(processed_dir / "synthetic_slot_bridge_networks.json", network)
    write_json(processed_dir / "synthetic_items.json", synthetic)
    write_json(processed_dir / "synthetic_generation_prompts.json", generation_prompts)
    write_json(processed_dir / "synthetic_prompt_edit_queue.json", prompt_edit_queue)
    write_json(processed_dir / "human_eval_views.json", human_views)
    write_json(processed_dir / "synthetic_eval_views.json", synthetic_views)
    write_json(reports_dir / "manual_prompt_scene_review.json", manual_scene_report)
    write_json(
        processed_dir / "eval_task_templates.json",
        {
            "schema": "eval_task_templates_v1",
            "tasks": {
                "H0": "image-only answer; no cross-concept hint",
                "H1": "image answer with generic cross-concept hint",
                "H4": "image answer with candidate choices",
                "E0": "free answer plus structured explanation",
                "E1": "gold answer provided; structured explanation only",
            },
        },
    )
    write_text(reports_dir / "synthetic_generation_review.md", build_review_markdown(synthetic))

    stats = {
        "network": network.get("stats", {}),
        "synthetic": synthetic.get("stats", {}),
        "human_items": len(human_items),
        "human_eval_views": len(human_views),
        "manual_scene_report": manual_scene_report,
        "synthetic_eval_views": len(synthetic_views),
        "eval_views_by_task": dict(Counter(view["eval_task"] for view in human_views + synthetic_views)),
        "outputs": {
            "network": "artifacts/synthetic_slot_bridge_networks.json",
            "synthetic_items": "artifacts/synthetic_items.json",
            "generation_prompts": "artifacts/synthetic_generation_prompts.json",
            "prompt_edit_queue": "artifacts/synthetic_prompt_edit_queue.json",
            "human_eval_views": "artifacts/human_eval_views.json",
            "synthetic_eval_views": "artifacts/synthetic_eval_views.json",
            "review": "artifacts/reports/synthetic_generation_review.md",
            "manual_scene_review": "artifacts/reports/manual_prompt_scene_review.json",
        },
    }
    write_json(reports_dir / "build_stats.json", stats)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build merged bridge networks, synthetic prompts, and eval task views."
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--max-per-level-per-idiom", type=int, default=1)
    args = parser.parse_args()
    stats = build_all(args.repo.resolve(), max_per_level_per_idiom=args.max_per_level_per_idiom)
    print("Build complete")
    print(stats)


if __name__ == "__main__":
    main()
