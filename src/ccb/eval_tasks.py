from __future__ import annotations

import hashlib
from typing import Any

TASKS = {
    "H0": "image_only_idiom_answer",
    "H1": "cross_concept_hint_idiom_answer",
    "H4": "candidate_constrained_idiom_answer",
    "E0": "free_answer_with_explanation",
    "E1": "gold_answer_explanation",
}


def stable_hash(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


def h0_prompt() -> str:
    return "你会看到一张图。请猜它对应的中文成语。只输出一个成语，不要解释。"


def h1_prompt() -> str:
    return (
        "你会看到一张图。这张图可能通过谐音、拆字、替换、角色联想、物品联想等跨概念方式表达一个中文成语。"
        "请根据图像线索猜成语。只输出一个成语，不要解释。"
    )


def h4_prompt(candidates: list[str]) -> str:
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[: len(candidates)]
    option_lines = [f"{label}. {candidate}" for label, candidate in zip(labels, candidates, strict=False)]
    return (
        "你会看到一张图。它通过跨概念方式表达下面候选成语之一。\n"
        + "\n".join(option_lines)
        + "\n请只输出最可能的成语，不要输出选项字母，不要解释。"
    )


def e0_prompt() -> str:
    return """你会看到一张图。这张图是某个中文成语的跨概念创意表达。
请先给出你认为的成语，再解释你如何从图像线索推到这个成语。
必须返回 JSON，不要输出 JSON 以外的文字，格式如下：
{
  "answer": "成语",
  "perceptual_cues": ["你看见的关键图像线索"],
  "bridge_analysis": [
    {"visual_or_textual_cue": "线索", "bridged_concept": "被联想到的概念", "idiom_part": "对应的成语片段"}
  ],
  "final_rationale": "一句话说明整体推理"
}"""


def e1_prompt(gold_idiom: str) -> str:
    return f"""你会看到一张图。已知它表达的成语是“{gold_idiom}”。
请解释图像中的关键线索如何通过跨概念桥接到这个成语。
必须返回 JSON，不要输出 JSON 以外的文字，格式如下：
{{
  "answer": "{gold_idiom}",
  "perceptual_cues": ["你看见的关键图像线索"],
  "bridge_analysis": [
    {{"visual_or_textual_cue": "线索", "bridged_concept": "被联想到的概念", "idiom_part": "对应的成语片段"}}
  ],
  "final_rationale": "一句话说明整体推理"
}}"""


def candidate_score(answer: str, candidate: str) -> tuple[int, int]:
    shared = len(set(answer) & set(candidate))
    return shared, stable_hash(answer + "::" + candidate)


def make_candidates(answer: str, pool: list[str], k: int = 4) -> list[str]:
    unique_pool = sorted({item for item in pool if item and item != answer})
    distractors = sorted(
        unique_pool, key=lambda item: (-candidate_score(answer, item)[0], candidate_score(answer, item)[1], item)
    )[: max(k - 1, 0)]
    candidates = distractors + [answer]
    insert_at = stable_hash(answer) % len(candidates)
    candidates.remove(answer)
    candidates.insert(insert_at, answer)
    return candidates


def synthetic_reference_explanation(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "answer": item["source_idiom"],
        "bridge_paths": [
            {
                "idiom_part": slot["slot_text"],
                "slot_span": slot["span"],
                "bridge_chain": slot["bridge_chain"],
                "bridge_count": slot["bridge_count"],
                "landing_concept": slot["bridge_landing_concept"],
                "visible_substitution": slot["substitution_text"],
            }
            for slot in item.get("replaced_slots", [])
        ],
        "short_rationale": f"图像应表现替换短语“{item['final_substituted_phrase']}”，需要把可见替换概念反向桥接回“{item['source_idiom']}”。",
    }


def human_reference_explanation(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "answer": item.get("gold_idiom"),
        "visible_cues": item.get("visible_cues", []),
        "bridge_units": item.get("bridge_units", []),
        "answer_alignment": item.get("answer_alignment", []),
        "simple_rationale": item.get("simple_rationale", ""),
        "difficulty": item.get("difficulty", {}),
    }


def build_eval_views_for_base(
    base: dict[str, Any], all_answers: list[str], explanation_reference: dict[str, Any]
) -> list[dict[str, Any]]:
    expected = base["expected_answer"]
    candidates = make_candidates(expected, all_answers)
    common = {
        "item_id": base["item_id"],
        "origin": base["origin"],
        "image_path": base.get("image_path"),
        "expected_answer": expected,
        "answer_aliases": base.get("answer_aliases", []),
        "explanation_reference": explanation_reference,
    }
    return [
        {**common, "eval_task": "H0", "task_name": TASKS["H0"], "prompt": h0_prompt()},
        {**common, "eval_task": "H1", "task_name": TASKS["H1"], "prompt": h1_prompt()},
        {
            **common,
            "eval_task": "H4",
            "task_name": TASKS["H4"],
            "candidates": candidates,
            "prompt": h4_prompt(candidates),
        },
        {**common, "eval_task": "E0", "task_name": TASKS["E0"], "prompt": e0_prompt()},
        {**common, "eval_task": "E1", "task_name": TASKS["E1"], "prompt": e1_prompt(expected)},
    ]


def build_human_eval_views(human_items: list[dict[str, Any]], all_answers: list[str]) -> list[dict[str, Any]]:
    views: list[dict[str, Any]] = []
    for item in human_items:
        gold = item.get("gold_idiom")
        if not gold:
            continue
        file_name = item.get("file_name") or f"{gold}.jpg"
        base = {
            "item_id": item.get("item_id") or f"human_{gold}",
            "origin": "human_seed_figure",
            "image_path": f"data/human/images/{file_name}",
            "expected_answer": gold,
            "answer_aliases": item.get("answer_aliases", []),
        }
        views.extend(build_eval_views_for_base(base, all_answers, human_reference_explanation(item)))
    return views


def build_synthetic_eval_views(synthetic_items: list[dict[str, Any]], all_answers: list[str]) -> list[dict[str, Any]]:
    views: list[dict[str, Any]] = []
    for item in synthetic_items:
        base = {
            "item_id": item["item_id"],
            "origin": "synthetic_bridge_prompt",
            "image_path": f"data/synthetic/images/{item['item_id']}.png",
            "expected_answer": item["source_idiom"],
            "generation_prompt_ref": item["generation_prompt"],
            "level": item["level"],
            "level_mode": item["level_mode"],
        }
        item_views = build_eval_views_for_base(base, all_answers, synthetic_reference_explanation(item))
        for view in item_views:
            view["level"] = item["level"]
            view["level_mode"] = item["level_mode"]
        views.extend(item_views)
    return views
