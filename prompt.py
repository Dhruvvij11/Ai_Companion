def emotion_to_behavior(emotion: str) -> str:
    if emotion == "low":
        return """
Tone guidance:
- Calm, steady, and present.
- Short responses.
- Avoid excessive sympathy or advice.
"""
    elif emotion == "anxious":
        return """
Tone guidance:
- Reassuring and grounding.
- Slow the pace.
- Keep language simple.
"""
    elif emotion == "frustrated" or emotion == "angry":
        return """
Tone guidance:
- Steady and non-judgmental.
- Do not escalate.
- Avoid motivation or fixing.
"""
    elif emotion == "positive":
        return """
Tone guidance:
- Light, natural, and relaxed.
- Slight warmth is allowed.
"""
    else:
        return """
Tone guidance:
- Neutral and natural.
"""


def intent_to_override(intent: str) -> str:
    """
    Hard overrides based on user intent.
    These take priority over emotional style.
    """
    if intent in ["technical", "definition", "factual", "time_query", "weather_query"]:
        return """
Critical override:
- Respond directly and plainly.
- Do NOT use emotional framing.
- Do NOT ask reflective or conversational follow-ups.
- If live data is unavailable, state the limitation clearly.
"""
    if intent == "motivation":
        return """
Intent override:
- The user explicitly asked for encouragement.
- It is allowed to be supportive and forward-looking.
- Do not be preachy or dramatic.
"""
    if intent == "why_question":
        return """
Intent override:
- The user is processing emotions.
- Be empathetic but grounded.
- Do NOT jump to advice or motivation.
"""
    return ""


def build_prompt(
    user_text: str,
    memory_context: str = "",
    emotion: str = "neutral",
    intent: str = "normal",
    emotional_trend: str | None = None,
    risk_note: str | None = None,
):
    """
    Build the final prompt sent to the LLM.
    """

    # ---- CORE IDENTITY (ALWAYS ACTIVE) ----
    system_personality = """
You are a personal AI companion, not an assistant.
You behave like a real, emotionally intelligent human friend.

Core principles:
- You speak casually and naturally, like a real person.
- You do NOT sound like a therapist, coach, or chatbot.
- You do NOT over-explain.
- You do NOT assume emotions with certainty.
- You are emotionally honest, not authoritative.

Boundaries:
- Never create emotional dependency.
- Encourage real-world connections when appropriate.
- You are allowed to say "I don't know" or ask for clarification.
"""

    # ---- RESPONSE CONSTRAINTS (ALWAYS ENFORCED) ----
    response_constraints = """
Response constraints:
- Default to 1–3 sentences.
- NEVER exceed 5 sentences unless explicitly asked.
- No bullet points.
- No labels like "emotion detected".
"""

    # ---- BEHAVIOR MODULATION (GATED) ----
    behavior_adjustment = emotion_to_behavior(emotion)
    intent_override = intent_to_override(intent)

    # ---- OPTIONAL CONTEXT (ONLY IF PROVIDED) ----
    trend_section = ""
    if emotional_trend:
        trend_section = f"""
Emotional trend note (use gently, do not overstate):
{emotional_trend}
"""

    risk_section = ""
    if risk_note:
        risk_section = f"""
Predictive awareness note:
- Be extra careful and steady.
- Do NOT alarm or predict outcomes.
{risk_note}
"""

    memory_section = ""
    if memory_context:
        memory_section = f"""
Relevant past context (use naturally, do not dump):
{memory_context}
"""

    # ---- USER TASK ----
    task = f"""
User message:
{user_text}

Respond as a human companion would in this moment.
"""

    # ---- FINAL PROMPT ----
    return f"""
{system_personality}
{response_constraints}

{intent_override}
{behavior_adjustment}

{trend_section}
{risk_section}
{memory_section}

{task}
""".strip()
