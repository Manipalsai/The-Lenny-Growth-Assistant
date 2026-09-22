import pytest
from app.security.artifact_security import artifact_security

def test_strips_script_tags():
    malicious = "<p>Hello</p><script>alert('XSS')</script><div>World</div>"
    sanitized, modified = artifact_security.sanitize_html(malicious)
    assert "<script>" not in sanitized
    assert "alert('XSS')" not in sanitized
    assert modified is True
    assert "<p>Hello</p>" in sanitized
    assert "<div>World</div>" in sanitized

def test_strips_inline_event_handlers():
    malicious = '<img src="x" onerror="alert(document.cookie)" onload="hack()" />'
    sanitized, modified = artifact_security.sanitize_html(malicious)
    assert "onerror" not in sanitized
    assert "onload" not in sanitized
    assert modified is True

def test_strips_javascript_pseudo_protocols():
    malicious = '<a href="javascript:stealData()">Click Here</a>'
    sanitized, modified = artifact_security.sanitize_html(malicious)
    assert "javascript:" not in sanitized

def test_strips_iframes_and_objects():
    malicious = '<iframe src="https://evil.com"></iframe><object data="evil.swf"></object>'
    sanitized, modified = artifact_security.sanitize_html(malicious)
    assert "<iframe" not in sanitized
    assert "<object" not in sanitized

def test_sandbox_attributes():
    sandbox = artifact_security.get_sandbox_attributes()
    assert 'sandbox="allow-scripts"' in sandbox
    # Critical security check: allow-same-origin MUST NOT be present
    assert 'allow-same-origin' not in sandbox
