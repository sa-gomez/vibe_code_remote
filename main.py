import json
import os
from pathlib import Path

import anthropic
import numpy as np
from dotenv import load_dotenv
from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer
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

_embed_model = SentenceTransformer("all-MiniLM-L6-v2")
_bow_chunks = [p.strip() for p in body_of_work_text.split("\n\n") if p.strip()]
_bow_embeddings = _embed_model.encode(_bow_chunks, convert_to_numpy=True)

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


def evaluate_match_embeddings(job_description: str) -> dict:
    jd_embedding = _embed_model.encode([job_description], convert_to_numpy=True)

    # Similarity of each body-of-work chunk against the JD
    chunk_scores = cosine_similarity(jd_embedding, _bow_embeddings)[0]
    top_k_idx = np.argsort(chunk_scores)[::-1][:5]
    top_scores = chunk_scores[top_k_idx]
    avg_score = float(top_scores.mean())

    # Matching areas: first sentence (or up to 80 chars) of top chunks
    matching_areas = []
    for idx in top_k_idx:
        chunk = _bow_chunks[idx]
        first_line = chunk.split("\n")[0].strip()
        matching_areas.append(first_line[:90] if len(first_line) > 90 else first_line)

    # Gaps: JD sentences with lowest max similarity to any chunk
    jd_sentences = [s.strip() for s in job_description.replace("\n", " ").split(".") if len(s.strip()) > 20]
    if jd_sentences:
        jd_sent_embeddings = _embed_model.encode(jd_sentences, convert_to_numpy=True)
        sent_scores = cosine_similarity(jd_sent_embeddings, _bow_embeddings).max(axis=1)
        gap_idx = np.argsort(sent_scores)[:6]
        gaps = [jd_sentences[i][:90] for i in gap_idx if sent_scores[i] < 0.4]
    else:
        gaps = []

    if avg_score > 0.45:
        match_level = "Strong Match"
    elif avg_score > 0.30:
        match_level = "Partial Match"
    else:
        match_level = "Not a Match"

    summary = (
        f"Semantic similarity analysis (avg score: {avg_score:.2f}) found strong overlap between "
        f"the job description and {len(matching_areas)} sections of Aaron's background. "
        "This method understands synonyms and paraphrasing — 'distributed systems' matches 'microservices'."
    )

    return {
        "match_level": match_level,
        "matching_areas": matching_areas,
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
                elif method == "embeddings":
                    result = evaluate_match_embeddings(job_description)
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
