"""
Curated list of verified live Beebom URLs used for parametrized SEO tests.

All URLs have been crawled from the live site and confirmed to return
HTTP 200 as of April 2026. The list covers the homepage, category pages,
tag pages, puzzle pages, how-to articles, reviews, news articles,
listicles, and static pages for maximum coverage.
"""

# ---------------------------------------------------------------------------
# Homepage
# ---------------------------------------------------------------------------
HOMEPAGE = "https://beebom.com/"

# ---------------------------------------------------------------------------
# Category pages (archive / listing pages)
# ---------------------------------------------------------------------------
CATEGORY_URLS = [
    "https://beebom.com/category/games/",
    "https://beebom.com/category/news/",
    "https://beebom.com/category/reviews/",
    "https://beebom.com/category/tech/",
]

# ---------------------------------------------------------------------------
# Tag pages
# ---------------------------------------------------------------------------
TAG_URLS = [
    "https://beebom.com/tag/opinion/",
    "https://beebom.com/tag/genshin-impact/",
    "https://beebom.com/tag/honkai-star-rail/",
    "https://beebom.com/tag/ai/",
    "https://beebom.com/tag/fortnite/",
    "https://beebom.com/tag/pokemon/",
]

# ---------------------------------------------------------------------------
# Article pages — diverse content types, all verified HTTP 200
# ---------------------------------------------------------------------------

# Reviews (game / product reviews)
REVIEW_URLS = [
    "https://beebom.com/doom-the-dark-ages-review/",
    "https://beebom.com/elden-ring-nightreign-review/",
    "https://beebom.com/nothing-phone-3-review/",
    "https://beebom.com/arc-raiders-review/",
    "https://beebom.com/ghost-of-yotei-review/",
    "https://beebom.com/borderlands-4-review/",
    "https://beebom.com/hp-omen-max-16-2025-review/",
    "https://beebom.com/metal-gear-solid-delta-snake-eater-review/",
]

# How-to / tutorial articles
HOWTO_URLS = [
    "https://beebom.com/how-to-extract-in-arc-raiders/",
    "https://beebom.com/how-to-create-an-ai-agent/",
    "https://beebom.com/how-to-change-your-gmail-address/",
    "https://beebom.com/how-to-make-money-with-ai/",
    "https://beebom.com/how-to-get-toy-story-skins-in-fortnite/",
    "https://beebom.com/how-to-kill-bastion-in-arc-raiders/",
    "https://beebom.com/how-find-appdata-folder-windows-11-10/",
]

# Listicle / "best of" articles
LISTICLE_URLS = [
    "https://beebom.com/best-iphone-16-pro-max-cases/",
    "https://beebom.com/best-wireless-earbuds/",
    "https://beebom.com/best-vpn-services/",
    "https://beebom.com/best-chatgpt-alternatives/",
    "https://beebom.com/best-ai-model/",
    "https://beebom.com/best-ai-tools-for-students/",
    "https://beebom.com/best-ai-assistant/",
    "https://beebom.com/best-ai-detector/",
]

# News articles
NEWS_URLS = [
    "https://beebom.com/gta-6-wants-to-be-the-next-roblox-and-fortnite-hints-new-rockstar-hirings/",
    "https://beebom.com/fortnite-reload-elite-stronghold-update-announced-brings-new-map-and-weapons/",
    "https://beebom.com/disney-eyes-major-buyout-deal-for-fortnite-creator-epic-games/",
    "https://beebom.com/ps5-and-ps5-pro-are-getting-another-price-hike-globally/",
    "https://beebom.com/popular-anime-piracy-site-hianime-officially-shutdown/",
    "https://beebom.com/gta-6-pc-release-wont-take-years-former-rockstar-dev-leaks-launch-window/",
    "https://beebom.com/netflix-one-piece-season-3-title-and-release-window-confirmed/",
]

# Codes / gaming guides
CODES_URLS = [
    "https://beebom.com/basketball-rivals-codes/",
    "https://beebom.com/blue-lock-rivals-codes/",
    "https://beebom.com/sailor-piece-codes/",
    "https://beebom.com/pokemon-champions-mystery-gift-codes/",
    "https://beebom.com/haikyuu-legends-codes/",
    "https://beebom.com/fortnite-brainrot-tower-defense-codes/",
]

# Explainer / "what is" articles
EXPLAINER_URLS = [
    "https://beebom.com/ai-vs-machine-learning/",
    "https://beebom.com/deepseek-vs-chatgpt/",
    "https://beebom.com/deep-learning-vs-machine-learning/",
    "https://beebom.com/snapchat-planets-meaning-order-explained/",
    "https://beebom.com/what-is-chatgpt-health/",
    "https://beebom.com/artificial-intelligence-hallucinations/",
]

# Puzzle / interactive pages
PUZZLE_URLS = [
    "https://beebom.com/puzzle/wordle-today-hint-answer/",
]

# All article URLs combined
ARTICLE_URLS = (
    REVIEW_URLS
    + HOWTO_URLS
    + LISTICLE_URLS
    + NEWS_URLS
    + CODES_URLS
    + EXPLAINER_URLS
    + PUZZLE_URLS
)

# ---------------------------------------------------------------------------
# Combined lists for parametrized tests
# ---------------------------------------------------------------------------

# Full list — used by most parametrized tests (21 categories/tags + 43 articles = 65 total)
ALL_URLS = [HOMEPAGE] + CATEGORY_URLS + TAG_URLS + ARTICLE_URLS

# Smoke subset — one of each page type for fast checks (links, perf, mobile)
SMOKE_URLS = [
    HOMEPAGE,
    "https://beebom.com/category/games/",
    "https://beebom.com/tag/ai/",
    "https://beebom.com/doom-the-dark-ages-review/",
    "https://beebom.com/best-wireless-earbuds/",
    "https://beebom.com/how-to-create-an-ai-agent/",
    "https://beebom.com/gta-6-wants-to-be-the-next-roblox-and-fortnite-hints-new-rockstar-hirings/",
    "https://beebom.com/basketball-rivals-codes/",
    "https://beebom.com/ai-vs-machine-learning/",
]
