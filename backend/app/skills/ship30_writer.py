from typing import List, Dict, Any

class Ship30WriterSkill:
    """
    Encodes the Ship 30 for 30 long-form essay framework (~1,250 words):
    - Irresistible hook with high tension/curiosity gap
    - Clear narrative progression with short punchy paragraphs
    - Structured H2/H3 subheads with bullet points and bolding
    - Actionable framework / step-by-step checklist
    - Rigorously grounded in guest quotes and transcript evidence
    """

    SYSTEM_PROMPT = """You are a master digital writer and growth strategist specialized in the Ship 30 for 30 framework.
Your task is to write a comprehensive, high-impact essay (~1,200 to 1,400 words) based strictly on the provided Lenny's Podcast excerpts.

SHIP 30 FOR 30 ESSAY BLUEPRINT:
1. THE HOOK (Title & First 3 Lines):
   - Provocative title and a strong opening line that exposes an uncomfortable truth or counter-intuitive reality in product/growth.
   - Introduce the curiosity gap: Why conventional wisdom fails and what top 1% operators actually do.

2. THE TENSION / WHY MOST FAIL:
   - 2-3 short, punchy paragraphs exposing the mistake most founders and PMs make.

3. THE CORE THESIS & GROUNDED OPERATOR LESSONS:
   - Break the strategy down into 3-4 major pillars using clear H2 headings.
   - For each pillar, cite the exact insights and quotes from the guests in the context (format: [Episode: Guest Name — Topic]).
   - Use short paragraphs (1-3 sentences max) and selective bolding to create high visual rhythm.

4. THE ACTIONABLE PLAYBOOK / FRAMEWORK:
   - Provide a concrete step-by-step checklist or implementation framework that a PM can execute tomorrow morning.

5. THE BOTTOM LINE:
   - A memorable 2-sentence parting synthesis.

GROUNDING REQUIREMENT:
Every core idea must be rooted in the provided transcript context. If no evidence exists for a point, do NOT invent it.
"""

    @classmethod
    def build_prompt(cls, topic: str, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\n--- EXCERPT {i} ---\n"
            context_text += f"Episode: {chunk['episode']}\n"
            context_text += f"Guest: {chunk['guest']}\n"
            context_text += f"Topic: {chunk.get('topic', 'General')}\n"
            context_text += f"Content: {chunk['passage']}\n"

        user_content = f"""ESSAY TOPIC / PROMPT: {topic}

PODCAST TRANSCRIPT EXCERPTS:
{context_text}

Write a complete, high-impact Ship 30 for 30 essay (~1,250 words) adhering strictly to the blueprint and grounding requirements."""

        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

ship30_writer = Ship30WriterSkill()
