import json
import math
import re
from collections import Counter

import httpx

from app.core.config import settings


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "for",
    "from",
    "i",
    "in",
    "is",
    "me",
    "my",
    "of",
    "on",
    "or",
    "someone",
    "teach",
    "the",
    "to",
    "want",
    "with",
    "you",
}

CATEGORY_RULES = {
    "programming": {"python", "react", "javascript", "typescript", "backend", "frontend", "api"},
    "design": {"design", "figma", "ui", "ux", "graphics", "illustrator"},
    "data": {"excel", "sql", "analytics", "data", "powerbi", "tableau"},
    "language": {"english", "spanish", "hindi", "speaking", "grammar", "writing"},
    "business": {"marketing", "sales", "resume", "interview", "product", "startup"},
    "creative": {"music", "guitar", "piano", "photography", "video", "editing"},
}


def _tokenize(text: str | None) -> list[str]:
    if not text:
        return []
    return re.findall(r"[a-z0-9+#]{2,}", text.lower())


def _important_tokens(*values: str | None) -> list[str]:
    tokens = []
    for value in values:
        tokens.extend(token for token in _tokenize(value) if token not in STOPWORDS)
    return tokens


def _normalize_title(raw_title: str | None, description: str, category: str | None) -> str:
    if raw_title:
        return raw_title.strip().title()
    tokens = _important_tokens(description, category)
    if not tokens:
        return "Skill Support"
    return " ".join(token.capitalize() for token in tokens[:3])


def _infer_category(title: str | None, description: str, current_category: str | None) -> str:
    if current_category:
        return current_category.strip().title()
    tokens = set(_important_tokens(title, description))
    for category, keywords in CATEGORY_RULES.items():
        if tokens.intersection(keywords):
            return category.title()
    return "General"


def _infer_proficiency(description: str, current_level: str | None) -> str | None:
    if current_level:
        return current_level
    lowered = description.lower()
    if any(keyword in lowered for keyword in {"advanced", "expert", "deep dive"}):
        return "advanced"
    if any(keyword in lowered for keyword in {"beginner", "basic", "start", "new to"}):
        return "beginner"
    if any(keyword in lowered for keyword in {"intermediate", "improve", "practice"}):
        return "intermediate"
    return None


def _infer_availability(description: str, current_availability: str | None) -> str | None:
    if current_availability:
        return current_availability
    lowered = description.lower()
    if "weekend" in lowered:
        return "weekends"
    if "evening" in lowered:
        return "evenings"
    if "morning" in lowered:
        return "mornings"
    return None


def _extract_tags(*values: str | None) -> list[str]:
    counts = Counter(_important_tokens(*values))
    tags = []
    for token, _count in counts.most_common(8):
        if token.isdigit():
            continue
        tags.append(token)
    return sorted(set(tags))


def _build_summary(title: str, category: str, description: str, skill_type: str) -> str:
    direction = "offers" if skill_type == "offer" else "needs help with"
    summary_body = description.strip().split(".")[0].strip()
    if not summary_body:
        summary_body = f"{direction} {title.lower()} support"
    return f"{title} ({category}) {direction} {summary_body[:180]}".strip()


def _maybe_call_llm(prompt: str) -> dict | None:
    if not settings.llm_api_key:
        return None
    try:
        response_format: dict = {
            "type": "json_schema",
            "json_schema": {
                "name": "skill_listing_metadata",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "category": {"type": "string"},
                        "ai_summary": {"type": "string"},
                        "proficiency_level": {
                            "type": ["string", "null"],
                        },
                        "availability": {
                            "type": ["string", "null"],
                        },
                        "tag_names": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "title",
                        "category",
                        "ai_summary",
                        "proficiency_level",
                        "availability",
                        "tag_names",
                    ],
                    "additionalProperties": False,
                },
            },
        }

        # Ollama's OpenAI-compatible endpoint documents JSON mode support. Use
        # json_object for the local compatibility path instead of json_schema.
        if "localhost:11434" in settings.llm_base_url or "127.0.0.1:11434" in settings.llm_base_url:
            response_format = {"type": "json_object"}

        payload = {
            "model": settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return JSON only. Keep answers concise and structured for a "
                        "skill exchange marketplace."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": response_format,
        }

        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json=payload,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception:
        return None


def _maybe_embed_text(text: str) -> list[float] | None:
    if not settings.llm_api_key or not text.strip():
        return None
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{settings.llm_base_url.rstrip('/')}/embeddings",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.embedding_model,
                    "input": text,
                },
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
    except Exception:
        return None


def generate_skill_metadata(
    *,
    title: str,
    category: str,
    description: str,
    skill_type: str,
    proficiency_level: str | None,
    availability: str | None,
) -> dict[str, str | list[str] | None]:
    prompt = (
        "Normalize this skill listing into JSON with keys title, category, ai_summary, "
        "proficiency_level, availability, tag_names. "
        f"title={title!r}, category={category!r}, description={description!r}, "
        f"skill_type={skill_type!r}, proficiency_level={proficiency_level!r}, "
        f"availability={availability!r}"
    )
    llm_result = _maybe_call_llm(prompt)
    if llm_result:
        return {
            "title": llm_result.get("title") or _normalize_title(title, description, category),
            "category": llm_result.get("category") or _infer_category(title, description, category),
            "ai_summary": llm_result.get("ai_summary")
            or _build_summary(title, category, description, skill_type),
            "proficiency_level": llm_result.get("proficiency_level") or proficiency_level,
            "availability": llm_result.get("availability") or availability,
            "tag_names": [
                str(tag).strip().lower()
                for tag in llm_result.get("tag_names", [])
                if str(tag).strip()
            ][:8],
        }

    normalized_title = _normalize_title(title, description, category)
    normalized_category = _infer_category(title, description, category)
    inferred_proficiency = _infer_proficiency(description, proficiency_level)
    inferred_availability = _infer_availability(description, availability)
    return {
        "title": normalized_title,
        "category": normalized_category,
        "ai_summary": _build_summary(normalized_title, normalized_category, description, skill_type),
        "proficiency_level": inferred_proficiency,
        "availability": inferred_availability,
        "tag_names": _extract_tags(title, category, description, normalized_category),
    }


def suggest_skill_listing(payload: dict) -> dict:
    metadata = generate_skill_metadata(**payload)
    return {
        "title": metadata["title"],
        "category": metadata["category"],
        "description": payload["description"].strip(),
        "skill_type": payload["skill_type"],
        "proficiency_level": metadata["proficiency_level"] or payload.get("proficiency_level"),
        "availability": metadata["availability"] or payload.get("availability"),
        "ai_summary": metadata["ai_summary"],
        "tag_names": metadata["tag_names"],
    }


def build_search_document(skill, tag_names: list[str]) -> str:
    return " ".join(
        part
        for part in [
            skill.title,
            skill.category,
            skill.description,
            skill.proficiency_level,
            skill.availability,
            skill.ai_summary,
            " ".join(tag_names),
            getattr(skill.owner, "city", None),
        ]
        if part
    )


def get_text_embedding(text: str) -> list[float] | None:
    return _maybe_embed_text(text)


def serialize_embedding(vector: list[float] | None) -> str | None:
    if vector is None:
        return None
    return json.dumps(vector)


def deserialize_embedding(raw_vector: str | None) -> list[float] | None:
    if not raw_vector:
        return None
    try:
        data = json.loads(raw_vector)
        if isinstance(data, list):
            return [float(value) for value in data]
    except Exception:
        return None
    return None


def _jaccard_score(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _cosine_similarity(left: list[float] | None, right: list[float] | None) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def score_skill_match(request_skill, offer_skill) -> dict[str, float | str | list[str]]:
    request_embedding = deserialize_embedding(getattr(request_skill, "embedding_vector", None))
    offer_embedding = deserialize_embedding(getattr(offer_skill, "embedding_vector", None))

    request_terms = set(
        _important_tokens(
            request_skill.title,
            request_skill.category,
            request_skill.description,
            request_skill.ai_summary,
            " ".join(request_skill.tag_names),
        )
    )
    offer_terms = set(
        _important_tokens(
            offer_skill.title,
            offer_skill.category,
            offer_skill.description,
            offer_skill.ai_summary,
            " ".join(offer_skill.tag_names),
        )
    )
    shared_terms = sorted(request_terms & offer_terms)
    lexical_score = _jaccard_score(request_terms, offer_terms)
    embedding_score = _cosine_similarity(request_embedding, offer_embedding)
    if request_embedding and offer_embedding:
        score = (embedding_score * 0.78) + (lexical_score * 0.22)
    else:
        score = (lexical_score * 0.85)
    if request_skill.category.lower() == offer_skill.category.lower():
        score += 0.15
    if request_skill.title.lower() == offer_skill.title.lower():
        score += 0.25
    score = min(round(score, 3), 0.99)
    rationale = (
        f"Embedding similarity {embedding_score:.2f} with shared concepts: {', '.join(shared_terms[:4])}"
        if shared_terms
        else f"Embedding similarity {embedding_score:.2f} with related listing intent"
    )
    return {
        "score": score,
        "rationale": rationale,
        "shared_tags": shared_terms[:6],
    }


def search_skill_against_query(query: str, skill) -> dict[str, float | str | list[str]]:
    query_embedding = get_text_embedding(query)
    skill_embedding = deserialize_embedding(getattr(skill, "embedding_vector", None))
    query_terms = set(_important_tokens(query))
    skill_terms = set(_important_tokens(skill.search_document or "", " ".join(skill.tag_names)))
    matched_terms = sorted(query_terms & skill_terms)
    lexical_score = _jaccard_score(query_terms, skill_terms)
    embedding_score = _cosine_similarity(query_embedding, skill_embedding)
    if query_embedding and skill_embedding:
        score = (embedding_score * 0.8) + (lexical_score * 0.2)
    else:
        score = lexical_score
    if skill.owner.city and skill.owner.city.lower() in query.lower():
        score += 0.2
    if skill.skill_type.value == "offer" and any(
        term in query.lower() for term in {"learn", "need", "mentor", "tutor", "teach"}
    ):
        score += 0.1
    score = min(round(score, 3), 0.99)
    rationale = (
        f"Embedding similarity {embedding_score:.2f}; matched on {', '.join(matched_terms[:4])}"
        if matched_terms
        else f"Embedding similarity {embedding_score:.2f}; matched semantically using listing content"
    )
    return {
        "score": score,
        "rationale": rationale,
        "matched_terms": matched_terms[:8],
    }


def draft_exchange_message(requested_skill, offered_skill, sender_name: str) -> str:
    offered_text = (
        f" In return, I can offer {offered_skill.title}."
        if offered_skill is not None
        else ""
    )
    return (
        f"Hi, I am {sender_name}. I would like to connect about your {requested_skill.title} "
        f"listing because it matches what I am trying to learn or improve.{offered_text} "
        "If this works for you, we can align on schedule and goals."
    )
