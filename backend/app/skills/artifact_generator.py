import re
from typing import List, Dict, Any, Tuple

class ArtifactGeneratorSkill:
    """
    Constructs prompts to generate structured deliverables:
    - Interactive HTML/CSS dashboards and visual frameworks
    - Clean, production-ready Markdown playbooks & checklists
    """

    HTML_SYSTEM_PROMPT = """You are an elite product designer and UI engineer.
Your task is to generate a standalone, self-contained HTML/CSS visual dashboard or framework based on the provided Lenny's Podcast excerpts.

DESIGN REQUIREMENTS:
1. Provide a COMPLETE, standalone HTML document starting with <!DOCTYPE html> and containing all CSS within <style> tags.
2. Aesthetic: Sleek, modern, dark-mode SaaS UI (slate/indigo/sky palette, rounded-xl cards, subtle border gradients, clean flex/grid layouts).
3. Responsive & Interactive: Visually stunning layout representing the key growth levers, metrics, or frameworks described by the guests.
4. Content: Grounded strictly in the excerpts provided, citing the guest names and episodes.
5. NO EXTERNAL SCRIPTS: Do not use external CDN scripts or malicious event handlers. Use vanilla CSS and clean semantic HTML.
"""

    MARKDOWN_SYSTEM_PROMPT = """You are an executive product leader.
Your task is to generate a comprehensive, publication-grade Markdown framework, playbook, or checklist based on the provided Lenny's Podcast excerpts.

REQUIREMENTS:
1. Use clear Markdown typography (# Title, ## Sections, ### Sub-steps).
2. Include structured tables, callout blocks, and checklists.
3. Every recommendation must cite the supporting guest and episode [Episode: Guest — Topic].
"""

    @classmethod
    def build_prompt(cls, topic: str, artifact_type: str, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\n--- EXCERPT {i} ---\n"
            context_text += f"Episode: {chunk['episode']} | Guest: {chunk['guest']}\n"
            context_text += f"Content: {chunk['passage']}\n"

        system_prompt = cls.HTML_SYSTEM_PROMPT if artifact_type == "html" else cls.MARKDOWN_SYSTEM_PROMPT
        user_content = f"""DELIVERABLE TOPIC: {topic}

TRANSCRIPT CONTEXT:
{context_text}

Generate the complete {artifact_type.upper()} deliverable."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    @classmethod
    def extract_artifact(cls, raw_output: str, default_type: str = "markdown") -> Tuple[str, str, str]:
        """
        Extracts title, type, and clean content from model output.
        Returns (title, type, clean_content).
        """
        # Check if raw_output has an HTML block
        html_match = re.search(r'```(?:html)?\s*(<!DOCTYPE html[\s\S]*?</html>)\s*```', raw_output, re.IGNORECASE)
        if html_match:
            content = html_match.group(1).strip()
            # Extract title if present in <title> tag
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "Generated Growth Framework"
            return title, "html", content

        if "<!DOCTYPE html" in raw_output and "</html>" in raw_output:
            start = raw_output.find("<!DOCTYPE html")
            end = raw_output.find("</html>") + 7
            content = raw_output[start:end]
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "Generated Growth Framework"
            return title, "html", content

        # Otherwise Markdown
        title = "Growth Framework & Playbook"
        # Find first # Heading for title
        heading_match = re.search(r'^#\s+(.+)$', raw_output, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()

        # Clean markdown code fences if wrapped
        clean_content = raw_output
        fence_match = re.match(r'^```(?:markdown)?\s*([\s\S]*?)\s*```$', raw_output.strip())
        if fence_match:
            clean_content = fence_match.group(1).strip()

        return title, default_type if default_type != "html" else "markdown", clean_content

artifact_generator = ArtifactGeneratorSkill()
