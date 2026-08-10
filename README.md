# C4 Bench

This repository contains the method implementation for **Chengyu-based Cross-Concept Creative Benchmark (C4 Bench)**. It focuses on the reproducible bridge-controlled construction framework, task materialization, Hugging Face export, and deterministic scoring utilities.

The complete evaluation set, including 221 images and 1,105 task-level question-answer instances, is hosted at [sci-m-wang/C4-Eval](https://huggingface.co/datasets/sci-m-wang/C4-Eval).

## Contents

- `src/ccb/`: bridge parsing, controlled item construction, prompt rendering, task generation, and scoring.
- `data/annotations/`: two independently authored bridge annotation sources under anonymous identifiers.
- `data/manual_scenes/`: manually reviewed scene descriptions for the four construction levels.
- `data/human/`: structured explanation annotations for 37 curated seed figures.
- `data/synthetic/`: generation manifest for 184 synthetic figures.

The annotations describe 221 base figures. Each figure is materialized into five evaluation views, yielding 1,105 task instances. Image files and ready-to-use task rows are distributed through the Hugging Face dataset above.

## Construction

The framework begins with a four-character Chengyu target and a reviewed cross-concept bridge network. Candidate substitutions are selected only when their target spans do not overlap. Four controlled configurations are instantiated:

| Level | Bridge-controlled configuration |
|---|---|
| L1 | one slot, one bridge step |
| L2 | two non-overlapping slots, one bridge step each |
| L3 | two non-overlapping slots, one one-step and one multi-step bridge |
| L4 | two non-overlapping slots, two multi-step bridges |

Generated phrases are filtered for anchoring, overlap, unchanged substitutions, punctuation-heavy forms, and excessive length. The selected substitutions are then rendered into reviewed scene prompts. Synthetic figures were generated with `gpt-image-2`; the exact scene and full generation prompt for every item are retained in `data/synthetic/manifest.json`.

## Evaluation Views

The build produces five views per image:

- `H0`: direct image-to-Chengyu answer.
- `H1`: image-to-Chengyu answer with a generic cross-concept hint.
- `H4`: candidate-constrained answer.
- `E0`: free answer with a structured bridge explanation.
- `E1`: explanation with the gold answer provided.

The primary score is exact recovery over `H0`, `H1`, `H4`, and the parsed answer from `E0`. `E1` is reserved for explanation analysis and is excluded from the primary score. JSON validity is recorded separately from answer correctness; the parser conservatively recovers explicitly marked answers when a model emits reasoning without a valid JSON envelope.

## Reproduce

```bash
uv sync
uv run ccb-build --repo .
uv run ccb-export-hf --repo . --output hf_export
uv run pytest
```

The build writes reproducible derived files to `artifacts/`. All paths stored in generated JSON are repository-relative.

Expected build counts:

```text
synthetic items: 184
human items: 37
evaluation views: 1,105
primary-score instances: 884
```

No model-serving code, credentials, machine-specific configuration, run logs, paper sources, or leaderboard outputs are included in this artifact.

## Integrated Evaluation

A ready-to-run [lmms-eval](https://github.com/EvolvingLMMs-Lab/lmms-eval)
task pack is included in `integrations/lmms_eval/c4_bench`. It exposes the
four-task 884-instance primary score as `c4_bench` and the explanation task as
`c4_bench_e1`, while preserving the published prompts and official answer
parser. See the [integration guide](integrations/lmms_eval/c4_bench/README.md)
for the command and protocol details.

## Load the Evaluation Set

```python
from datasets import load_dataset

test = load_dataset("sci-m-wang/C4-Eval", split="test")
print(test[0]["question"], test[0]["answer"])
```

Each row contains the image, exact question, task identifier, gold answer, aliases, candidates when applicable, difficulty metadata, and a structured explanation reference. See the dataset card for the complete schema.

## Citation

If you use C4 Bench in your research, please cite the arXiv preprint:

```bibtex
@misc{wang2026mllmsdecodecreativeleap,
      title={Can MLLMs Decode the Creative Leap? Introducing C4 for Cross-Concept Understanding},
      author={Ming Wang and Yuqing Zhang and Tingna Xie and Xiangju Li and Xiaocui Yang and Daling Wang and Shi Feng and Yifei Zhang},
      year={2026},
      eprint={2608.06501},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2608.06501},
}
```
