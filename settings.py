"""GenZMarketer Content Studio - your settings. This is the only file you normally edit."""
from urllib.parse import quote_plus


def gnews(q):      # Google News search, India edition
    return f"https://news.google.com/rss/search?q={quote_plus(q)}+when:2d&hl=en-IN&gl=IN&ceid=IN:en"


def gnews_us(q):   # Google News search, US / global edition
    return f"https://news.google.com/rss/search?q={quote_plus(q)}+when:2d&hl=en-US&gl=US&ceid=US:en"


# ---------------- About you ----------------
AUTHOR = "Anshika Sharma"
BRAND = "GenZMarketer"
INSTAGRAM = "https://www.instagram.com/genzmarketer_/"
LINKEDIN = "https://www.linkedin.com/in/anshxka02/"
ABOUT_ME = ("Performance and programmatic marketer in India (~3 years) working across Meta, Google Ads, DV360, CM360, "
            "The Trade Desk, Amazon DSP, AppsFlyer, CleverTap, Looker Studio and SQL. Runs GenZMarketer on "
            "Instagram and LinkedIn to guide people who are new to marketing.")

# ---------------- LinkedIn content ----------------
PILLARS = ["Marketing", "AI", "Resume & CV", "Career guidance", "Job search", "Personal branding"]
IDEAS_PER_DAY = 10       # topic ideas each day
POSTS_PER_DAY = 3        # full LinkedIn posts written each day

# Your post framework (the AI follows this exactly)
FRAMEWORK = """Every post MUST follow this framework, in this order:
1. HOOK / TRIGGER - 1-2 short lines that stop the scroll. Highly engaging: unexpected, bold, curious, a little
   provocative, or even seemingly unrelated to the topic - but it must make people stop and read.
   Never start with "In today's world", "Let's talk about", "Here's why", or an emoji.
2. STORY - tell it as a short, relatable story or scene (3-6 short lines) that pulls the reader in and leads to the topic.
3. PROBLEM - name the real problem plainly, and the mistake most people make.
4. SOLUTION - specific, practical steps or a clear reframe. Real substance, not fluff.
5. CTA - end with one clear call to action: a question to comment on, "save this", or follow GenZMarketer.
LinkedIn style: very short paragraphs (1-2 lines) with white space, 180-300 words, plain text,
max 2 emojis in the whole post, 3 relevant hashtags at the very end."""

# ---------------- News sources the ideas are based on ----------------
FEEDS = [
    # Marketing & advertising
    ("ET BrandEquity", "https://brandequity.economictimes.indiatimes.com/rss/topstories"),
    ("afaqs", gnews("site:afaqs.com")),
    ("exchange4media", gnews("site:exchange4media.com")),
    ("Social Samosa", gnews("site:socialsamosa.com")),
    ("Marketing Dive", "https://www.marketingdive.com/feeds/news/"),
    ("Digiday", "https://digiday.com/feed/"),
    ("Ad platforms", gnews_us('Meta ads OR "Google Ads" OR "Performance Max" OR "Advantage+" advertisers')),
    ("Programmatic", gnews_us('programmatic OR "The Trade Desk" OR DV360 OR "ad tech"')),
    ("Brand campaigns India", gnews('"ad campaign" OR rebrand OR "brand ambassador" India')),
    ("Creators & social", gnews('influencer OR "creator economy" OR Instagram India')),
    ("Growth & D2C", gnews('D2C OR "quick commerce" OR startup growth India')),
    # AI
    ("AI news", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("AI in marketing", gnews_us('"generative AI" marketing OR advertising OR creative')),
    ("AI & jobs", gnews_us('AI jobs OR "AI skills" OR "entry-level" workers')),
    # Careers, resumes, job search
    ("Hiring & layoffs India", gnews('hiring OR layoffs OR "job market" India')),
    ("Freshers & campus", gnews('freshers OR "campus hiring" OR internships India')),
    ("Resumes & ATS", gnews_us('resume OR "applicant tracking" OR recruiters AI')),
    ("LinkedIn platform", gnews_us('LinkedIn algorithm OR LinkedIn feature OR "LinkedIn" creators')),
    ("Recruiting trends", gnews_us('hiring managers OR recruiters OR interview trend')),
    ("Global jobs & visas", gnews_us('"visa sponsorship" OR H-1B OR "remote jobs"')),
    ("Salaries & appraisals", gnews('salary hike OR appraisal OR pay employees India')),
]
PER_FEED = 6

# ---------------- Weekly newsletter ----------------
NEWSLETTER_NAME = "The GenZ Marketer Weekly"
NEWSLETTER_DAY = 6                 # 0 = Monday ... 6 = Sunday
NEWSLETTER_START = "2026-10-05"    # the Monday of lesson week 1

# One lesson per week, in order, for people new to marketing. Edit, reorder or add freely.
CURRICULUM = [
    ("Core marketing", "What marketing actually is: needs, value and exchange (beyond 'running ads')"),
    ("Core marketing", "STP: segmentation, targeting and positioning with Indian brand examples"),
    ("Core marketing", "The 4Ps and why modern marketers still use them"),
    ("Core marketing", "Consumer behaviour: how people really decide what to buy"),
    ("Core marketing", "The marketing funnel vs the messy middle"),
    ("Brand marketing", "Brand positioning: owning one idea in the customer's mind"),
    ("Brand marketing", "Brand identity, voice and consistency"),
    ("Brand marketing", "Brand vs performance: why you need both"),
    ("Brand marketing", "How big Indian campaigns are planned: from brief to launch"),
    ("Digital marketing", "SEO basics: how Google decides who ranks"),
    ("Digital marketing", "Content marketing people actually read"),
    ("Digital marketing", "Organic social media strategy for brands"),
    ("Digital marketing", "Email and WhatsApp marketing: owned channels"),
    ("Digital marketing", "Influencer and creator marketing in India"),
    ("Performance marketing", "How Meta ads work: auction, audiences and creative"),
    ("Performance marketing", "Google Ads: Search, Performance Max, YouTube and Demand Gen"),
    ("Performance marketing", "Key metrics: CPM, CPC, CTR, CVR, CPA, ROAS and what they tell you"),
    ("Performance marketing", "Tracking: pixels, Conversions API, UTMs and why data breaks"),
    ("Performance marketing", "App marketing: installs, MMPs like AppsFlyer, and retention"),
    ("Performance marketing", "Budgeting and scaling campaigns without wasting money"),
    ("Programmatic", "What programmatic advertising is, in plain language"),
    ("Programmatic", "The ad-tech chain: advertisers, DSPs, ad exchanges, SSPs and publishers"),
    ("Programmatic", "Real-time bidding: what happens in 100 milliseconds"),
    ("Programmatic", "DV360, The Trade Desk and Amazon DSP compared"),
    ("Programmatic", "Ad servers and CM360: trafficking, tags and verification"),
    ("Programmatic", "Deals: open auction, PMPs and programmatic guaranteed"),
    ("Programmatic", "Brand safety, viewability and ad fraud"),
    ("Programmatic", "CTV and digital audio: the new programmatic frontier"),
    ("Growth marketing", "Growth marketing vs performance marketing"),
    ("Growth marketing", "The AARRR funnel: acquisition to referral"),
    ("Growth marketing", "Running experiments: A/B tests that actually mean something"),
    ("Growth marketing", "Retention and CRM: lifecycle journeys with tools like CleverTap"),
    ("Growth marketing", "Conversion rate optimisation for landing pages"),
    ("Analytics", "GA4 for marketers: events, conversions and reports"),
    ("Analytics", "Attribution: who gets credit for a sale?"),
    ("Analytics", "Looker Studio dashboards people actually use"),
    ("Analytics", "SQL for marketers: the 5 queries you will actually need"),
    ("AI in marketing", "AI tools for marketers: what's useful vs hype"),
    ("AI in marketing", "Prompting for marketing work: briefs, copy and research"),
    ("AI in marketing", "How AI is changing ad platforms (Advantage+, PMax and more)"),
    ("Personal branding", "Personal branding for marketers: your LinkedIn is your portfolio"),
    ("Personal branding", "Finding your niche and content pillars"),
    ("Career", "Marketing career paths: brand, performance, programmatic, growth, content"),
    ("Career", "Building a marketing resume with numbers that matter"),
    ("Career", "Cracking marketing interviews: case studies and test tasks"),
]
