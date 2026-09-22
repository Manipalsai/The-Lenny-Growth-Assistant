from typing import List, Dict, Any

class GroundedQASkill:
    """
    Constructs prompts strictly grounded in Lenny's Podcast transcripts.
    Refuses out-of-domain or unsupported claims.
    """

    SYSTEM_PROMPT = """You are The Lenny Growth Assistant, a specialized AI for product managers and growth leaders.
Your knowledge comes EXCLUSIVELY from the provided Lenny's Podcast transcript excerpts.

CRITICAL RULES:
1. Base your answer ONLY on the provided Context excerpts.
2. Every factual assertion, recommendation, or tactic MUST be attributed to the specific guest and episode from the excerpts using the citation format: [Episode: Guest Name — Topic].
3. If the provided excerpts DO NOT contain sufficient evidence to answer the question, you MUST clearly state:
   "Based on the available Lenny's Podcast transcript archive, there is insufficient evidence to answer this question."
   Do NOT attempt to fabricate, hallucinate, or use external knowledge.
4. Maintain a structured, professional tone suitable for a VP of Product or Head of Growth.
5. Highlight disagreements or contrasting viewpoints between different guests when present.
"""

    @classmethod
    def build_prompt(cls, query: str, context_chunks: List[Dict[str, Any]], history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": cls.SYSTEM_PROMPT}]

        # Append recent conversation history if provided (up to last 4 turns)
        if history:
            for h in history[-4:]:
                if h.get("role") in ["user", "assistant"]:
                    messages.append({"role": h["role"], "content": h["content"]})

        # Build context block
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\n--- EXCERPT {i} ---\n"
            context_text += f"Episode: {chunk['episode']}\n"
            context_text += f"Guest: {chunk['guest']}\n"
            context_text += f"Topic/Timestamp: {chunk.get('topic', 'General')}\n"
            context_text += f"Content: {chunk['passage']}\n"

        user_content = f"""QUESTION: {query}

TRANSCRIPT CONTEXT EXCERPTS:
{context_text}

Please provide a grounded answer with inline citations in the format [Episode: Guest Name — Topic]."""

        messages.append({"role": "user", "content": user_content})
        return messages

grounded_qa = GroundedQASkill()
