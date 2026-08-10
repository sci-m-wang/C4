from ccb.score_answers import parse_task_answer, primary_score, score_task_output


def test_direct_and_explanation_answers_are_parsed_by_task() -> None:
    direct = score_task_output("H0", "一叶障目\n", "一叶障目")
    explanation = score_task_output("E0", '```json\n{"answer": "一叶障目"}\n```', "一叶障目")

    assert direct["exact_match"] is True
    assert direct["valid_json"] is None
    assert explanation["exact_match"] is True
    assert explanation["valid_json"] is True


def test_explicit_answer_is_recovered_when_json_is_invalid() -> None:
    answer, valid_json, error = parse_task_answer("E0", "分析略。答案是一叶障目。")

    assert answer == "一叶障目"
    assert valid_json is False
    assert error


def test_primary_score_excludes_e1() -> None:
    result = primary_score(
        [
            {"eval_task": "H0", "exact_match": True},
            {"eval_task": "H1", "exact_match": False},
            {"eval_task": "H4", "exact_match": True},
            {"eval_task": "E0", "exact_match": True},
            {"eval_task": "E1", "exact_match": True},
        ]
    )

    assert result == {
        "exact": 3,
        "total": 4,
        "score": 0.75,
        "included_tasks": ["E0", "H0", "H1", "H4"],
    }
