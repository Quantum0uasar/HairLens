# HairLens

HairLens is an AI-powered hair and skin analysis service that uses OpenAI’s GPT‑4o vision model to evaluate a user’s photo and return personalized care and style recommendations. It is built for salons, creators, and skincare brands that want an intelligent backend for photo-based consultations.

## Overview

Given a single uploaded image, HairLens analyzes visible hair and skin attributes and produces a structured JSON report. That report can be used to power client dashboards, booking flows, or marketing funnels that adapt automatically to the user’s hair type, scalp condition, and skin profile.

The backend is implemented in Python using FastAPI and Uvicorn, and integrates with OpenAI for vision analysis and ScrapingBee/Sephora for live product discovery.

## Features

- Photo-based analysis of hair and skin from a single uploaded image.
- Hair attribute detection (type, texture, hydration, scalp condition).
- Skin profile detection (tone, type, and primary concern).
- Structured JSON output suitable for API clients and frontends.
- Product recommendations for skincare and haircare (with static catalog fallback).
- Optional live product search against Sephora via ScrapingBee.
- Suggestions for haircut styles informed by the user’s hair and face shape.
- Interactive API documentation exposed via FastAPI’s `/docs` route.

## Architecture and Tech Stack

| Layer        | Technology                          |
|-------------|--------------------------------------|
| Language    | Python 3.13                          |
| Web API     | FastAPI, Uvicorn                     |
| AI / Vision | OpenAI GPT‑4o (vision)               |
| HTTP client | httpx                                |
| Images      | Pillow                               |
| Config      | python‑dotenv                        |
| Scraping    | ScrapingBee + Sephora product pages  |
| Frontend    | Vanilla JavaScript, HTML, CSS        |

The service is designed as a lightweight, stateless API that can be deployed behind any reverse proxy or integrated into existing web stacks.

## Project Structure

```text
HairLens/
├── main.py            # FastAPI application and route definitions
├── analyzer.py        # GPT‑4o vision analysis and parsing logic
├── products.py        # Static product catalog and lookup helpers
├── recommender.py     # Recommendation assembly and business rules
├── product_service.py # Integration with ScrapingBee / Sephora
├── static/
│   ├── index.html     # Simple web UI for manual testing
│   ├── app.js         # Frontend logic calling the /analyze endpoint
│   └── style.css      # Basic styling
└── .env               # Environment variables (not committed)
```

## Getting Started

### Prerequisites

- Python 3.11 or higher.
- An OpenAI API key with access to GPT‑4o.
- (Optional) A ScrapingBee API key if you want live product search instead of only the static catalog.

### Installation

```bash
git clone https://github.com/Quantum0uasar/HairLens.git
cd HairLens
python3 -m venv venv
source venv/bin/activate
venv/bin/pip install fastapi uvicorn openai python-multipart pillow python-dotenv httpx
```

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
HAIRLENS_MODEL=gpt-4o
SCRAPINGBEE_API_KEY=your_scrapingbee_key_here  # optional
```

The `.env` file is already ignored via `.gitignore` and should never be committed.

### Running the API

Start the development server with:

```bash
venv/bin/uvicorn main:app --reload
```

By default, the service will listen on `http://127.0.0.1:8000`.

- Root endpoint: `GET /` — basic health/landing response.
- API docs: `GET /docs` — interactive Swagger UI for all routes.
- OpenAPI schema: `GET /openapi.json`.

## API Reference

### `POST /analyze`

Analyze a single image and return hair and skin recommendations.

**Request**

- Method: `POST`
- Content type: `multipart/form-data`
- Body: a `file` field containing the image.

**Example cURL**

```bash
curl -X POST \
  -F "file=@your_photo.jpg" \
  http://127.0.0.1:8000/analyze
```

**Response**

On success, the endpoint returns a JSON payload similar to:

```json
{
  "hair_type": "straight",
  "hair_condition": "balanced",
  "hydration": "normal",
  "scalp": "healthy",
  "skin_tone": "medium",
  "skin_type": "combination",
  "primary_concern": "frizz",
  "skincare": [...],
  "haircare": {
    "shampoo": [...],
    "conditioner": [...],
    "treatments": [...]
  },
  "cuts": {
    "recommended": [...],
    "avoid": "..."
  }
}
```

Exact fields may evolve as the analysis prompts and recommendation logic are refined.

## Use Cases

HairLens is suitable for:

- Salon intake forms that convert a selfie into a consultation summary.
- E‑commerce flows that personalize product recommendations based on a customer’s photo.
- Creator tools that add “AI hair/skin assessment” as a backend feature for apps or bots.
- Internal experiments around AI‑assisted styling and skincare guidance.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
