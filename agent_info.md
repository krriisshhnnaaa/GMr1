# Mail Automation — v0.0

## 1. Project Goal

Build a web application that allows users to connect one or more Gmail accounts and automatically identify important emails.

The system should:

1. Authenticate users with Google OAuth 2.0.
2. Allow users to connect Gmail accounts.
3. Receive notifications when new Gmail activity occurs.
4. Retrieve newly relevant emails through the Gmail API.
5. Normalize email data into an internal format.
6. Classify emails into categories using an AI model.
7. Forward emails classified as important or urgent to a user-configured destination email address.
8. Store processing metadata and classification results in a database.
9. Provide a minimal web dashboard showing connected accounts and processed email statistics.

This is a v0.0 prototype. Prioritize working end-to-end functionality and clean architecture over production-grade polish.

---

# 2. Core Architecture

Use an event-driven architecture.

```text
                    Google Gmail
                         │
                         │ Gmail API notification
                         ▼
                  Google Pub/Sub
                         │
                         ▼
                 Event Ingestion
                         │
                         ▼
                  Message Queue
                         │
                         ▼
                Email Processing
                         │
              ┌──────────┴──────────┐
              │                     │
        Rules Engine          AI Classifier
              │                     │
              └──────────┬──────────┘
                         ▼
                  Decision Engine
                    │         │
                  ignore    forward
                              │
                              ▼
                         Gmail API
                              │
                              ▼
                    Destination Email
```

Do not implement continuous Gmail polling as the primary architecture.

---

# 3. Recommended Technology Stack

Use:

* Backend: Python + FastAPI
* Database: PostgreSQL
* ORM: SQLAlchemy
* Authentication: Google OAuth 2.0
* Gmail integration: Gmail API
* Event system: Google Cloud Pub/Sub
* Queue: use Pub/Sub directly for v0.0 unless another queue is genuinely necessary
* AI classification: configurable LLM API
* Frontend: React
* API communication: REST
* Configuration: environment variables
* Deployment: Docker

Keep components modular so individual technologies can be replaced later.

---

# 4. Gmail Authentication

Implement Google OAuth 2.0.

Required functionality:

```text
/connect/google
/oauth/google/callback
```

After successful authentication:

1. Identify the application user.
2. Obtain Gmail authorization.
3. Obtain access and refresh tokens as required.
4. Encrypt sensitive credentials before storing them.
5. Associate the Gmail account with the application user.

Do not expose Gmail access tokens to the frontend.

Request the minimum Gmail scopes required for the prototype.

Design the authentication layer so additional Gmail accounts can be connected to the same application user.

---

# 5. Gmail Account Model

A user can have multiple connected Gmail accounts.

Example:

```text
User
 ├── Gmail Account A
 ├── Gmail Account B
 └── Gmail Account C
```

Each account must store:

```text
id
user_id
email_address
encrypted_access_token
encrypted_refresh_token
token_expiry
created_at
updated_at
active
```

Never store plaintext OAuth credentials.

---

# 6. Event-Driven Gmail Processing

Use Gmail's push notification mechanism through Google Cloud Pub/Sub.

Expected flow:

```text
Gmail mailbox changes
        ↓
Google Pub/Sub notification
        ↓
Backend webhook/subscriber
        ↓
Identify Gmail account
        ↓
Determine changed messages
        ↓
Create processing jobs
```

The Pub/Sub notification itself should not be treated as the email contents.

After receiving the notification, use the Gmail API to determine which messages changed and retrieve the required message data.

Implement processing so duplicate events do not result in duplicate forwarding.

---

# 7. Email Normalization

Do not expose Gmail-specific data structures to the rest of the application.

Create an internal normalized email object:

```python
class NormalizedEmail:
    message_id: str
    thread_id: str
    sender: str
    recipients: list[str]
    subject: str
    body_text: str
    body_html: str | None
    received_at: datetime
    labels: list[str]
    has_attachments: bool
```

Create a Gmail adapter responsible for converting Gmail API responses into this structure.

The classifier, rules engine, and forwarding system must operate on the normalized representation.

---

# 8. Email Processing Pipeline

Every newly detected email should follow this pipeline:

```text
Gmail event
    ↓
Retrieve message
    ↓
Normalize message
    ↓
Check duplicate/idempotency
    ↓
Apply user rules
    ↓
AI classification
    ↓
Decision
    ↓
Store result
    ↓
Forward if required
```

Each processing step should be independently testable.

---

# 9. Classification

For v0.0, classify emails into:

```text
SPAM
NEWSLETTER
NORMAL
IMPORTANT
URGENT
```

The AI classifier receives:

```text
sender
subject
body
relevant metadata
```

and returns structured JSON:

```json
{
  "category": "IMPORTANT",
  "confidence": 0.91,
  "reason": "The email concerns an active client project and requires a response."
}
```

The classifier must return one of the predefined categories.

Do not allow arbitrary category names.

Make the AI provider configurable through environment variables.

Create an abstraction such as:

```python
class EmailClassifier:
    def classify(email: NormalizedEmail) -> Classification:
        ...
```

This allows the AI implementation to be replaced later.

---

# 10. Rules Engine

Implement a basic rules layer before or alongside AI classification.

Examples:

```text
IF sender matches configured address
    → IMPORTANT

IF sender/domain is blocked
    → SPAM

IF sender/domain is configured as newsletter
    → NEWSLETTER
```

The rules engine should be separate from the AI classifier.

Architecture:

```text
Email
 ↓
Rules Engine
 ↓
Rule result or no result
 ↓
AI Classifier if necessary
 ↓
Final Classification
```

The AI should not unnecessarily process emails whose classification can be determined deterministically.

---

# 11. Forwarding

Each user configures a destination email address.

Example:

```text
destination_email:
important@example.com
```

Forward emails classified as:

```text
IMPORTANT
URGENT
```

Do not forward:

```text
SPAM
NEWSLETTER
NORMAL
```

For v0.0, forward the original email content with a small metadata header indicating that it was processed by Mail Automation.

Example:

```text
MAIL AUTOMATION
Classification: URGENT
Confidence: 0.94
Original sender: client@example.com
Original subject: Project deadline

--------------------------------

Original email content...
```

Use the Gmail API for sending.

---

# 12. Database

Use PostgreSQL.

Minimum tables:

```text
users
gmail_accounts
email_metadata
classifications
processing_events
user_rules
user_settings
```

## email_metadata

Store metadata required for processing and deduplication:

```text
id
user_id
gmail_account_id
gmail_message_id
gmail_thread_id
sender
subject
received_at
processed_at
forwarded_at
created_at
```

## classifications

```text
id
email_id
category
confidence
reason
model
created_at
```

## processing_events

```text
id
email_id
event_type
status
error_message
created_at
```

Possible event types:

```text
RECEIVED
FETCHED
NORMALIZED
CLASSIFIED
FORWARDING_STARTED
FORWARDED
FAILED
```

---

# 13. Idempotency

This is mandatory.

The same Gmail event or Pub/Sub message may be delivered more than once.

The system must prevent duplicate processing and duplicate forwarding.

Use a unique identifier such as:

```text
gmail_account_id + gmail_message_id
```

as an idempotency key.

Before processing an email:

```text
Does this Gmail message already have a completed processing record?

YES → skip
NO  → process
```

Forwarding must also be idempotent.

---

# 14. Error Handling

Implement retries for temporary failures.

Examples:

```text
Gmail API failure
AI API timeout
database temporary failure
email sending failure
```

Use exponential backoff where appropriate.

Permanent failures should be recorded in the database.

Do not silently discard failed processing jobs.

For v0.0, a simple failed-job table/status is sufficient.

---

# 15. REST API

Implement endpoints approximately like:

```text
GET  /api/health

GET  /api/auth/google
GET  /api/auth/google/callback

GET  /api/accounts
POST /api/accounts
DELETE /api/accounts/{account_id}

GET  /api/emails
GET  /api/emails/{email_id}

GET  /api/stats

GET  /api/rules
POST /api/rules
DELETE /api/rules/{rule_id}

GET  /api/settings
PUT  /api/settings
```

The frontend must never directly access Gmail credentials.

---

# 16. Dashboard

Build a minimal React dashboard.

Display:

```text
Connected Gmail accounts

Destination email

Emails processed today

Important emails

Urgent emails

Newsletters

Spam

Recent processing activity
```

Allow the user to:

```text
connect Gmail
disconnect Gmail
set destination email
create/delete simple rules
view recent processed emails
```

Do not build a full email client.

---

# 17. Security Requirements

Treat email contents as sensitive data.

Requirements:

* Never log email bodies.
* Never log OAuth tokens.
* Encrypt stored OAuth credentials.
* Never expose access/refresh tokens to the frontend.
* Use HTTPS in production.
* Validate OAuth state to prevent CSRF.
* Validate webhook authenticity where applicable.
* Use parameterized database queries/ORM.
* Apply authentication to all user-specific API endpoints.
* Ensure users can only access their own accounts and email metadata.

Minimize persistent storage of email contents.

For v0.0, store metadata and classification results. Process email body content transiently whenever practical.

---

# 18. Project Structure

Use a structure similar to:

```text
mail-automation/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── gmail/
│   │   ├── events/
│   │   ├── classifier/
│   │   ├── rules/
│   │   ├── forwarding/
│   │   ├── database/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── migrations/
│
├── docker-compose.yml
├── .env.example
├── README.md
└── .gitignore
```

Keep Gmail-specific implementation inside `gmail/`.

Keep AI-specific implementation inside `classifier/`.

Do not tightly couple the application to a particular AI provider.

---

# 19. Environment Variables

Provide `.env.example` containing placeholders for:

```text
DATABASE_URL=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=

GOOGLE_CLOUD_PROJECT=
GOOGLE_PUBSUB_TOPIC=
GOOGLE_PUBSUB_SUBSCRIPTION=

AI_PROVIDER=
AI_API_KEY=
AI_MODEL=

ENCRYPTION_KEY=

APP_SECRET=
```

Never commit actual credentials.

---

# 20. Development Strategy

Build in this order:

### Milestone 1

Create FastAPI application + PostgreSQL + database models.

### Milestone 2

Implement Google OAuth.

### Milestone 3

Connect one Gmail account and manually retrieve emails.

### Milestone 4

Implement normalized email representation.

### Milestone 5

Implement AI classification.

### Milestone 6

Implement forwarding.

At this point the basic product works.

### Milestone 7

Replace manual triggering/polling with Gmail Pub/Sub events.

### Milestone 8

Add idempotency, retries, logging, and failure handling.

### Milestone 9

Build React dashboard.

### Milestone 10

Dockerize the complete system and create local development instructions.

---

# 21. v0.0 Definition of Done

The prototype is considered successful when this complete flow works:

```text
User opens application
        ↓
Connects Gmail
        ↓
Configures destination email
        ↓
New email arrives
        ↓
Gmail generates notification
        ↓
Pub/Sub delivers event
        ↓
Backend retrieves email
        ↓
Email is normalized
        ↓
Classifier determines:
IMPORTANT
        ↓
Classification stored
        ↓
Email forwarded
        ↓
Destination inbox receives it
        ↓
Dashboard shows the processed email
```

The prototype does NOT need:

* billing
* subscriptions
* advanced analytics
* mobile application
* custom ML training
* sophisticated UI
* multi-provider email support
* autonomous email replies
* attachment processing
* enterprise administration

Prioritize a working end-to-end pipeline and clean separation between components.

# 22. Agent Instructions

You are implementing a prototype, not merely generating a design document.

Start by creating the repository structure and implementing the smallest working vertical slice.

Do not implement every future feature before testing the core pipeline.

After each milestone:

1. Run tests.
2. Verify the service starts.
3. Verify database migrations.
4. Verify API endpoints.
5. Document configuration requirements.
6. Keep secrets out of source control.

When an external Google Cloud/Gmail configuration is required, clearly document the manual setup steps instead of fabricating credentials or pretending the integration is configured.

Favor simple, maintainable implementations over premature abstraction, but maintain clear interfaces around Gmail, classification, rules, and forwarding so they can be replaced later.

