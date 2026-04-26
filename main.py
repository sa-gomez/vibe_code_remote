import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

app = Flask(__name__)

work = [
    {
        "company": "Acme Corp",
        "role": "Senior Software Engineer",
        "years": "2022 – present",
        "description": "Led backend development for a distributed data pipeline processing millions of events daily. Placeholder — replace with your real experience.",
    },
    {
        "company": "Startup Co",
        "role": "Software Engineer",
        "years": "2019 – 2022",
        "description": "Full-stack engineer on a B2B SaaS product. Built the billing system and led the migration to a microservices architecture. Placeholder.",
    },
]

projects = [
    {
        "name": "Project One",
        "description": "A personal project you built for fun or to scratch an itch. Placeholder — fill this in with something real.",
        "url": "https://github.com",
        "tech": ["Python", "PostgreSQL"],
    },
    {
        "name": "Project Two",
        "description": "Another side project. Maybe a tool, a CLI, a bot, or an experiment. Placeholder.",
        "url": "https://github.com",
        "tech": ["TypeScript", "React"],
    },
    {
        "name": "Project Three",
        "description": "Yet another thing you made. Could be open source, could be just for you. Placeholder.",
        "url": "https://github.com",
        "tech": ["Go"],
    },
]

BODY_OF_WORK = Path(__file__).parent / "data" / "body_of_work.md"
body_of_work_text = BODY_OF_WORK.read_text()

SYSTEM_PROMPT = f"""You are evaluating whether a software engineer is a good match for a job posting.

Here is their complete background and body of work:

{body_of_work_text}

When given a job description, respond with JSON only — no prose, no markdown fences. Use this exact shape:
{{
  "match_level": "Strong Match" | "Partial Match" | "Not a Match",
  "matching_areas": ["...", "..."],
  "gaps": ["...", "..."],
  "summary": "2-3 sentence plain-English assessment written directly to a recruiter"
}}"""


def evaluate_match(job_description: str) -> dict:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Job description:\n\n{job_description}",
            }
        ],
    )
    return json.loads(response.content[0].text)


def evaluate_match_tfidf(job_description: str) -> dict:
    vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
    matrix = vectorizer.fit_transform([body_of_work_text, job_description])
    score = float(cosine_similarity(matrix[0], matrix[1])[0][0])

    feature_names = vectorizer.get_feature_names_out()
    bow_weights = matrix[0].toarray()[0]
    jd_weights = matrix[1].toarray()[0]

    jd_terms = {feature_names[i] for i, w in enumerate(jd_weights) if w > 0}
    bow_terms = {feature_names[i] for i, w in enumerate(bow_weights) if w > 0}

    matched = sorted(jd_terms & bow_terms)[:12]
    gaps = sorted(jd_terms - bow_terms)[:12]

    if score > 0.15:
        match_level = "Strong Match"
    elif score > 0.06:
        match_level = "Partial Match"
    else:
        match_level = "Not a Match"

    summary = (
        f"Keyword analysis (cosine similarity: {score:.2f}) found {len(matched)} term(s) "
        f"from the job description in Aaron's background and {len(gaps)} that are absent. "
        "Note: this method is purely lexical — synonyms and paraphrasing are not detected."
    )

    return {
        "match_level": match_level,
        "matching_areas": matched,
        "gaps": gaps,
        "summary": summary,
    }


@app.route("/")
def index():
    return render_template("index.html", work=work, projects=projects)


@app.route("/match", methods=["GET", "POST"])
def match():
    result = None
    error = None
    job_description = ""
    method = "claude"

    if request.method == "POST":
        job_description = request.form.get("job_description", "").strip()
        method = request.form.get("method", "claude")
        if not job_description:
            error = "Please paste a job description."
        elif method == "claude" and not os.environ.get("ANTHROPIC_API_KEY"):
            error = "ANTHROPIC_API_KEY environment variable is not set."
        else:
            try:
                if method == "tfidf":
                    result = evaluate_match_tfidf(job_description)
                else:
                    result = evaluate_match(job_description)
            except Exception as e:
                error = f"Something went wrong: {e}"

    return render_template(
        "match.html",
        result=result,
        error=error,
        job_description=job_description,
        method=method,
    )


if __name__ == "__main__":
    app.run(debug=True)
