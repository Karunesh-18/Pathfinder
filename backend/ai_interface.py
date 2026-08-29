import logging
import time
from typing import Any, Dict, List, Optional
import ai_service
from backend.config import settings

logger = logging.getLogger("ai_interface")
logger.setLevel(logging.INFO)

class AIInterface:
    @staticmethod
    def process_chat(message: str, profile: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        start = time.time()
        res = ai_service.chat_reply(message, profile, history)
        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(f"chat_reply latency: {elapsed}ms")

        # Enforce server-side session cap for clarifying questions
        questions_asked = profile.get("questions_asked_session", 0)
        if res.get("wants_clarifying_question"):
            if questions_asked >= settings.MAX_QUESTIONS_PER_SESSION:
                res["asked_clarifying_question"] = False
                res["question"] = None
                res["reply"] = "Got it! Rebuilding your roadmap based on current estimations."
            else:
                res["asked_clarifying_question"] = True
                profile["questions_asked_session"] = questions_asked + 1
        else:
            res["asked_clarifying_question"] = False

        return res

    @staticmethod
    def get_recommendations(profile: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        start = time.time()
        recs = ai_service.recommend(profile, top_k=top_k)
        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(f"recommend latency: {elapsed}ms")
        return recs

    @staticmethod
    def generate_path(profile: Dict[str, Any], recommendations: Optional[List[Dict[str, Any]]] = None, previous_path: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.time()
        path = ai_service.generate_path(profile, recommendations, previous_path)
        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(f"generate_path latency: {elapsed}ms")
        return path

    @staticmethod
    def analyze_evidence(profile: Dict[str, Any], assessment_result: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        updated_profile = ai_service.analyze_evidence(profile, assessment_result)
        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(f"analyze_evidence latency: {elapsed}ms")
        return updated_profile

    @staticmethod
    def analyze_feedback(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.time()
        fb = ai_service.analyze_feedback(text, context)
        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(f"analyze_feedback latency: {elapsed}ms")
        return fb

    @staticmethod
    def explain(profile: Dict[str, Any], resource_id: str, recommendations: List[Dict[str, Any]]) -> str:
        start = time.time()
        exp = ai_service.explain(profile, resource_id, recommendations)
        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(f"explain latency: {elapsed}ms")
        return exp
