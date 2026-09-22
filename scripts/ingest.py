import sys
import os
import glob
import re

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import init_db, get_db_session
from app.models.db_models import TranscriptChunkModel
from app.rag.chunker import chunker
from app.rag.embeddings import embedding_generator
from app.observability.logging import logger

PRELOADED_EPISODES = [
    {
        "episode": "Brian Chesky on Founder Mode, Product Design, and Scaling Airbnb",
        "guest": "Brian Chesky",
        "topic": "Founder Mode and Product Excellence",
        "source_url": "https://www.lennyspodcast.com/brian-chesky",
        "content": """
Lenny (00:01): Welcome back to Lenny's Podcast. Today my guest is Brian Chesky, co-founder and CEO of Airbnb. Brian, you recently gave a talk at Y Combinator that broke the internet about 'Founder Mode'. What is Founder Mode?

Brian Chesky (00:30): For over twenty years, founders have been told a lie by professional managers and business schools: that once you get to a certain size, you are supposed to 'hire professional executives and get out of their way'. You are told to delegate, empower, manage through OKRs, and inspect outcomes from a distance. That advice is completely wrong for creative, product-led companies.

When Airbnb hit the pandemic and our revenue dropped 80% in eight weeks, we had to lay off 25% of our staff and rebuild the company from scratch. We fired the conventional divisional structure. We got rid of traditional product managers who acted as coordinators or mini-CEOs. Instead, we shifted into what I call Founder Mode.

In Founder Mode, the founder is deeply in the details. You don't manage through layers of abstraction. You run a centralized review cadence. I personally review every single feature, every single screen, every marketing campaign twice a year in our biannual releases. We unified our product roadmap into a single integrated system.

Lenny (03:15): How do you avoid micromanagement when you are so deep in the details?

Brian Chesky (03:45): People confuse micromanagement with excellence. Micromanagement is when you tell someone how to do a task they already know how to do, without vision. Being in the details means setting an uncompromising bar for product quality, taste, and craft. Steve Jobs was in the details. Walt Disney was in the details. You cannot delegate the soul of your product to people who don't have founder context.

If you want to build a truly defensible moat, your moat is not just your technology or your distribution network. Your moat is the velocity of your design craft and the obsessive standard you uphold. When customers feel that an application is crafted with genuine love, they become lifelong evangelists.
"""
    },
    {
        "episode": "Shreyas Doshi on High-Agency Product Management and the LNO Framework",
        "guest": "Shreyas Doshi",
        "topic": "The LNO Framework and Strategic Impact",
        "source_url": "https://www.lennyspodcast.com/shreyas-doshi",
        "content": """
Lenny (00:05): Today on the podcast, we have Shreyas Doshi, legendary product leader from Stripe, Twitter, Google, and Yahoo. Shreyas, you've introduced some of the most influential frameworks in modern tech. Let's talk about the LNO framework.

Shreyas Doshi (00:45): Most product managers suffer from chronic burnout because they treat all tasks with the same 10/10 level of effort. They obsess over formatting status updates with the same emotional energy they give to product strategy. That is a guaranteed recipe for mediocrity.

The LNO Framework categorizes work into three distinct buckets:
1. 'L' stands for Leverage tasks. These are tasks where an exceptional 10/10 execution yields a 10x or 100x return. Examples include defining your product differentiation, drafting your core strategy memo, or designing your critical onboarding conversion funnel. On Leverage tasks, you must be relentless and do your absolute best work.

2. 'N' stands for Neutral tasks. These are operational necessities that need to be done well enough, but doing them at a 10/10 level creates zero marginal value. An 8/10 is completely fine. Examples include weekly team syncs, routine sprint planning, or standard compliance reviews.

3. 'O' stands for Overhead tasks. These are bureaucratic tasks that you must minimize, automate, or do at a 5/10 acceptable threshold. Filing expense reports, filling out lengthy internal surveys, or responding to low-priority emails.

Lenny (03:30): What separates a good product manager from a great, high-agency product manager?

Shreyas Doshi (04:00): Good product managers solve problems that are handed to them. High-agency product managers reshape reality. When told that a deadline is impossible or that an API cannot be built, a high-agency PM finds the creative third path. They don't accept artificial constraints. They understand that conviction comes from deep qualitative user observation combined with quantitative telemetry, not from consensus meetings.
"""
    },
    {
        "episode": "Elena Verna on B2B Product-Led Growth and Retention Funnels",
        "guest": "Elena Verna",
        "topic": "PLG Loops and Monetization Timing",
        "source_url": "https://www.lennyspodcast.com/elena-verna",
        "content": """
Lenny (00:10): Elena Verna is back! Elena is the Interim CMO at Amplitude, Head of Growth at Lovable, and advisor to companies like Miro, SurveyMonkey, and Dropbox. Elena, what is the biggest mistake SaaS companies make when transitioning to Product-Led Growth (PLG)?

Elena Verna (00:40): The number one mistake is thinking that PLG is a pricing model or just adding a 'Start Free Trial' button to your marketing site. PLG is an organizational go-to-market motion where the product itself drives acquisition, retention, and expansion.

Companies fail at PLG because they try to monetize before the user has experienced the 'Aha!' moment. If you ask for a credit card before delivering value, you are imposing friction at the exact moment when the user's intent is most fragile.

Your growth funnel must follow this strict sequence:
First: Deliver immediate, effortless time-to-value (TTV).
Second: Build an ongoing habit loop where users return organically.
Third: Trigger monetization only when the user encounters a natural paywall—such as team collaboration, usage thresholds, or advanced enterprise security features.

Lenny (02:45): How should product leaders think about growth loops versus traditional funnels?

Elena Verna (03:15): Funnels are linear: you pour money into paid ads, get a lead, and convert them once. The moment you stop spending, growth drops to zero. Growth loops are compounding engines: the output of one user creates the input for the next user.

In B2B, the most powerful loop is the Collaboration Loop. When a PM creates a board in Miro or a report in Amplitude, they invite their engineers and designers to view it. Those collaborators sign up for free, experience the value, and create their own boards, inviting more teammates. That is how you achieve sustainable negative churn and explosive net revenue retention.
"""
    },
    {
        "episode": "Gustaf Alströmer on Finding Product-Market Fit and Metrics that Matter",
        "guest": "Gustaf Alströmer",
        "topic": "Product-Market Fit Benchmarks and Retention Curves",
        "source_url": "https://www.lennyspodcast.com/gustaf-alstromer",
        "content": """
Lenny (00:08): Today my guest is Gustaf Alströmer, Group Partner at Y Combinator and former VP of Growth at Airbnb. Gustaf, having evaluated thousands of startups at YC, how do you define real Product-Market Fit?

Gustaf Alströmer (00:35): Product-Market Fit is not a feeling, and it is not a press release. Product-Market Fit is a flattening retention curve.

If you plot your user retention by cohort over 30, 60, and 90 days:
If your curve heads asymptotically toward zero, you do NOT have product-market fit. No amount of growth hacking, SEO, or paid ad spend will save a leaky bucket.
If your retention curve flattens out—say at 20%, 30%, or 40%—and stays horizontal for six months, you have found product-market fit for that core cohort. Now you can pour fuel on the fire.

Lenny (02:15): What are the benchmarks for healthy retention across different verticals?

Gustaf Alströmer (02:40): Here are the benchmarks we look for at Y Combinator:
For Consumer Social: You need at least 25% Day-30 retention.
For Consumer Transactional (like Airbnb or Uber): You look for 30% annual repeat purchase rate.
For B2B SaaS: You need 40% to 50% month-12 logo retention, and over 110% Net Dollar Retention (NDR).
For Prosumer / Freemium tools (like Figma or Notion): You want 30% to 35% user retention after 6 months.

If your numbers are below these thresholds, stop hiring a sales team. Stop scaling performance marketing. Talk to the users who churned, find the 10% of users who love your product intensely, and double down exclusively on solving their hair-on-fire problem.
"""
    }
]

def ingest_all():
    logger.info("Initializing database for transcript ingestion...")
    db = get_db_session()

    total_chunks_added = 0

    # 1. Ingest preloaded flagship episodes
    for ep in PRELOADED_EPISODES:
        logger.info(f"Ingesting preloaded episode: {ep['episode']} ({ep['guest']})")
        chunks = chunker.chunk_transcript(
            transcript_text=ep["content"],
            episode_title=ep["episode"],
            guest_name=ep["guest"],
            source_url=ep["source_url"]
        )

        for c in chunks:
            # Generate normalized dense vector embedding
            embedding = embedding_generator.generate_embedding_sync(c["content"])

            # Check if chunk already exists
            existing = db.query(TranscriptChunkModel).filter(TranscriptChunkModel.id == c["id"]).first()
            if not existing:
                model = TranscriptChunkModel(
                    id=c["id"],
                    episode=c["episode"],
                    guest=c["guest"],
                    topic=c["topic"],
                    content=c["content"],
                    embedding=embedding,
                    source_url=c["source_url"]
                )
                db.add(model)
                total_chunks_added += 1

    db.commit()
    logger.info(f"Successfully ingested {total_chunks_added} chunks into knowledge base.")
    db.close()

if __name__ == "__main__":
    ingest_all()
