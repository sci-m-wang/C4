from __future__ import annotations

import json
from pathlib import Path

from ccb.build_all import build_all
from ccb.export_hf import export_hf_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_release_build_is_complete_and_portable() -> None:
    stats = build_all(REPO_ROOT)

    assert stats["synthetic"]["items"] == 184
    assert stats["human_items"] == 37
    assert stats["human_eval_views"] == 185
    assert stats["synthetic_eval_views"] == 920
    assert stats["eval_views_by_task"] == {"H0": 221, "H1": 221, "H4": 221, "E0": 221, "E1": 221}
    assert sum(stats["eval_views_by_task"][task] for task in ("H0", "H1", "H4", "E0")) == 884

    artifacts = REPO_ROOT / "artifacts"
    synthetic_items = json.loads((artifacts / "synthetic_items.json").read_text(encoding="utf-8"))["items"]
    manifest_items = json.loads((REPO_ROOT / "data/synthetic/manifest.json").read_text(encoding="utf-8"))["items"]
    human_views = json.loads((artifacts / "human_eval_views.json").read_text(encoding="utf-8"))
    synthetic_views = json.loads((artifacts / "synthetic_eval_views.json").read_text(encoding="utf-8"))
    all_views = human_views + synthetic_views

    assert {item["item_id"] for item in synthetic_items} == {item["item_id"] for item in manifest_items}
    assert all(view["image_path"].startswith("data/") for view in all_views)
    if (REPO_ROOT / "data/human/images").exists() and (REPO_ROOT / "data/synthetic/images").exists():
        assert all((REPO_ROOT / view["image_path"]).is_file() for view in all_views)
    assert human_views[0]["explanation_reference"]["bridge_units"]

    for path in artifacts.rglob("*"):
        if path.is_file():
            assert str(REPO_ROOT) not in path.read_text(encoding="utf-8")


def test_manifests_match_image_directories() -> None:
    human = json.loads((REPO_ROOT / "data/human/annotations.json").read_text(encoding="utf-8"))
    synthetic = json.loads((REPO_ROOT / "data/synthetic/manifest.json").read_text(encoding="utf-8"))

    assert len(human) == 37
    assert len(synthetic["items"]) == 184
    if (REPO_ROOT / "data/human/images").exists() and (REPO_ROOT / "data/synthetic/images").exists():
        assert all((REPO_ROOT / item["image_file"]).is_file() for item in human)
        assert all((REPO_ROOT / item["image_file"]).is_file() for item in synthetic["items"])


def test_hugging_face_export_contains_task_specific_questions(tmp_path: Path) -> None:
    build_all(REPO_ROOT)
    report = export_hf_dataset(REPO_ROOT, tmp_path, "sci-m-wang/C4-Eval")
    rows = [json.loads(line) for line in (tmp_path / "data/eval.jsonl").read_text(encoding="utf-8").splitlines()]

    assert report["task_rows"] == 1105
    assert report["item_rows"] == 221
    assert {row["task"] for row in rows} == {"H0", "H1", "H4", "E0", "E1"}
    assert all(row["question"] and row["answer"] and row["image"] for row in rows)
    assert all(row["candidates"] for row in rows if row["task"] == "H4")
    assert all(not row["candidates"] for row in rows if row["task"] != "H4")
