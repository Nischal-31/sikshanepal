# Siksha Nepal

A centralized e-learning platform built with Django, containerized with Docker, and deployed to AWS EC2 via an automated CI/CD pipeline.

## Tech Stack for SikshaNepal

- **Backend:** Django + Django REST Framework
- **Database:** PostgreSQL (Docker container)
- **App server:** Django dev server (`manage.py runserver`)
- **Reverse proxy:** Nginx
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Image registry:** Docker Hub
- **Hosting:** AWS EC2

## Architecture

```
GitHub push (main)
      │
      ▼
GitHub Actions
   ├─ build Docker image
   ├─ push image → Docker Hub
   └─ SSH into EC2 → pull image → restart containers
      │
      ▼
EC2 instance
   ├─ Nginx        (reverse proxy, port 80)
   ├─ Django (runserver, app container)
   └─ PostgreSQL   (db container, persistent volume)
```

Django, Postgres, and Nginx all run as containers on a single EC2 instance via Docker Compose. Postgres data persists in a named Docker volume, independent of container restarts.

## Local Development

```bash
git clone <repo-url>
cd sikshanepal
cp .env.example .env   # fill in real values
docker compose up --build
```

App will be available at `http://localhost` (via Nginx) or `http://localhost:8000` (Django directly, if exposed).

## Environment Variables

See `.env.example` for the full list. Required:

| Variable | Description |
|---|---|
| `DEBUG` | `False` in production |
| `SECRET_KEY` | Django secret key |
| `ALLOWED_HOSTS` | EC2 public IP / domain, comma-separated |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | Postgres credentials |
| `DB_HOST` | `db` (the Compose service name — not `localhost`) |
| `DB_PORT` | `5432` |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP credentials for outgoing email (Gmail app password) |

`.env` is never committed — it's created manually on the server and locally.

## Deployment

Deployment is fully automated via GitHub Actions on every push to `master`:

1. Runs the build and pushes a new image to Docker Hub, tagged `latest` and with the commit SHA.
2. SSHs into the EC2 instance and runs `docker compose pull && docker compose up -d` to roll out the new image.

### One-time EC2 setup

```bash
# On the EC2 instance
mkdir ~/sikshanepal && cd ~/sikshanepal
# copy docker-compose.yml and nginx/nginx.conf here
# create .env manually with production values
docker compose up -d
```

### Required GitHub Secrets

| Secret | Purpose |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub login |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `EC2_HOST` | EC2 public IP |
| `EC2_USER` | SSH user (`ubuntu`) |
| `EC2_SSH_KEY` | Private key for SSH access |

## Project Structure

```
sikshanepal/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── nginx/
│   └── nginx.conf
├── .github/
│   └── workflows/
│       └── deploy.yml
├── sikshanepal/          # Django project package (settings, wsgi, urls)
├── manage.py
├── requirements.txt
├── analytics/
├── backend/
├── blog/
├── contactenquiry/
├── courses/
├── dashboard/
├── quiz/
├── subscription/
├── user/
├── media/                # runtime uploads, mounted as a Docker volume
├── static/ / staticfiles/
└── templates/
```

## Notes

- Static and media files are served by Nginx via shared Docker volumes.
- Postgres runs as a container on the same EC2 instance rather than a managed service (e.g. RDS) — a deliberate choice for this project's scope.
- Only the `web` (Django) image is rebuilt and redeployed on push; `docker-compose.yml` and `nginx.conf` on the server are updated manually when changed.
- The app was originally developed against SQLite (`db.sqlite3`); production `settings.py` must read database credentials from environment variables so it connects to the Postgres container instead.
- Firebase credentials (`sikshanepal/firebase.py` / `config/firebase`) are treated as secrets — not committed to git, provided via environment variables or mounted at runtime instead.
- `env/` (local virtualenv) and `db.sqlite3` are excluded from the Docker build via `.dockerignore`.
