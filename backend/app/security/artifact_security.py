import re
from typing import Tuple

class ArtifactSecurity:
    """
    Security sanitizer and validator for untrusted LLM-generated HTML and Markdown artifacts.

    SECURITY MODEL:
    - ALLOWED:
      - Clean semantic HTML structure: <div>, <span>, <h1>-<h6>, <p>, <ul>, <ol>, <li>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <hr>, <strong>, <em>, <code>, <pre>.
      - Inline CSS in <style> blocks (for styling modern SaaS cards, grids, flexboxes).
      - SVG icons with safe attributes.

    - BLOCKED:
      - <script> tags (execution of arbitrary JavaScript).
      - <iframe>, <object>, <embed>, <applet> tags (nesting untrusted external contexts).
      - Inline event handlers: onclick, onload, onerror, onmouseover, onfocus, etc.
      - Pseudo-protocols: javascript:, data:text/html, vbscript:.
      - <form> submissions to external endpoints.
      - <meta http-equiv="refresh"> redirects.
      - <link rel="stylesheet"> pointing to remote unverified stylesheets.
    """

    DANGEROUS_TAGS_PATTERN = re.compile(
        r'<\s*(?:script|iframe|object|embed|applet|meta|base|link)\b[^>]*>[\s\S]*?<\s*/\s*(?:script|iframe|object|embed|applet|meta|base|link)\s*>|<\s*(?:script|iframe|object|embed|applet|meta|base|link)\b[^>]*>',
        re.IGNORECASE
    )

    EVENT_HANDLER_PATTERN = re.compile(
        r'\s*on[a-zA-Z]+\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+)',
        re.IGNORECASE
    )

    JAVASCRIPT_URI_PATTERN = re.compile(
        r'(?:href|src|action)\s*=\s*[\'"]?\s*(?:javascript:|data:text/html|vbscript:)[^\'"]*',
        re.IGNORECASE
    )

    FORM_ACTION_PATTERN = re.compile(
        r'<\s*form\b[^>]*>',
        re.IGNORECASE
    )

    @classmethod
    def sanitize_html(cls, html_content: str) -> Tuple[str, bool]:
        """
        Sanitizes raw HTML string, stripping dangerous tags, attributes, and handlers.
        Returns (sanitized_html, was_modified).
        """
        original = html_content

        # 1. Strip dangerous tags
        sanitized = cls.DANGEROUS_TAGS_PATTERN.sub('', original)

        # 2. Strip event handlers (onload, onerror, etc.)
        sanitized = cls.EVENT_HANDLER_PATTERN.sub('', sanitized)

        # 3. Strip javascript: URIs
        sanitized = cls.JAVASCRIPT_URI_PATTERN.sub('', sanitized)

        # 4. Strip forms
        sanitized = cls.FORM_ACTION_PATTERN.sub('<div>', sanitized)
        sanitized = re.sub(r'<\s*/\s*form\s*>', '</div>', sanitized, flags=re.IGNORECASE)

        was_modified = sanitized != original
        return sanitized, was_modified

    @classmethod
    def get_sandbox_attributes(cls) -> str:
        """
        Returns strict HTML iframe sandbox attributes.
        Note: allow-same-origin is deliberately EXCLUDED so the iframe has an opaque origin
        with zero access to application cookies, localStorage, or parent window DOM.
        """
        return 'sandbox="allow-scripts" referrerpolicy="no-referrer"'

artifact_security = ArtifactSecurity()
