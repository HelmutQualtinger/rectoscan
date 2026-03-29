# Rectoscan

A web application for reordering PDF pages — designed to correct interleaved page order from double-sided scanning with a single-sided scanner.

## How It Works

When scanning a double-sided document with a single-sided scanner, the typical workflow produces a single PDF where all front pages come first (1, 3, 5, …) followed by all back pages in reverse order (…, 6, 4, 2). Rectoscan reorders these pages into the correct sequential order (1, 2, 3, 4, …).

## Installation

### Prerequisites

- Docker
- Docker Compose

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rectoscan
   ```

2. The app uses an external Docker network named `reverse-proxy`. Create it if it doesn't exist:
   ```bash
   docker network create reverse-proxy
   ```

3. Build and start the container:
   ```bash
   docker compose up -d
   ```

## Usage

Once the container is running, open your browser and navigate to the address exposed by your reverse proxy, or access it directly at:

```
http://localhost:8000
```

Use the web interface to:
- Upload your interleaved PDF
- Download the reordered PDF

## Operations

| Task | Command |
|------|---------|
| Start | `docker compose up -d` |
| Stop | `docker compose down` |
| View logs | `docker compose logs -f` |
| Rebuild after changes | `docker compose up -d --build` |