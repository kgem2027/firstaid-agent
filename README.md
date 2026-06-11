# Herbal First Aid Agent

An AI-powered plant medicine guide. Upload a photo of your ailment, describe your symptoms, and get recommendations for medicinal plants native to your region — cross-referenced across iNaturalist observations, regional ethnobotany databases, and Dr. Duke's Phytochemical Database.

## How it works

1. User uploads an image of their ailment + symptoms + country
2. Gemini 2.5 Flash analyzes the image and derives therapeutic keywords
3. iNaturalist is queried for locally observed medicinal plants in that country
4. A regional ethnobotany database is searched semantically using keyword embeddings
5. Dr. Duke's Phytochemical Database is cross-referenced against the iNaturalist results
6. A curated, safety-filtered plant list is returned with sources and matching uses
7. Uses MongoDB MCP to log all anaysis provided
## Tech stack

**Frontend:** React 19, React Router 7, Tailwind CSS 4, Vite 8, Axios

**Backend:** FastAPI, Uvicorn, Python 3.13, Pydantic v2, python-jose (JWT), bcrypt

**Database:** MongoDB Atlas, Motor, Beanie

**AI:** Google Gemini 2.5 Flash, Google ADK 2.1, Gemini text-embedding-004, MCP (Model Context Protocol)

**External APIs:** iNaturalist, Google Maps Geocoding, Dr. Duke's Phytochemical Database

**Deployment:** Docker, Railway

---

## Prerequisites

- Python 3.13+
- Node.js 20+
- npm
- A MongoDB Atlas cluster (with a database and vector search index named `unified_vector_search` on the `embedding` field of your `unifiedethnobotanies` collection)
- A Google Cloud project with Vertex AI enabled
- Service account credentials with Vertex AI User role

---

## Environment variables

Create a `.env` file inside the `server/` directory:

```env
# MongoDB
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority
DB_NAME=firstaid

# JWT
SECRET_KEY=your-secret-key-here

# Google Cloud / Vertex AI
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Option A: base64-encoded service account JSON (recommended for deployment)
GOOGLE_APPLICATION_CREDENTIALS_JSON=<base64-encoded-service-account-json>

# Option B: path to service account key file (local development)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

---

## Local setup

### 1. Clone the repo

```bash
git clone <repo-url>
cd firstaid-Agent
```

### 2. Backend

```bash
cd server

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install the MongoDB MCP server (requires Node.js 20+)
npm install -g mongodb-mcp-server

# Add your .env file (see Environment variables section above)
```

### 3. Frontend

```bash
cd client
npm install
```

---

## Running locally

Open two terminals from the project root.

**Terminal 1 — Backend:**

```bash
cd server
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

uvicorn main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

**Terminal 2 — Frontend:**

```bash
cd client
npm run dev
```

The app will be available at `http://localhost:5173`. The Vite dev server proxies all `/api` requests to the backend automatically.

---

## Running with Docker

```bash
cd server

docker build -t firstaid-agent .

docker run -p 8000:8000 \
  --env-file .env \
  -e PORT=8000 \
  firstaid-agent
```

---

## Deploying to Railway

The backend is configured for Railway via `nixpacks.toml`. Ensure the following environment variables are set in your Railway service:

- `MONGO_URI`
- `SECRET_KEY`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` (base64-encoded service account JSON)

For the frontend, set the Vite `VITE_API_URL` or update the proxy target in `vite.config.js` to point to your deployed backend URL before building:

```bash
cd client
npm run build
```

Deploy the contents of `client/dist/` to a static hosting provider (Railway, Vercel, Netlify, etc.).

---

## API routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive JWT |
| POST | `/api/analyze/` | Analyze ailment image (auth required) |
| GET | `/api/history/` | Retrieve past analyses (auth required) |
| GET | `/api/plants/` | Query iNaturalist nearby plants |
| GET | `/api/location/` | Geocode a location |
| GET | `/api/ddplants/` | Search Dr. Duke's database |

---

## Medical disclaimer

This application is for informational and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified health provider before using any plant-based remedy.
