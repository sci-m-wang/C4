from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

HEADING_RE = re.compile(r"^\s*-?\s*#{2,5}\s*(.+?)\s*$")
SLOT_RE = re.compile(r"^\s*-\s*(?:\*\*)?\s*([^:：*]+?)\s*(?:\*\*)?\s*[:：]\s*(.*)$")
BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")
SCHEME_RE = re.compile(r"^(?:(?:槽位)?方案\s*\d+|方案\s*\d+)$")
PAREN_RE = re.compile(r"[（(]([^()（）]+)[)）]")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def normalize_arrow(text: str) -> str:
    text = text.replace("→", "->").replace("—>", "->").replace("–>", "->")
    return re.sub(r"(?<!-)", "", text) if False else re.sub(r"(?<!-)>|＞", "->", text)


def clean_heading(raw: str) -> str | None:
    text = raw.strip().lstrip("- ").strip().rstrip("：:").strip()
    text = re.sub(r"^#+\s*", "", text).strip().rstrip("：:").strip()
    if not text or SCHEME_RE.match(text):
        return None
    if text.startswith("槽位方案"):
        return None
    return text


def clean_slot(raw: str) -> str:
    return raw.replace("**", "").strip().rstrip("：:").strip()


def split_note(raw_node: str) -> dict[str, Any]:
    raw = raw_node.strip()
    notes: list[str] = []
    for note in PAREN_RE.findall(raw):
        if note.strip():
            notes.append(note.strip())
    without_parens = PAREN_RE.sub("", raw).strip()
    if "，" in without_parens or "," in without_parens:
        parts = re.split(r"[，,]", without_parens, maxsplit=1)
        base = parts[0].strip()
        if len(parts) > 1 and parts[1].strip():
            notes.append(parts[1].strip())
    else:
        base = without_parens
    aliases: list[str] = []
    if "/" in base or "／" in base:
        pieces = [p.strip() for p in re.split(r"[/／]", base) if p.strip()]
        if pieces:
            base = pieces[0]
            aliases = pieces[1:]
    return {
        "raw": raw,
        "text": base.strip(),
        "aliases": aliases,
        "notes": notes,
    }


def parse_chain(raw_chain: str) -> dict[str, Any] | None:
    normalized = normalize_arrow(raw_chain)
    raw_nodes = [p.strip() for p in normalized.split("->") if p.strip()]
    if len(raw_nodes) < 2:
        return None
    parsed_nodes = [split_note(node) for node in raw_nodes]
    nodes = [node["text"] for node in parsed_nodes if node["text"]]
    if len(nodes) < 2:
        return None
    notes: list[dict[str, str]] = []
    for index, node in enumerate(parsed_nodes):
        for note in node["notes"]:
            notes.append({"node_index": index, "note": note})
        for alias in node["aliases"]:
            notes.append({"node_index": index, "note": f"alias:{alias}"})
    return {
        "raw_chain": raw_chain.strip(),
        "normalized_chain": normalized.strip(),
        "nodes": nodes,
        "raw_nodes": raw_nodes,
        "node_annotations": parsed_nodes,
        "notes": notes,
        "bridge_count": len(nodes) - 1,
        "landing_concept": nodes[-1],
        "substitution_text": nodes[-1],
    }


def find_spans(idiom: str, slot: str) -> list[list[int]]:
    if not idiom or not slot:
        return []
    spans: list[list[int]] = []
    start = 0
    while True:
        index = idiom.find(slot, start)
        if index < 0:
            break
        spans.append([index, index + len(slot)])
        start = index + 1
    return spans


def resolve_effective_slot(
    idiom: str, declared_slot: str, chain_nodes: list[str]
) -> tuple[str, list[list[int]], list[str]]:
    warnings: list[str] = []
    first_node = chain_nodes[0] if chain_nodes else declared_slot
    declared_spans = find_spans(idiom, declared_slot)
    first_spans = find_spans(idiom, first_node)
    if first_node == declared_slot and declared_spans:
        return declared_slot, declared_spans, warnings
    if first_node != declared_slot and first_spans:
        if declared_slot and first_node in declared_slot:
            warnings.append("declared_slot_refined_to_chain_start")
        else:
            warnings.append("chain_start_used_as_effective_slot")
        return first_node, first_spans, warnings
    if declared_spans:
        if first_node != declared_slot:
            warnings.append("chain_start_unanchored_declared_slot_used")
        return declared_slot, declared_spans, warnings
    fallback = declared_slot or first_node
    warnings.append("slot_unanchored")
    return fallback, [], warnings


def slot_status(spans: list[list[int]]) -> str:
    if not spans:
        return "unanchored"
    if len(spans) > 1:
        return "ambiguous"
    return "anchored"


def parse_markdown_file(path: Path, source_id: str | None = None, root: Path | None = None) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []
    current_idiom: str | None = None
    rel_path = path.relative_to(root).as_posix() if root and path.is_relative_to(root) else path.name
    annotation_source = source_id or path.stem
    for line_no, line in enumerate(text.splitlines(), start=1):
        heading_match = HEADING_RE.match(line)
        if heading_match:
            heading = clean_heading(heading_match.group(1))
            if heading:
                current_idiom = heading
            continue
        if not current_idiom:
            continue
        slot_match = SLOT_RE.match(line)
        if not slot_match:
            continue
        declared_slot = clean_slot(slot_match.group(1))
        tail = slot_match.group(2).strip()
        for chain_match in BRACKET_RE.finditer(tail):
            parsed = parse_chain(chain_match.group(1))
            if not parsed:
                continue
            effective_slot, spans, warnings = resolve_effective_slot(current_idiom, declared_slot, parsed["nodes"])
            rows.append(
                {
                    "idiom": current_idiom,
                    "declared_slot_text": declared_slot,
                    "slot_text": effective_slot,
                    "slot_spans": spans,
                    "slot_status": slot_status(spans),
                    "bridge": parsed,
                    "warnings": warnings,
                    "source": {
                        "source_id": annotation_source,
                        "file": rel_path,
                        "line": line_no,
                        "raw_line": line.strip(),
                        "raw_chain": chain_match.group(0),
                    },
                }
            )
    return rows


def bridge_quality_flags(slot_text: str, bridge: dict[str, Any], row_warnings: list[str]) -> dict[str, Any]:
    flags = list(row_warnings)
    first = bridge["nodes"][0] if bridge.get("nodes") else ""
    landing = bridge.get("substitution_text", "")
    if first != slot_text:
        flags.append("chain_start_differs_from_effective_slot")
    if not landing:
        flags.append("empty_landing")
    if landing == slot_text:
        flags.append("unchanged_landing")
    if not CJK_RE.search(landing):
        flags.append("landing_without_cjk")
    return {
        "status": "pass" if not flags else "review",
        "flags": sorted(set(flags)),
    }


def merge_bridge_rows(rows: list[dict[str, Any]], source_files: list[dict[str, str]] | None = None) -> dict[str, Any]:
    idiom_slots: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    bridge_index: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    top_warnings: list[dict[str, Any]] = []

    for row in rows:
        idiom = row["idiom"]
        slot_text = row["slot_text"]
        slot_map = idiom_slots[idiom]
        if slot_text not in slot_map:
            spans = row["slot_spans"]
            slot_map[slot_text] = {
                "slot_id": "",
                "text": slot_text,
                "span": spans[0] if len(spans) == 1 else None,
                "occurrences": spans,
                "status": row["slot_status"],
                "declared_slot_texts": [],
                "bridges": [],
            }
        slot = slot_map[slot_text]
        if row["declared_slot_text"] not in slot["declared_slot_texts"]:
            slot["declared_slot_texts"].append(row["declared_slot_text"])
        bridge_nodes = tuple(row["bridge"]["nodes"])
        key = (idiom, slot_text, bridge_nodes)
        if key not in bridge_index:
            bridge = {
                "bridge_id": "",
                "chain": row["bridge"]["nodes"],
                "raw_chain_examples": [row["bridge"]["raw_chain"]],
                "bridge_count": row["bridge"]["bridge_count"],
                "bridge_landing_concept": row["bridge"]["landing_concept"],
                "substitution_text": row["bridge"]["substitution_text"],
                "node_annotations": row["bridge"].get("node_annotations", []),
                "notes": row["bridge"].get("notes", []),
                "declared_slot_texts": [row["declared_slot_text"]],
                "sources": [row["source"]],
                "quality": bridge_quality_flags(slot_text, row["bridge"], row["warnings"]),
            }
            slot["bridges"].append(bridge)
            bridge_index[key] = bridge
        else:
            bridge = bridge_index[key]
            if row["bridge"]["raw_chain"] not in bridge["raw_chain_examples"]:
                bridge["raw_chain_examples"].append(row["bridge"]["raw_chain"])
            if row["declared_slot_text"] not in bridge["declared_slot_texts"]:
                bridge["declared_slot_texts"].append(row["declared_slot_text"])
            bridge["sources"].append(row["source"])
            merged_flags = set(bridge["quality"].get("flags", [])) | set(row["warnings"])
            bridge["quality"] = {
                "status": "pass" if not merged_flags else "review",
                "flags": sorted(merged_flags),
            }
        for warning in row["warnings"]:
            top_warnings.append(
                {
                    "idiom": idiom,
                    "declared_slot_text": row["declared_slot_text"],
                    "effective_slot_text": slot_text,
                    "chain": row["bridge"]["nodes"],
                    "warning": warning,
                    "source": row["source"],
                }
            )

    items: list[dict[str, Any]] = []
    for idiom in sorted(idiom_slots):
        slots = list(idiom_slots[idiom].values())
        slots.sort(key=lambda slot: (slot["span"] is None, slot["span"] or [99, 99], slot["text"]))
        for slot_index, slot in enumerate(slots, start=1):
            slot["slot_id"] = f"S{slot_index:02d}"
            slot["declared_slot_texts"].sort(key=lambda s: (len(s), s))
            slot["bridges"].sort(
                key=lambda bridge: (
                    bridge["bridge_count"],
                    len(bridge["substitution_text"]),
                    bridge["substitution_text"],
                    bridge["chain"],
                )
            )
            for bridge_index_in_slot, bridge in enumerate(slot["bridges"], start=1):
                bridge["bridge_id"] = f"{slot['slot_id']}-B{bridge_index_in_slot:03d}"
                bridge["declared_slot_texts"].sort(key=lambda s: (len(s), s))
        items.append(
            {
                "idiom": idiom,
                "slots": slots,
            }
        )

    return {
        "schema": "merged_slot_bridge_network_v1",
        "merge_policy": "All annotation-source slot schemes are flattened. Each idiom stores every anchored or unanchored effective slot and all deduplicated bridge chains; scheme IDs are intentionally not preserved.",
        "source_files": source_files or [],
        "stats": {
            "idioms": len(items),
            "slots": sum(len(item["slots"]) for item in items),
            "bridges": sum(len(slot["bridges"]) for item in items for slot in item["slots"]),
            "warnings": len(top_warnings),
        },
        "items": items,
        "warnings": top_warnings,
    }


def parse_bridge_networks(paths: list[Path], repo_root: Path) -> dict[str, Any]:
    source_files: list[dict[str, str]] = []
    rows: list[dict[str, Any]] = []
    for index, path in enumerate(paths, start=1):
        source_id = f"annotation_{index:02d}"
        source_files.append({"source_id": source_id, "file": path.relative_to(repo_root).as_posix()})
        rows.extend(parse_markdown_file(path, source_id=source_id, root=repo_root))
    return merge_bridge_rows(rows, source_files=source_files)
