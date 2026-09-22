import pytest
from app.skills.router import router
from app.skills.grounded_qa import grounded_qa
from app.skills.ship30_writer import ship30_writer
from app.skills.artifact_generator import artifact_generator

def test_intent_router():
    assert router.classify_intent("Can you write a Ship 30 essay on product-market fit?") == "ship30_essay"
    assert router.classify_intent("Create an HTML dashboard showing growth levers") == "html_artifact"
    assert router.classify_intent("Generate a one-page growth framework") == "markdown_artifact"
    assert router.classify_intent("What did Brian Chesky say about founder mode?") == "grounded_qa"

def test_grounded_qa_prompt_construction():
    chunks = [{
        "episode": "Episode 1",
        "guest": "Brian Chesky",
        "topic": "Founder Mode",
        "passage": "Founder mode is about being in the details."
    }]
    prompts = grounded_qa.build_prompt("Explain founder mode", chunks)
    assert len(prompts) == 2
    assert prompts[0]["role"] == "system"
    assert "Brian Chesky" in prompts[1]["content"]
    assert "Episode 1" in prompts[1]["content"]

def test_ship30_writer_prompt_construction():
    chunks = [{
        "episode": "Episode 2",
        "guest": "Elena Verna",
        "topic": "PLG",
        "passage": "PLG is not a pricing model."
    }]
    prompts = ship30_writer.build_prompt("B2B Growth Loops", chunks)
    assert "SHIP 30 FOR 30 ESSAY BLUEPRINT" in prompts[0]["content"]
    assert "Elena Verna" in prompts[1]["content"]

def test_artifact_extraction():
    raw_markdown = "# Strategic Growth Framework\n\nHere is the framework..."
    title, art_type, clean = artifact_generator.extract_artifact(raw_markdown, "markdown")
    assert title == "Strategic Growth Framework"
    assert art_type == "markdown"

    raw_html = "```html\n<!DOCTYPE html><html><head><title>Growth Dashboard</title></head><body><h1>Content</h1></body></html>\n```"
    title, art_type, clean = artifact_generator.extract_artifact(raw_html, "html")
    assert title == "Growth Dashboard"
    assert art_type == "html"
    assert "<!DOCTYPE html>" in clean
