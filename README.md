# Jobs Scraper API

FastAPI-based REST API for querying job listings from a SQLite database. Consumes data from the [jobs-scraper](https://github.com/virgotagle/jobs-scraper) project.

## Stack

- **FastAPI** 0.122.0+ • **SQLAlchemy** 2.0.44+ • **Pydantic** 2.12.5+ • **Python** 3.12+
- **Database**: SQLite (default) • PostgreSQL/MySQL supported
- **Auth**: Optional API key authentication (bcrypt hashed)
- **Testing**: pytest 8.3.4+

## Quick Start

```bash
# Clone and install
git clone <repository-url> && cd jobs-scraper-api
uv sync

# Configure (optional)
cp .env.example .env

# Run
fastapi dev main.py
```

API: `http://localhost:8000` • Docs: `http://localhost:8000/docs`

## Database Schema

**`job_listings`** (main table): `job_id` (PK) • `title` • `job_details_url` • `job_summary` • `company_name` • `location` • `country_code` • `listing_date` • `salary_label` • `work_type` • `job_classification` • `job_sub_classification` • `work_arrangements`

**`job_details`** (1:1 relationship): `job_id` (PK, FK) • `status` • `is_expired` • `details` • `is_verified` • `expires_at`

**`api_keys`** (authentication): `id` • `key_hash` • `key_prefix` • `name` • `email` • `company` • `is_active` • `created_at` • `last_used_at` • `expires_at` • `rate_limit` • `request_count`

## API Endpoints

| Endpoint | Method | Description | Key Params |
|----------|--------|-------------|------------|
| `/` | GET | Root endpoint | - |
| `/jobs/` | GET | List jobs with filters | `job_classification`, `job_sub_classification`, `work_arrangements`, `skip=0`, `limit=100` |
| `/jobs/{job_id}` | GET | Get job with details | - |
| `/jobs/search` | GET | Search jobs | `keyword` (min 2 chars, required), `skip=0`, `limit=100` |
| `/jobs/classifications` | GET | List all classifications | - |
| `/jobs/sub-classifications` | GET | List all sub-classifications | - |
| `/jobs/work-arrangements` | GET | List all work arrangements | - |

**Validation**: `skip` ≥ 0 • `limit` 1-1000 • `keyword` min 2 chars

**HTTP Status**: 200 OK • 400 Bad Request • 401 Unauthorized • 404 Not Found • 422 Validation Error • 500 Server Error

## Configuration

Environment variables (`.env` file, see `.env.example`):

```bash
DATABASE_URL=sqlite:///jobs.db                    # or postgresql:// or mysql://
REQUIRE_API_KEY=false                             # Enable API key auth
CORS_ORIGINS=["*"]                                # ["https://myapp.com"] in prod
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

## Data Source

Requires `jobs.db` from [jobs-scraper](https://github.com/virgotagle/jobs-scraper):

```bash
git clone https://github.com/virgotagle/jobs-scraper
cd jobs-scraper && uv sync && uv run playwright install
uv run python -m src.app --site seek --by-category
cp database/jobs.db /path/to/jobs-scraper-api/
```

## Testing

```bash
pytest                                            # All tests
pytest tests/test_api.py                         # API integration tests
pytest --cov=src --cov-report=html               # Coverage report
```

Note: `test_api.py` requires `jobs.db` to exist.

## Authentication (Optional)

API key authentication is **disabled by default**. Enable with `REQUIRE_API_KEY=true`.

**Generate keys:**
```bash
uv run python -m src.admin.create_key --name "Client" --email "dev@company.com" --rate-limit 5000
```

**Use keys:**
```bash
curl -H "X-API-Key: sk_live_YOUR_KEY" http://localhost:8000/jobs/
```

**Manage keys:**
```bash
uv run python -m src.admin.list_keys              # List active keys
uv run python -m src.admin.list_keys --all        # List all keys
uv run python -m src.admin.revoke_key --id 1      # Revoke key
```

**Security**: Bcrypt-hashed • 256-bit entropy • Rate limiting (default: 1000/hour) • Never commit keys

## Deployment

**Production checklist:**
- Set `REQUIRE_API_KEY=true` and generate client keys
- Use PostgreSQL/MySQL: `DATABASE_URL=postgresql://user:pass@host/db`
- Set specific CORS origins: `CORS_ORIGINS=["https://myapp.com"]`
- Enable HTTPS (reverse proxy or platform SSL)
- Configure logging/monitoring
- Consider Alembic for DB migrations

**Performance**: Add indexes on frequently queried fields • Cache classifications endpoints • Use connection pooling for multi-worker deployments



