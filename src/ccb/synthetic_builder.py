from __future__ import annotations

import hashlib
import itertools
import re
from collections import Counter, defaultdict
from typing import Any

from ccb.prompt_renderer import render_generation_prompt

ASCII_RE = re.compile(r"[A-Za-z]")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
BAD_CHARS_RE = re.compile(r"[《》()（）/／、，,。；;:：\[\]【】]")


def stable_id(*parts: str, length: int = 12) -> str:
    digest = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()
    return digest[:length]


def spans_overlap(a: list[int], b: list[int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def are_mutually_exclusive(selections: list[dict[str, Any]]) -> bool:
    spans = [selection["span"] for selection in selections]
    for left, right in itertools.combinations(spans, 2):
        if spans_overlap(left, right):
            return False
    return True


def review_bridge(slot_text: str, bridge: dict[str, Any]) -> dict[str, Any]:
    substitution = bridge.get("substitution_text", "").strip()
    flags: list[str] = []
    score = 1.0
    if not substitution:
        flags.append("empty_substitution")
    if substitution == slot_text:
        flags.append("unchanged_substitution")
    if ASCII_RE.search(substitution):
        flags.append("contains_ascii")
    if BAD_CHARS_RE.search(substitution):
        flags.append("contains_punctuation_or_variant_marker")
    if not CJK_RE.search(substitution):
        flags.append("no_cjk_substitution")
    if len(substitution) > 4:
        flags.append("substitution_too_long")
    elif len(substitution) > 3:
        flags.append("substitution_long_but_usable")
        score -= 0.15
    if bridge.get("quality", {}).get("status") == "review":
        source_flags = bridge.get("quality", {}).get("flags", [])
        if "declared_slot_refined_to_chain_start" not in source_flags:
            flags.extend(source_flags)
            score -= 0.1
    serious = {
        "empty_substitution",
        "unchanged_substitution",
        "contains_ascii",
        "contains_punctuation_or_variant_marker",
        "no_cjk_substitution",
        "substitution_too_long",
        "slot_unanchored",
        "chain_start_differs_from_effective_slot",
    }
    status = "pass" if not (set(flags) & serious) else "reject"
    return {
        "status": status,
        "score": round(max(score, 0.0), 3),
        "flags": sorted(set(flags)),
    }


def bridge_prefix_variants(bridge: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = bridge.get("chain", [])
    variants: list[dict[str, Any]] = []
    for bridge_count in range(1, len(nodes)):
        chain = nodes[: bridge_count + 1]
        is_full_chain = bridge_count == bridge.get("bridge_count")
        variant = {
            "bridge_id": bridge["bridge_id"] if is_full_chain else f"{bridge['bridge_id']}-P{bridge_count}",
            "chain": chain,
            "bridge_count": bridge_count,
            "bridge_landing_concept": chain[-1],
            "substitution_text": chain[-1],
            "sources": bridge.get("sources", []),
            "quality": {"status": "pass", "flags": []},
            "is_derived_prefix": not is_full_chain,
            "derived_from_bridge_id": bridge["bridge_id"],
        }
        variants.append(variant)
    return variants


def collect_candidate_bridges(network: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_idiom: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for item in network.get("items", []):
        idiom = item["idiom"]
        for slot in item.get("slots", []):
            if slot.get("status") != "anchored" or not slot.get("span"):
                continue
            for bridge in slot.get("bridges", []):
                for bridge_variant in bridge_prefix_variants(bridge):
                    bridge_review = review_bridge(slot["text"], bridge_variant)
                    if bridge_review["status"] != "pass":
                        continue
                    key = (idiom, slot["slot_id"], tuple(bridge_variant["chain"]))
                    if key in seen:
                        continue
                    seen.add(key)
                    candidate = {
                        "idiom": idiom,
                        "slot_id": slot["slot_id"],
                        "slot_text": slot["text"],
                        "declared_slot_texts": slot.get("declared_slot_texts", []),
                        "span": slot["span"],
                        "bridge_id": bridge_variant["bridge_id"],
                        "bridge_chain": bridge_variant["chain"],
                        "bridge_count": bridge_variant["bridge_count"],
                        "bridge_landing_concept": bridge_variant["bridge_landing_concept"],
                        "substitution_text": bridge_variant["substitution_text"],
                        "sources": bridge_variant.get("sources", []),
                        "is_derived_prefix": bridge_variant.get("is_derived_prefix", False),
                        "derived_from_bridge_id": bridge_variant.get("derived_from_bridge_id"),
                        "bridge_review": bridge_review,
                    }
                    by_idiom[idiom].append(candidate)
    for candidates in by_idiom.values():
        candidates.sort(key=bridge_sort_key)
    return by_idiom


def bridge_sort_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    substitution = candidate["substitution_text"]
    return (
        -candidate.get("bridge_review", {}).get("score", 0),
        candidate["bridge_count"],
        candidate.get("is_derived_prefix", False),
        len(substitution),
        candidate["span"],
        substitution,
        candidate["bridge_chain"],
    )


def replace_idiom(idiom: str, selections: list[dict[str, Any]]) -> str:
    pieces = list(idiom)
    for selection in sorted(selections, key=lambda item: item["span"][0], reverse=True):
        start, end = selection["span"]
        pieces[start:end] = [selection["substitution_text"]]
    return "".join(pieces)


def review_phrase(phrase: str, selections: list[dict[str, Any]]) -> dict[str, Any]:
    flags: list[str] = []
    score = sum(selection["bridge_review"]["score"] for selection in selections) / max(len(selections), 1)
    if ASCII_RE.search(phrase):
        flags.append("phrase_contains_ascii")
    if BAD_CHARS_RE.search(phrase):
        flags.append("phrase_contains_punctuation")
    if len(phrase) > 7:
        flags.append("phrase_too_long")
        score -= 0.25
    elif len(phrase) > 6:
        flags.append("phrase_long_but_usable")
        score -= 0.1
    if len({selection["substitution_text"] for selection in selections}) < len(selections):
        flags.append("repeated_substitution_text")
        score -= 0.1
    serious = {"phrase_contains_ascii", "phrase_contains_punctuation", "phrase_too_long"}
    return {
        "status": "pass" if not (set(flags) & serious) else "reject",
        "score": round(max(score, 0.0), 3),
        "flags": sorted(set(flags)),
    }


def combo_key(combo: list[dict[str, Any]]) -> tuple[Any, ...]:
    return (
        sum(int(item.get("is_derived_prefix", False)) for item in combo),
        sum(len(item["substitution_text"]) for item in combo),
        -sum(item["bridge_review"]["score"] for item in combo),
        [item["span"] for item in combo],
        [item["substitution_text"] for item in combo],
    )


def level_combos(candidates: list[dict[str, Any]], level: str) -> list[tuple[str, list[dict[str, Any]]]]:
    one_step = [candidate for candidate in candidates if candidate["bridge_count"] == 1]
    two_step = [candidate for candidate in candidates if candidate["bridge_count"] >= 2]
    combos: list[tuple[str, list[dict[str, Any]]]] = []
    if level == "L1":
        combos.extend(("single_one_step", [candidate]) for candidate in one_step)
    elif level == "L2":
        for pair in itertools.combinations(one_step, 2):
            pair_list = list(pair)
            if are_mutually_exclusive(pair_list):
                combos.append(("two_one_step", sorted(pair_list, key=lambda item: item["span"])))
    elif level == "L3":
        for left in one_step:
            for right in two_step:
                pair = sorted([left, right], key=lambda item: item["span"])
                if left["bridge_id"] != right["bridge_id"] and are_mutually_exclusive(pair):
                    combos.append(("one_step_plus_two_step", pair))
    elif level == "L4":
        for pair in itertools.combinations(two_step, 2):
            pair_list = sorted(pair, key=lambda item: item["span"])
            if are_mutually_exclusive(pair_list):
                combos.append(("two_two_step", pair_list))
    seen: set[tuple[str, tuple[str, ...]]] = set()
    deduped: list[tuple[str, list[dict[str, Any]]]] = []
    for mode, combo in sorted(combos, key=lambda item: combo_key(item[1])):
        key = (mode, tuple(candidate["bridge_id"] for candidate in combo))
        if key in seen:
            continue
        seen.add(key)
        deduped.append((mode, combo))
    return deduped


def build_item(idiom: str, level: str, mode: str, selections: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not are_mutually_exclusive(selections):
        return None
    phrase = replace_idiom(idiom, selections)
    phrase_review = review_phrase(phrase, selections)
    if phrase_review["status"] != "pass":
        return None
    item_id = f"syn_{level.lower()}_{stable_id(idiom, level, mode, phrase, *[s['bridge_id'] for s in selections])}"
    replaced_slots = []
    for selection in selections:
        replaced_slots.append(
            {
                "slot_text": selection["slot_text"],
                "declared_slot_texts": selection.get("declared_slot_texts", []),
                "span": selection["span"],
                "bridge_chain": selection["bridge_chain"],
                "bridge_count": selection["bridge_count"],
                "bridge_landing_concept": selection["bridge_landing_concept"],
                "substitution_text": selection["substitution_text"],
                "sources": selection.get("sources", []),
                "is_derived_prefix": selection.get("is_derived_prefix", False),
                "derived_from_bridge_id": selection.get("derived_from_bridge_id"),
                "bridge_review": selection["bridge_review"],
            }
        )
    prompt_bundle = render_generation_prompt(idiom, phrase, selections)
    return {
        "item_id": item_id,
        "source": "synthetic_bridge_network",
        "source_idiom": idiom,
        "level": level,
        "level_mode": mode,
        "final_substituted_phrase": phrase,
        "replaced_slots": replaced_slots,
        "landing_check": {
            "status": "pass",
            "rule": "Each substitution replaces only its own recorded slot span; multi-slot replacements are non-overlapping.",
        },
        "phrase_review": phrase_review,
        "prompt_scene": prompt_bundle["scene"],
        "prompt_scene_placeholder": prompt_bundle["scene_placeholder"],
        "prompt_review": prompt_bundle["review"],
        "generation_prompt": prompt_bundle["prompt"],
        "generation_prompt_template": prompt_bundle["prompt_template"],
        "negative_prompt": prompt_bundle["negative_prompt"],
    }


def item_selection_key(item: dict[str, Any]) -> tuple[Any, ...]:
    prompt_flags = set(item.get("prompt_review", {}).get("flags", []))
    phrase_flags = item.get("phrase_review", {}).get("flags", [])
    total_slot_width = sum(slot["span"][1] - slot["span"][0] for slot in item.get("replaced_slots", []))
    total_bridge_count = sum(slot["bridge_count"] for slot in item.get("replaced_slots", []))
    return (
        int("generic_multi_element_scene" in prompt_flags),
        len(phrase_flags),
        -item.get("phrase_review", {}).get("score", 0),
        len(item["final_substituted_phrase"]),
        -total_slot_width,
        total_bridge_count,
        item["final_substituted_phrase"],
        item["item_id"],
    )


def dedupe_items_for_level(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    best_by_phrase: dict[str, tuple[int, dict[str, Any]]] = {}
    duplicate_count = 0
    for index, item in enumerate(items):
        phrase = item["final_substituted_phrase"]
        current = best_by_phrase.get(phrase)
        if current is None:
            best_by_phrase[phrase] = (index, item)
            continue
        first_index, current_item = current
        duplicate_count += 1
        if item_selection_key(item) < item_selection_key(current_item):
            best_by_phrase[phrase] = (first_index, item)
    ordered = [item for _, item in sorted(best_by_phrase.values(), key=lambda pair: pair[0])]
    return ordered, duplicate_count


def build_synthetic_items(network: dict[str, Any], max_per_level_per_idiom: int = 1) -> dict[str, Any]:
    candidates_by_idiom = collect_candidate_bridges(network)
    items: list[dict[str, Any]] = []
    omitted: dict[str, dict[str, str]] = defaultdict(dict)
    deduped_duplicates = 0
    for idiom in sorted(candidates_by_idiom):
        candidates = candidates_by_idiom[idiom]
        for level in ["L1", "L2", "L3", "L4"]:
            level_items: list[dict[str, Any]] = []
            for mode, combo in level_combos(candidates, level):
                item = build_item(idiom, level, mode, combo)
                if item:
                    level_items.append(item)
            unique_level_items, duplicate_count = dedupe_items_for_level(level_items)
            deduped_duplicates += duplicate_count
            selected = unique_level_items[:max_per_level_per_idiom]
            items.extend(selected)
            if not selected:
                omitted[idiom][level] = "no legal non-overlapping bridge combo passed filtering"
    counts = Counter(item["level"] for item in items)
    return {
        "schema": "synthetic_bridge_prompt_items_v5",
        "difficulty_definition": {
            "L1": "one slot with exactly one bridge step",
            "L2": "two non-overlapping slots; each slot uses exactly one bridge step",
            "L3": "two non-overlapping slots: one one-step bridge and one two-or-more-step bridge",
            "L4": "two non-overlapping slots: both two-or-more-step bridges",
        },
        "filter_policy": "Rejects ASCII/punctuation-heavy/unchanged/overlong substitutions, expands bridge-chain prefixes as derived candidates, rejects overlapping slot replacements, fixes L2 to two one-step slots, deduplicates identical final substituted phrases within each idiom-level cell, and by default selects one item per idiom per level. Prompts are rendered as scene descriptions; prompt_template exposes {{SCENE_DESCRIPTION}} for manual rewriting.",
        "stats": {
            "items": len(items),
            "by_level": dict(sorted(counts.items())),
            "idioms_with_candidates": len(candidates_by_idiom),
            "omitted_level_cells": sum(len(levels) for levels in omitted.values()),
            "deduped_duplicate_items": deduped_duplicates,
            "max_per_level_per_idiom": max_per_level_per_idiom,
        },
        "items": items,
        "omitted_levels": dict(omitted),
    }


def build_generation_prompts(synthetic_items: dict[str, Any]) -> list[dict[str, Any]]:
    prompts = []
    for item in synthetic_items.get("items", []):
        prompts.append(
            {
                "item_id": item["item_id"],
                "source_idiom": item["source_idiom"],
                "level": item["level"],
                "level_mode": item["level_mode"],
                "final_substituted_phrase": item["final_substituted_phrase"],
                "prompt_scene": item.get("prompt_scene"),
                "prompt_scene_placeholder": item.get("prompt_scene_placeholder"),
                "prompt_template": item.get("generation_prompt_template"),
                "prompt": item["generation_prompt"],
                "negative_prompt": item["negative_prompt"],
                "prompt_review": item.get("prompt_review", {}),
            }
        )
    return prompts


def build_review_markdown(synthetic_items: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Synthetic Bridge Generation Review")
    lines.append("")
    lines.append(
        "This report is generated from the merged human slot-bridge network. It records which L1-L4 cells are present or omitted after legality and lightweight naturalness filtering."
    )
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    stats = synthetic_items.get("stats", {})
    lines.append(f"- Total approved prompt items: {stats.get('items', 0)}")
    for level, count in stats.get("by_level", {}).items():
        lines.append(f"- {level}: {count}")
    lines.append(f"- Omitted idiom-level cells: {stats.get('omitted_level_cells', 0)}")
    lines.append(f"- Deduplicated duplicate items: {stats.get('deduped_duplicate_items', 0)}")
    lines.append(f"- Max items per idiom-level cell: {stats.get('max_per_level_per_idiom', 1)}")
    prompt_flags = Counter(
        flag for item in synthetic_items.get("items", []) for flag in item.get("prompt_review", {}).get("flags", [])
    )
    if prompt_flags:
        lines.append(f"- Prompt review flags: {dict(sorted(prompt_flags.items()))}")
    lines.append("")
    lines.append("## Omitted Levels")
    lines.append("")
    omitted = synthetic_items.get("omitted_levels", {})
    if not omitted:
        lines.append("None.")
    else:
        for idiom in sorted(omitted):
            levels = ", ".join(f"{level} ({reason})" for level, reason in sorted(omitted[idiom].items()))
            lines.append(f"- {idiom}: {levels}")
    lines.append("")
    lines.append("## Sample Approved Items")
    lines.append("")
    for item in synthetic_items.get("items", [])[:40]:
        slots = "; ".join(
            f"{slot['slot_text']}->{slot['substitution_text']} ({slot['bridge_count']} step{'s' if slot['bridge_count'] > 1 else ''})"
            for slot in item["replaced_slots"]
        )
        flags = ", ".join(item.get("phrase_review", {}).get("flags", [])) or "none"
        prompt_flags = ", ".join(item.get("prompt_review", {}).get("flags", [])) or "none"
        scene = item.get("prompt_scene", "")
        lines.append(
            f"- `{item['item_id']}` {item['source_idiom']} / {item['level']} / {item['final_substituted_phrase']} / {slots} / phrase flags: {flags} / prompt flags: {prompt_flags} / scene: {scene}"
        )
    lines.append("")
    return "\n".join(lines)
