import pytest
from ai_service import (
    decide_replan_action,
    compute_skill_gaps,
    recommend,
    generate_path,
    analyze_evidence
)

def test_decide_replan_action_compress():
    evidence = {"quiz_score": 0.90}
    state = {"pace": {"value": "fast"}, "difficulty_fit": {"value": "too_easy", "confidence": 0.9}}
    action = decide_replan_action(evidence, state)
    assert action == "compress_and_advance"

def test_decide_replan_action_remedial():
    evidence = {"quiz_score": 0.40}
    state = {"pace": {"value": "slow"}, "difficulty_fit": {"value": "too_hard", "confidence": 0.9}}
    action = decide_replan_action(evidence, state)
    assert action == "insert_remedial"

def test_decide_replan_action_keep():
    evidence = {"quiz_score": 0.75}
    state = {"pace": {"value": "moderate"}, "difficulty_fit": {"value": "good", "confidence": 0.8}}
    action = decide_replan_action(evidence, state)
    assert action == "keep_path"

def test_decide_replan_action_uncertain():
    evidence = {"quiz_score": 0.75}
    state = {"pace": {"value": "moderate"}, "difficulty_fit": {"value": "good", "confidence": 0.3}}
    action = decide_replan_action(evidence, state)
    assert action == "active_questioning"

def test_compute_skill_gaps():
    profile = {
        "target_role": "Data Scientist",
        "digital_twin": {
            "skill_vector": {"python_basics": 0.9, "sql_basics": 0.2}
        }
    }
    gaps = compute_skill_gaps(profile)
    assert isinstance(gaps, list)
    # sql_basics gap should be present
    gap_skills = [g["skill_id"] for g in gaps]
    assert "sql_basics" in gap_skills

def test_generate_path():
    profile = {
        "target_role": "Data Scientist",
        "digital_twin": {
            "skill_vector": {"python_basics": 0.1, "sql_basics": 0.1}
        }
    }
    recs = recommend(profile, top_k=5)
    path = generate_path(profile, recs)
    assert "milestones" in path
    assert len(path["milestones"]) > 0
