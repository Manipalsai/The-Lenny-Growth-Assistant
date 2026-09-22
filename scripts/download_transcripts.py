import os
import subprocess
from app.observability.logging import logger

TRANSCRIPTS_REPO = "https://github.com/ChatPRD/lennys-podcast-transcripts.git"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "transcripts_raw")

def download_transcripts():
    os.makedirs(TARGET_DIR, exist_ok=True)
    if os.path.exists(os.path.join(TARGET_DIR, ".git")):
        logger.info(f"Transcripts repository already exists in {TARGET_DIR}. Pulling latest...")
        subprocess.run(["git", "-C", TARGET_DIR, "pull"], check=False)
    else:
        logger.info(f"Cloning transcripts from {TRANSCRIPTS_REPO} into {TARGET_DIR}...")
        subprocess.run(["git", "clone", "--depth", "1", TRANSCRIPTS_REPO, TARGET_DIR], check=True)
    logger.info("Transcripts download complete.")

if __name__ == "__main__":
    download_transcripts()
