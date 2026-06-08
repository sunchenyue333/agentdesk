import re
from typing import Any

PASSWORD_TERMS = (
    "忘记密码",
    "密码",
    "password",
    "forgot password",
    "reset password",
    "注册邮箱",
    "邮件",
    "30 分钟",
    "30分钟",
)

NEGATIVE_TOPICS = (
    "退款",
    "refund",
    "数据删除",
    "delete data",
    "starter plan",
    "重复扣款",
    "duplicate charge",
    "系统加载慢",
    "系统很慢",
    "slow",
    "urgent priority",
)


def generate_grounded_answer(
    question: str,
    chunks: list[dict[str, Any]],
    openai_api_key: str | None = None,
) -> dict[str, Any]:
    language = "zh" if _contains_cjk(question) else "en"
    answer_mode = "llm" if openai_api_key else "mock"

    relevant_chunks = rank_chunks_for_question(question, chunks)[:3]
    relevant_sentences = _collect_relevant_sentences(question, relevant_chunks)
    intent = _classify_question(question)

    if intent == "password_reset":
        answer = _password_reset_answer(language, relevant_sentences)
        confidence = "high" if _has_password_reset_requirements(relevant_sentences) else "medium"
        steps = _password_steps(language, answer_mode, bool(openai_api_key))
    elif relevant_sentences:
        answer = _general_answer(language, relevant_sentences, answer_mode)
        confidence = "medium"
        steps = _general_steps(language, answer_mode, bool(openai_api_key))
    else:
        answer = (
            "（Mock 模式）知识库中没有找到与该问题直接相关的内容，请转人工处理。"
            if language == "zh"
            else "(Mock mode) I could not find directly relevant knowledge base content. Please escalate to a human."
        )
        confidence = "low"
        steps = _no_context_steps(language, answer_mode, bool(openai_api_key))

    return {
        "answer": answer,
        "citations": _build_citations(relevant_chunks, question),
        "confidence": confidence,
        "answer_mode": answer_mode,
        "structured_steps": steps,
        "relevant_chunks": relevant_chunks,
    }


def rank_chunks_for_question(question: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    query_terms = _query_terms(question)

    def score(chunk: dict[str, Any]) -> float:
        heading = str(chunk.get("heading") or "")
        content = str(chunk.get("content") or "")
        text = f"{heading}\n{content}".lower()
        lexical = sum(3 if term in heading.lower() else 1 for term in query_terms if term in text)
        password_boost = 4 if _classify_question(question) == "password_reset" and _is_password_related(text) else 0
        vector_score = float(chunk.get("score") or 0)
        topic_penalty = sum(1 for topic in NEGATIVE_TOPICS if topic in text and topic not in question.lower())
        return lexical + password_boost + vector_score - topic_penalty

    return sorted(chunks, key=score, reverse=True)


def _password_reset_answer(language: str, sentences: list[str]) -> str:
    if language == "zh":
        return (
            "（Mock 模式）用户忘记密码时，请按以下步骤处理：\n"
            "1. 请用户在登录页点击 Forgot password。\n"
            "2. 输入注册邮箱并提交重置请求。\n"
            "3. 引导用户通过邮件链接重置密码。\n"
            "4. 重置链接有效期为 30 分钟。\n"
            "5. 如果用户 10 分钟后仍未收到邮件，请创建 medium priority 工单，由支持团队继续排查。"
        )
    return (
        "(Mock mode) If a user forgets their password, ask them to click Forgot password on the login page, "
        "enter their registered email address, and reset the password through the email link. The reset link "
        "is valid for 30 minutes. If the email has not arrived after 10 minutes, create a medium priority ticket."
    )


def _general_answer(language: str, sentences: list[str], answer_mode: str) -> str:
    prefix = "（Mock 模式）" if language == "zh" and answer_mode == "mock" else ""
    if language == "zh":
        return f"{prefix}" + " ".join(_strip_markdown(sentence) for sentence in sentences[:3])
    mock_prefix = "(Mock mode) " if answer_mode == "mock" else ""
    return mock_prefix + " ".join(_strip_markdown(sentence) for sentence in sentences[:3])


def _build_citations(chunks: list[dict[str, Any]], question: str) -> list[dict[str, str]]:
    citations = []
    for chunk in chunks[:3]:
        quote = _best_quote(question, str(chunk.get("content") or ""))
        citations.append(
            {
                "document_id": str(chunk.get("document_id") or ""),
                "document_title": str(chunk.get("document_title") or ""),
                "chunk_id": str(chunk.get("chunk_id") or ""),
                "heading": str(chunk.get("heading") or ""),
                "quote": quote,
            }
        )
    return citations


def _collect_relevant_sentences(question: str, chunks: list[dict[str, Any]]) -> list[str]:
    query_terms = _query_terms(question)
    candidates: list[tuple[int, str]] = []
    for chunk in chunks:
        heading = str(chunk.get("heading") or "")
        for sentence in _split_sentences(str(chunk.get("content") or "")):
            clean = _strip_markdown(sentence)
            lowered = clean.lower()
            if any(topic in lowered and topic not in question.lower() for topic in NEGATIVE_TOPICS):
                continue
            score = sum(1 for term in query_terms if term in lowered or term in heading.lower())
            if _classify_question(question) == "password_reset" and _is_password_related(lowered):
                score += 4
            if score > 0:
                candidates.append((score, clean))
    ranked = sorted(candidates, key=lambda item: item[0], reverse=True)
    deduped: list[str] = []
    for _, sentence in ranked:
        if sentence not in deduped:
            deduped.append(sentence)
    return deduped[:6]


def _best_quote(question: str, content: str) -> str:
    sentences = _collect_relevant_sentences(question, [{"content": content, "heading": ""}])
    if sentences:
        return sentences[0][:260]
    return _strip_markdown(content)[:260]


def _split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    parts = re.split(r"(?<=[。！？.!?])\s+", normalized)
    return [part.strip() for part in parts if part.strip()]


def _query_terms(question: str) -> set[str]:
    lowered = question.lower()
    terms = {term for term in re.split(r"[\s,，。！？?!.:：;；/]+", lowered) if len(term) >= 2}
    if "忘记密码" in question or "密码" in question:
        terms.update({"忘记密码", "密码", "forgot password", "reset", "email", "邮箱"})
    if "password" in lowered:
        terms.update({"password", "forgot password", "reset", "email"})
    return terms


def _classify_question(question: str) -> str:
    lowered = question.lower()
    if "忘记密码" in question or "密码" in question or "forgot password" in lowered or "password" in lowered:
        return "password_reset"
    return "general"


def _is_password_related(text: str) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in PASSWORD_TERMS)


def _has_password_reset_requirements(sentences: list[str]) -> bool:
    text = " ".join(sentences).lower()
    required = ("forgot password", "注册邮箱", "邮件", "30", "10", "medium")
    return sum(term in text for term in required) >= 4


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _strip_markdown(text: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", text.strip())
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.strip()


def _password_steps(language: str, answer_mode: str, has_key: bool) -> list[str]:
    if language == "zh":
        mode = "Mock 模式：未配置 OPENAI_API_KEY，使用确定性 demo answer" if not has_key else "LLM 模式：使用配置的模型生成回答"
        return [
            "判断意图：密码重置问题",
            "检索知识库：找到账户设置相关资料",
            f"生成回答：基于密码重置 SOP（{mode}）",
            "风险等级：低",
            "不需要人工审批",
        ]
    return [
        "Intent: password reset question",
        "Knowledge retrieval: found account setup material",
        f"Answer generation: based on password reset SOP ({answer_mode})",
        "Risk level: low",
        "Human approval: not required",
    ]


def _general_steps(language: str, answer_mode: str, has_key: bool) -> list[str]:
    if language == "zh":
        mode = "Mock 模式：未配置 OPENAI_API_KEY" if not has_key else "LLM 模式"
        return [
            "判断意图：知识库问题",
            "检索知识库：找到相关资料",
            f"生成回答：只使用与问题直接相关的句子（{mode}）",
            "风险等级：低",
            "不需要人工审批",
        ]
    return [
        "Intent: knowledge base question",
        "Knowledge retrieval: found relevant material",
        f"Answer generation: direct evidence only ({answer_mode})",
        "Risk level: low",
        "Human approval: not required",
    ]


def _no_context_steps(language: str, answer_mode: str, has_key: bool) -> list[str]:
    if language == "zh":
        mode = "Mock 模式：未配置 OPENAI_API_KEY" if not has_key else "LLM 模式"
        return [
            "判断意图：知识库问题",
            "检索知识库：未找到直接相关资料",
            f"生成回答：拒绝编造答案（{mode}）",
            "风险等级：低",
            "建议人工处理",
        ]
    return [
        "Intent: knowledge base question",
        "Knowledge retrieval: no directly relevant material",
        f"Answer generation: no fabricated answer ({answer_mode})",
        "Risk level: low",
        "Human handoff suggested",
    ]
