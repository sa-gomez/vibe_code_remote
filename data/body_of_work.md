> PLACEHOLDER — Replace this entire file with your real background before using in production.

# Aaron Gomez — Full Background & Body of Work

## Summary
Software engineer with 7 years of experience, primarily in backend systems, distributed infrastructure, and developer tooling. Comfortable owning projects end-to-end: from system design through deployment and on-call. Have worked on teams ranging from 3-person startups to 200-person engineering orgs.

---

## Technical Skills

**Languages:** Python (primary, 7 years), Go (3 years), TypeScript/JavaScript (4 years), SQL (PostgreSQL, MySQL), Bash  
**Frameworks:** Flask, FastAPI, Django, React, Next.js  
**Infrastructure:** AWS (EC2, ECS, Lambda, S3, RDS, SQS, SNS, CloudWatch), GCP (Cloud Run, BigQuery), Docker, Kubernetes (EKS), Terraform, GitHub Actions, CircleCI  
**Data:** PostgreSQL, Redis, Kafka, Elasticsearch, dbt, Airflow  
**Practices:** REST API design, event-driven architecture, microservices, TDD, code review, incident response, technical writing  

---

## Work Experience

### Meridian Health Tech — Senior Software Engineer (2022 – present)
Healthcare data platform serving 40+ hospital systems. Team of 12 engineers.

- **Data pipeline ownership:** Designed and maintain a real-time event ingestion pipeline processing 8M+ events/day using Kafka, Python consumers, and PostgreSQL. Reduced end-to-end latency from 4 minutes to under 15 seconds by rewriting the consumer layer and adding parallel processing.
- **API platform:** Led the design of an internal REST API gateway used by 6 downstream product teams. Introduced OpenAPI spec-first development, cutting integration bugs by ~60%.
- **On-call & reliability:** Primary on-call for the data platform. Drove SLO adoption across the team, bringing P99 API latency from 2.1s to 380ms over 6 months.
- **Mentorship:** Onboarded and mentored 3 junior engineers. Ran weekly architecture review sessions.
- **Tech:** Python, Go, Kafka, PostgreSQL, AWS ECS, Terraform, GitHub Actions

### Pivot Labs — Software Engineer (2019 – 2022)
B2B SaaS startup (Series A, ~40 employees). Full-stack with a heavy backend focus.

- **Billing system:** Built the entire billing and subscription system from scratch using Stripe. Handled proration, trials, usage-based billing, and dunning. Zero billing-related incidents in 2 years post-launch.
- **Microservices migration:** Planned and led migration from a monolithic Django app to a service-oriented architecture. Decomposed 3 core domains (auth, billing, notifications) into independent services over 18 months without downtime.
- **Search:** Implemented full-text search using Elasticsearch, replacing a slow PostgreSQL ILIKE approach. Reduced search latency from 800ms to 40ms.
- **Frontend:** Shipped several customer-facing features in React including a real-time dashboard and a CSV data import flow.
- **Tech:** Python/Django, React, PostgreSQL, Elasticsearch, Stripe, AWS, Docker

### Freelance / Contract (2017 – 2019)
Built web applications and automation tools for small businesses and startups.

- Developed a custom CRM for a real estate agency (Django, PostgreSQL, deployed on Heroku)
- Built an automated invoice processing pipeline for an accounting firm using Python, PDF parsing, and email integration
- Various React/Node.js frontends for marketing sites and dashboards

---

## Personal Projects

### log-sheriff (open source, ~200 GitHub stars)
CLI tool for querying and filtering structured logs from multiple sources (CloudWatch, Datadog, local files) with a unified query syntax. Written in Go. Used by engineers at several companies per GitHub issues/PRs.

### pg-explain-viz
A web tool that takes PostgreSQL `EXPLAIN ANALYZE` output and renders it as an interactive tree diagram. Built with Python (FastAPI) and vanilla JS. Useful for debugging slow queries without reading the raw text output.

### homelab-k8s
Personal Kubernetes cluster running on old hardware at home. Hosts a handful of personal services (Nextcloud, Grafana, a home automation dashboard). Terraform + Helm for config management. Mostly a learning exercise that got out of hand.

---

## Education
B.S. Computer Science, California State University, 2017

---

## Working Style & Soft Skills
- Strong technical writer — comfortable writing RFCs, post-mortems, and ADRs
- Prefer async communication, document decisions thoroughly
- Experienced in Agile/Scrum (sprints, retros) and lighter-weight kanban processes
- Have led technical interviews and hiring panels
- Comfortable presenting to non-technical stakeholders
- Timezone: US Pacific
