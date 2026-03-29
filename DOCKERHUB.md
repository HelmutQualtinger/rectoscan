# Rectoscan

Web service for correcting PDF page order from double-sided scanning with a single-sided scanner.

When scanning a two-sided document with a single-sided scanner, the result is an interleaved PDF: all front pages first (1, 3, 5, …), then all back pages in reverse order (…, 6, 4, 2). Rectoscan reorders the pages back into sequential order (1, 2, 3, 4, …).

## Quick Start

```bash
docker run -d -p 5000:5000 helmutqualtinger/rectoscan
```

Open `http://localhost:5000` in your browser, upload your PDF, and download the reordered result.

## Usage with Docker Compose

```yaml
services:
  rectoscan:
    image: helmutqualtinger/rectoscan
    ports:
      - "5000:5000"
```

### Behind a reverse proxy (Traefik / nginx-proxy)

```yaml
services:
  rectoscan:
    image: helmutqualtinger/rectoscan
    networks:
      - reverse-proxy

networks:
  reverse-proxy:
    external: true
```

## Details

| Property | Value |
|----------|-------|
| Port | `5000` |
| Server | Gunicorn (2 workers) |
| Base image | `python:3.9-alpine` |
| Runs as | `nobody` (non-root) |
| Max upload size | 16 MB |

## Constraints

- Input PDF must have an **even number of pages**
- Only `.pdf` files are accepted

## Source

[github.com/HelmutQualtinger/rectoscan](https://github.com/HelmutQualtinger/rectoscan)