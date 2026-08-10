from __future__ import annotations

import importlib.util
from pathlib import Path


def load_utils():
    path = Path(__file__).parents[1] / "integrations/lmms_eval/c4_bench/utils.py"
    spec = importlib.util.spec_from_file_location("c4_lmms_eval_utils", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lmms_eval_parser_matches_primary_scoring_policy() -> None:
    utils = load_utils()
    direct = {"task": "H0", "answer": "一叶障目", "answer_aliases": []}
    assert utils.c4_process_results(direct, ["一叶障目"])["c4_exact_match"] == 1.0

    explained = {"task": "E0", "answer": "一叶障目", "answer_aliases": []}
    valid = utils.c4_process_results(explained, ['{"answer":"一叶障目"}'])
    assert valid == {"c4_exact_match": 1.0, "c4_json_valid": 1.0}

    recovered = utils.c4_process_results(explained, ["分析过程\n最终答案：一叶障目"])
    assert recovered == {"c4_exact_match": 1.0, "c4_json_valid": 0.0}


def test_lmms_eval_task_filters_and_primary_scope() -> None:
    utils = load_utils()

    class FakeDataset(list):
        def filter(self, predicate):
            return FakeDataset(row for row in self if predicate(row))

    rows = FakeDataset({"task": task} for task in ("H0", "H1", "H4", "E0", "E1"))
    assert [row["task"] for row in utils.c4_process_docs_h4(rows)] == ["H4"]

    group = Path(__file__).parents[1] / "integrations/lmms_eval/c4_bench/c4_bench.yaml"
    text = group.read_text(encoding="utf-8")
    assert "c4_bench_e1" not in text
    assert all(task in text for task in ("c4_bench_h0", "c4_bench_h1", "c4_bench_h4", "c4_bench_e0"))


def test_lmms_eval_configs_do_not_impose_generation_caps() -> None:
    config_dir = Path(__file__).parents[1] / "integrations/lmms_eval/c4_bench"
    payload = "\n".join(path.read_text(encoding="utf-8") for path in config_dir.glob("*.yaml"))
    assert "max_new_tokens" not in payload
    assert "max_tokens" not in payload
    assert "max_model_len" not in payload
