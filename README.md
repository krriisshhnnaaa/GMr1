# Mail Automation v0.0

An event-driven Gmail prototype: Gmail sends a mailbox-change notification to Google Pub/Sub; the backend retrieves changed messages, normalizes them, applies deterministic rules or a classifier, persists metadata, and forwards important/urgent mail.

## Local start

1. Copy `.env.example` to `.env` and fill the configuration values.
2. Start PostgreSQL and the application with `docker compose up --build`.
3. Open `http://localhost:5173`. The prototype dashboard uses `demo@example.com` as its temporary development identity.

For backend-only development, install `backend/requirements.txt` and run `uvicorn app.main:app --reload` from `backend/`. The default SQLite URL makes the health endpoint usable without PostgreSQL; set `DATABASE_URL` to PostgreSQL for normal development.

## Google Cloud setup

1. Create a Google Cloud project, enable Gmail API and Pub/Sub API, and configure the OAuth consent screen.
2. Create a Web application OAuth client. Add `GOOGLE_REDIRECT_URI` (by default `http://localhost:8000/api/auth/google/callback`) as an authorized redirect URI, then set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
3. Create a Pub/Sub topic and subscription. Grant Gmail permission to publish to the topic and configure an authenticated push subscription pointing to `/api/events/gmail-pubsub`.
4. Implement mailbox `watch` registration after OAuth account association and renew it before Gmail's watch expiry. The push notification contains only `emailAddress` and `historyId`; use Gmail `history.list` and `messages.get` to retrieve messages.
5. Set a durable random Fernet `ENCRYPTION_KEY` and a random `APP_SECRET`. OAuth access and refresh tokens must be encrypted before storage; never send them to the browser.

## API

`GET /api/health` is public. User data endpoints require an application identity; during v0.0 this is represented by `X-User-Email` strictly as a development boundary. Replace it with a signed application session before deployment. Google OAuth routes are `/api/auth/google` and `/api/auth/google/callback`.

The current classifier is a local heuristic so the pipeline can be exercised without an AI key. Its `EmailClassifier` interface is intentionally replaceable with an LLM implementation configured using `AI_PROVIDER`, `AI_API_KEY`, and `AI_MODEL`.

## Testing

From `backend/`, run `pytest`. The test verifies normalized email processing, urgent classification, and duplicate-message idempotency.
