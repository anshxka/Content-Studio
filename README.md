# ✍️ GenZMarketer Content Studio

Every morning (about 7:00 AM IST) this tool reads fresh marketing, AI, career and job-search news and creates:

1. **10 non-generic LinkedIn topic ideas**: a mix of Marketing, AI, Resume & CV, Career guidance, Job search and Personal branding. Each has an under-discussed angle, why it's timely, and two hook options.
2. **3 ready-to-post LinkedIn drafts** in the framework **Hook → Story → Problem → Solution → CTA**, with a Copy button.
3. **The GenZ Marketer Weekly** newsletter every Sunday, for people new to marketing. It follows a 45-week lesson plan across core, brand, digital, performance, programmatic, growth, analytics, AI, personal branding and career.

## Files
| File | What it does |
|---|---|
| `settings.py` | **Your settings:** about you, pillars, post framework, news sources, newsletter name, day and lesson plan |
| `studio.py` | The engine (no need to edit) |
| `requirements.txt` | Libraries it needs |
| `.github/workflows/studio.yml` | Daily schedule |

## Setup
1. **Gemini key:** at aistudio.google.com, go to API keys, then Create API key, then **Create project** "Content Studio". Copy the key.
2. **Repo:** create a new **Public** GitHub repo named `content-studio`, with "Add a README" ticked.
3. **Upload:** add `studio.py`, `settings.py`, `requirements.txt` and `README.md`, then commit.
4. **Workflow:** click Add file, then Create new file, and name it `.github/workflows/studio.yml`. Paste in the file's contents and commit.
5. **Secret:** go to Settings, Secrets and variables, Actions, New repository secret. Use the name `GEMINI_API_KEY`.
6. **Run:** go to Actions, Content Studio, Run workflow (about 2–3 minutes).
7. **Pages:** go to Settings, then Pages. Choose Deploy from a branch, `main`, `/docs`, and save.
   Your link: `https://<username>.github.io/content-studio/`

## Tips
- **Get a newsletter now:** under Settings, Secrets and variables, Actions, open the Variables tab and add `NEWSLETTER_NOW` = `yes`. Run once, then delete the variable.
- **Change the post style:** edit `FRAMEWORK` in `settings.py`.
- **Change the lesson order:** edit `CURRICULUM` in `settings.py`.
- Drafts never invent your experiences. Fill in anything in [square brackets] with your real story before posting.
