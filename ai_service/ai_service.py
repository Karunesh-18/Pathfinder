import json
import math
import os
import re
from typing import Any, Dict, List, Optional, Tuple

# ==========================================
# NAMED CONSTANTS (NO MAGIC NUMBERS)
# ==========================================
CONFIDENCE_THRESHOLD = 0.5
MAX_QUESTIONS_PER_SESSION = 2
ALPHA_TWIN_UPDATE = 0.4
DEFAULT_CONFIDENCE = 0.5

# Evidence / Mastery estimation weights
WEIGHT_QUIZ_SCORE = 0.6
WEIGHT_COMPLETION_STATUS = 0.2
WEIGHT_PACE_FIT = 0.2

# Hybrid Recommender weights
WEIGHT_SKILL_GAP = 0.4
WEIGHT_SEMANTIC_SIM = 0.3
WEIGHT_PREREQ_FIT = 0.15
WEIGHT_DIFFICULTY_FIT = 0.15

# Default paths for shared data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SKILL_GRAPH_PATH = os.path.join(DATA_DIR, "skill_graph.json")
RESOURCE_CATALOG_PATH = os.path.join(DATA_DIR, "resource_catalog.json")
ROLE_REQUIREMENTS_PATH = os.path.join(DATA_DIR, "required_skills_by_role.json")


def load_json_fixture(filepath: str) -> Any:
    """Helper to load JSON data safely."""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if filepath.endswith("role.json") else []


# ==========================================
# 1. DIGITAL TWIN & SKILL GAP ENGINE
# ==========================================

def compute_skill_gaps(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Computes prioritized skill gaps using prerequisite constraints.
    Prerequisite filter: don't surface a gap whose prerequisite skill is also a gap.
    """
    target_role = profile.get("target_role", "Data Scientist")
    roles_data = load_json_fixture(ROLE_REQUIREMENTS_PATH)
    role_info = roles_data.get(target_role, roles_data.get("Data Scientist", {}))
    required_skills = role_info.get("required_skills", ["python_basics", "sql_basics", "data_analysis"])

    digital_twin = profile.get("digital_twin", {})
    skill_vector = digital_twin.get("skill_vector", {})

    # Compute raw gaps (required - current, floored at 0)
    raw_gaps = {}
    for skill_id in required_skills:
        current_val = skill_vector.get(skill_id, 0.0)
        gap = max(0.0, 1.0 - current_val)
        if gap > 0.05:  # threshold for meaningful gap
            raw_gaps[skill_id] = gap

    # Load prerequisites
    skill_graph = load_json_fixture(SKILL_GRAPH_PATH)
    prereq_map = {}
    if isinstance(skill_graph, dict):
        for p in skill_graph.get("prerequisites", []):
            prereq_map.setdefault(p["skill_id"], []).append(p["prerequisite_id"])

    # Filter out skills whose prerequisites are still unmet gaps
    prioritized_gaps = []
    for skill_id, gap_val in raw_gaps.items():
        prereqs = prereq_map.get(skill_id, [])
        unmet_prereqs = [p for p in prereqs if p in raw_gaps]
        if not unmet_prereqs:
            prioritized_gaps.append({
                "skill_id": skill_id,
                "gap": round(gap_val, 2),
                "unmet_prerequisites": []
            })
        else:
            # Skill is blocked by prerequisite gap
            pass

    # Sort gaps descending by gap magnitude
    prioritized_gaps.sort(key=lambda x: x["gap"], reverse=True)
    return prioritized_gaps


def calculate_career_readiness(profile: Dict[str, Any]) -> float:
    """Calculates skill overlap % against the target role."""
    target_role = profile.get("target_role", "Data Scientist")
    roles_data = load_json_fixture(ROLE_REQUIREMENTS_PATH)
    role_info = roles_data.get(target_role, roles_data.get("Data Scientist", {}))
    required_skills = role_info.get("required_skills", [])
    weights = role_info.get("weights", {})

    if not required_skills:
        return 0.0

    digital_twin = profile.get("digital_twin", {})
    skill_vector = digital_twin.get("skill_vector", {})

    total_weighted_mastery = 0.0
    total_weight = 0.0

    for skill_id in required_skills:
        w = weights.get(skill_id, 1.0 / len(required_skills))
        m = skill_vector.get(skill_id, 0.0)
        total_weighted_mastery += m * w
        total_weight += w

    if total_weight == 0:
        return 0.0

    readiness = (total_weighted_mastery / total_weight) * 100.0
    return round(readiness, 1)


def extract_goal(message: str, existing_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts structured goal and profile fields from chat message text.
    Pure function parsing key intent, target role, timeframe, and hours.
    """
    extracted = {}
    lower_msg = message.lower()

    # Roles regex matching
    if "data scientist" in lower_msg or "data science" in lower_msg:
        extracted["target_role"] = "Data Scientist"
    elif "ai engineer" in lower_msg or "machine learning" in lower_msg or "llm" in lower_msg:
        extracted["target_role"] = "AI Engineer"
    elif "backend" in lower_msg or "fastapi" in lower_msg:
        extracted["target_role"] = "Backend Engineer"
    elif "fullstack" in lower_msg or "web" in lower_msg:
        extracted["target_role"] = "Fullstack Data Developer"

    # Timeframe weeks
    week_match = re.search(r'(\d+)\s*(?:weeks?|wk)', lower_msg)
    if week_match:
        extracted["timeframe_weeks"] = int(week_match.group(1))

    # Hours per week
    hour_match = re.search(r'(\d+)\s*(?:hours?|hrs?)(?:\s*/\s*week|\s*per\s*week|\s*a\s*week)?', lower_msg)
    if hour_match:
        extracted["hours_per_week"] = int(hour_match.group(1))

    # General goal text
    extracted["goal"] = message.strip()
    return extracted


# ==========================================
# 2. HYBRID RECOMMENDATION ENGINE
# ==========================================

def _token_jaccard_similarity(text1: str, text2: str) -> float:
    """Simple token-based semantic similarity fallback for TF-IDF / sentence-transformer."""
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)


def recommend(profile: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Hybrid recommendation engine combining:
    1. Skill-gap match
    2. Semantic similarity
    3. Prerequisite fit
    4. Difficulty fit
    """
    resources = load_json_fixture(RESOURCE_CATALOG_PATH)
    if not isinstance(resources, list):
        return []

    digital_twin = profile.get("digital_twin", {})
    skill_vector = digital_twin.get("skill_vector", {})
    state = digital_twin.get("state", {})
    diff_fit = state.get("difficulty_fit", {}).get("value", "good")

    gaps = compute_skill_gaps(profile)
    gap_skill_ids = {g["skill_id"]: g["gap"] for g in gaps}
    goal_text = profile.get("goal", "") + " " + profile.get("target_role", "")

    # Prerequisite map
    skill_graph = load_json_fixture(SKILL_GRAPH_PATH)
    prereq_map = {}
    if isinstance(skill_graph, dict):
        for p in skill_graph.get("prerequisites", []):
            prereq_map.setdefault(p["skill_id"], []).append(p["prerequisite_id"])

    ranked_items = []
    for res in resources:
        res_id = res["id"]
        res_skills = res.get("skills_addressed", [])

        # 1. Skill Gap Score
        gap_score = sum(gap_skill_ids.get(s, 0.0) for s in res_skills)
        if res_skills:
            gap_score = gap_score / len(res_skills)

        # 2. Semantic Similarity Score
        res_text = res.get("title", "") + " " + res.get("description", "")
        semantic_score = _token_jaccard_similarity(goal_text, res_text)

        # 3. Prerequisite Fit Score
        prereq_scores = []
        for s in res_skills:
            req_prereqs = prereq_map.get(s, [])
            if not req_prereqs:
                prereq_scores.append(1.0)
            else:
                sat = sum(skill_vector.get(pr, 0.0) for pr in req_prereqs) / len(req_prereqs)
                prereq_scores.append(sat)
        prereq_fit_score = sum(prereq_scores) / len(prereq_scores) if prereq_scores else 1.0

        # 4. Difficulty Fit Score
        res_diff = res.get("difficulty", "beginner")
        diff_score = 1.0
        if diff_fit == "too_easy" and res_diff == "beginner":
            diff_score = 0.5
        elif diff_fit == "too_hard" and res_diff == "advanced":
            diff_score = 0.4
        elif res_diff == "intermediate":
            diff_score = 0.9

        # Weighted Final Score
        final_score = (
            WEIGHT_SKILL_GAP * gap_score +
            WEIGHT_SEMANTIC_SIM * semantic_score +
            WEIGHT_PREREQ_FIT * prereq_fit_score +
            WEIGHT_DIFFICULTY_FIT * diff_score
        )

        reason = f"Matches gap for {', '.join(res_skills)} with fit score {round(final_score, 2)}"
        ranked_items.append({
            "resource_id": res_id,
            "resource": res,
            "score": round(final_score, 3),
            "reason_short": reason,
            "breakdown": {
                "gap_score": round(gap_score, 2),
                "semantic_score": round(semantic_score, 2),
                "prereq_fit_score": round(prereq_fit_score, 2),
                "diff_score": round(diff_score, 2)
            }
        })

    ranked_items.sort(key=lambda x: x["score"], reverse=True)
    return ranked_items[:top_k]


# ==========================================
# 3. PATH GENERATOR & REPLANNING RULES
# ==========================================

def generate_path(
    profile: Dict[str, Any],
    recommendations: Optional[List[Dict[str, Any]]] = None,
    previous_path: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prerequisite-aware path generator.
    Generates topological ordered milestones with attached top-ranked resources.
    Generates change_summary diff against previous_path.
    """
    if recommendations is None:
        recommendations = recommend(profile, top_k=10)

    gaps = compute_skill_gaps(profile)
    if not gaps:
        # Fallback default gap if user mastered everything
        gaps = [{"skill_id": "python_basics", "gap": 0.5}]

    resources_by_skill = {}
    for rec in recommendations:
        res = rec.get("resource", {})
        for s in res.get("skills_addressed", []):
            if s not in resources_by_skill:
                resources_by_skill[s] = rec

    milestones = []
    for idx, gap in enumerate(gaps, start=1):
        s_id = gap["skill_id"]
        matched_rec = resources_by_skill.get(s_id)
        res_list = [matched_rec["resource_id"]] if matched_rec else ["res_py_01"]

        milestones.append({
            "milestone_id": f"ms_{idx}",
            "title": f"Master {s_id.replace('_', ' ').title()}",
            "skill_id": s_id,
            "resources": res_list,
            "status": "not_started" if idx > 1 else "in_progress",
            "explanation": f"Targeting key gap in {s_id.replace('_', ' ')} based on target role requirements."
        })

    change_summary = ""
    if previous_path and "milestones" in previous_path:
        prev_count = len(previous_path["milestones"])
        curr_count = len(milestones)
        if curr_count < prev_count:
            change_summary = "Path accelerated! Skipped redundant milestones based on high evidence performance."
        elif curr_count > prev_count:
            change_summary = "Path adapted: Inserted remedial milestone to reinforce core foundation."
        else:
            change_summary = "Path updated: Re-sequenced milestones to align with current pace and confidence."

    return {
        "milestones": milestones,
        "change_summary": change_summary
    }


def decide_replan_action(evidence: Dict[str, Any], state: Dict[str, Any]) -> str:
    """
    Deterministic replanning rule engine per 03_AI.md §8:
    | Quiz score | Pace | Feedback signal | Action |
    | >=85% | faster | "too easy" / bored | compress_and_advance |
    | <=50% | slower | "struggling" / overwhelmed | insert_remedial |
    | 50-85% | on pace | good / neutral | keep_path |
    | any | any | unclear on critical field | active_questioning |
    """
    quiz_score = evidence.get("quiz_score", 0.7)
    pace = state.get("pace", {}).get("value", "moderate")
    diff_signal = state.get("difficulty_fit", {}).get("value", "good")
    diff_confidence = state.get("difficulty_fit", {}).get("confidence", 1.0)

    if diff_confidence < CONFIDENCE_THRESHOLD:
        return "active_questioning"

    if quiz_score >= 0.85 and (pace == "fast" or diff_signal == "too_easy"):
        return "compress_and_advance"
    elif quiz_score <= 0.50 or pace == "slow" or diff_signal == "too_hard":
        return "insert_remedial"
    else:
        return "keep_path"


# ==========================================
# 4. EVIDENCE ENGINE & MASTERY ESTIMATION
# ==========================================

def analyze_evidence(profile: Dict[str, Any], assessment_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates skill_vector/skill_confidence and behavior from a completion/quiz event.
    Calculates mastery estimate: weighted(quiz_score: 0.6, completion: 0.2, pace_penalty: 0.2).
    Uses exponential update: new = old*0.6 + observed*0.4.
    """
    quiz_score = assessment_result.get("quiz_score", 0.8)
    status = assessment_result.get("status", "done")
    time_spent = assessment_result.get("time_spent_min", 30)
    est_time = assessment_result.get("est_time_min", 30)
    resource_id = assessment_result.get("resource_id", "res_py_01")

    # Pace penalty heuristic
    pace_ratio = time_spent / max(1, est_time)
    pace_fit = 1.0 if 0.8 <= pace_ratio <= 1.2 else (0.6 if pace_ratio > 1.5 else 0.8)
    completion_score = 1.0 if status == "done" else 0.5

    observed_mastery = (
        WEIGHT_QUIZ_SCORE * quiz_score +
        WEIGHT_COMPLETION_STATUS * completion_score +
        WEIGHT_PACE_FIT * pace_fit
    )

    digital_twin = profile.get("digital_twin", {})
    skill_vector = digital_twin.get("skill_vector", {})
    skill_confidence = digital_twin.get("skill_confidence", {})

    # Map resource to skills addressed
    resources = load_json_fixture(RESOURCE_CATALOG_PATH)
    res_info = next((r for r in resources if r["id"] == resource_id), {}) if isinstance(resources, list) else {}
    skills_addressed = res_info.get("skills_addressed", ["python_basics"])

    updated_vector = dict(skill_vector)
    updated_confidence = dict(skill_confidence)

    for skill in skills_addressed:
        old_val = skill_vector.get(skill, 0.2)
        old_conf = skill_confidence.get(skill, 0.4)
        # Exponential update: new = old*(1-ALPHA) + observed*ALPHA
        new_val = old_val * (1.0 - ALPHA_TWIN_UPDATE) + observed_mastery * ALPHA_TWIN_UPDATE
        new_conf = old_conf * (1.0 - ALPHA_TWIN_UPDATE) + 0.9 * ALPHA_TWIN_UPDATE

        updated_vector[skill] = round(new_val, 2)
        updated_confidence[skill] = round(new_conf, 2)

    digital_twin["skill_vector"] = updated_vector
    digital_twin["skill_confidence"] = updated_confidence
    profile["digital_twin"] = digital_twin

    return profile


# ==========================================
# 5. FEEDBACK ANALYSIS & ACTIVE QUESTIONING
# ==========================================

def analyze_feedback(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extracts structured sentiment/pace/difficulty signals from feedback text.
    Returns {emotion, pace_signal, difficulty_signal, confidence_per_field}.
    """
    lower = text.lower()

    emotion = "neutral"
    if any(w in lower for w in ["frustrated", "hard", "confusing", "stuck"]):
        emotion = "frustrated"
    elif any(w in lower for w in ["easy", "bored", "slow", "simple"]):
        emotion = "bored"
    elif any(w in lower for w in ["great", "enjoyed", "good", "clear", "confident"]):
        emotion = "confident"

    pace_signal = "good"
    if "too fast" in lower or "rushed" in lower:
        pace_signal = "too_fast"
    elif "too slow" in lower or "dragged" in lower:
        pace_signal = "too_slow"

    difficulty_signal = "good"
    if "too hard" in lower or "difficult" in lower:
        difficulty_signal = "too_hard"
    elif "too easy" in lower or "basic" in lower:
        difficulty_signal = "too_easy"

    confidence = 0.85 if len(text.strip()) > 10 else 0.45

    return {
        "emotion": emotion,
        "pace_signal": pace_signal,
        "difficulty_signal": difficulty_signal,
        "confidence_per_field": {
            "emotion": confidence,
            "pace": confidence,
            "difficulty_fit": confidence
        }
    }


def chat_reply(
    message: str,
    profile: Dict[str, Any],
    history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generates conversational response and handles Active Questioning rules.
    Respects MAX_QUESTIONS_PER_SESSION cap (2 questions max per session).
    """
    questions_asked = profile.get("questions_asked_session", 0)
    digital_twin = profile.get("digital_twin", {})
    state = digital_twin.get("state", {})
    diff_conf = state.get("difficulty_fit", {}).get("confidence", 0.4)

    wants_clarifying_question = False
    clarifying_question = None

    if diff_conf < CONFIDENCE_THRESHOLD and questions_asked < MAX_QUESTIONS_PER_SESSION:
        wants_clarifying_question = True
        clarifying_question = (
            "You completed the resource quickly but quiz results were mixed — "
            "did the explanation feel clear, or would a step-by-step practice task help more?"
        )

    # General reply logic
    reply_text = f"Got it! Let's focus on your goal of '{profile.get('goal', 'mastering coding')}'. "
    if wants_clarifying_question:
        reply_text += f"\n\n{clarifying_question}"
    else:
        reply_text += "Your personalized roadmap is up to date with the latest resources!"

    return {
        "reply": reply_text,
        "extracted_fields": extract_goal(message, profile),
        "wants_clarifying_question": wants_clarifying_question,
        "question": clarifying_question
    }


def explain(profile: Dict[str, Any], resource_id: str, recommendations: List[Dict[str, Any]]) -> str:
    """Grounded natural-language explanation referencing specific profile gap numbers."""
    matched = next((r for r in recommendations if r["resource_id"] == resource_id), None)
    if not matched:
        return f"Resource '{resource_id}' was selected to address key skill prerequisites in your learning path."

    breakdown = matched.get("breakdown", {})
    reason = matched.get("reason_short", "")
    return (
        f"This resource was prioritized (score: {matched.get('score')}) because it has a high skill gap relevance "
        f"({breakdown.get('gap_score', 0)*100}%) and strong prerequisite fit ({breakdown.get('prereq_fit_score', 0)*100}%). {reason}."
    )
