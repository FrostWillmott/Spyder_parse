# Spyder Parse

A Scrapy-based spider that scrapes proxies from [advanced.name/freeproxy](https://advanced.name/freeproxy) and uploads them to a specified endpoint.

## Features

- Scrapes first 150 proxies from advanced.name/freeproxy
- Saves proxies to `proxies.json` in structured format
- Uploads proxies to test-rg8.ddns.net using personal token
- Saves upload results with save_id to `results.json`
- Records execution time to `time.txt`
- Includes required `sec-fetch-mode: navigate` headers
- Built with Scrapy framework only (no external extensions)

## Requirements

- Python 3.11+
- Poetry

## Installation

```bash
# Install dependencies
poetry install
```

## Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` file and add your personal token:
```
PERSONAL_TOKEN=your_actual_personal_token_here
```

## Usage

```bash
# Simple run (recommended)
python run.py

# Or with Poetry directly
poetry run scrapy crawl proxy_spider

# Or with token override
python run.py YOUR_TOKEN
```

## Output Files

### `proxies.json`
```json
[
  {
    "ip": "0.0.0.0",
    "port": 8080,
    "protocols": ["HTTP", "HTTPS"]
  }
]
```

### `results.json`
```json
{
  "save_id_1": ["proxy1", "proxy2", "..."]
}
```

### `time.txt`
```
00:02:45
```

## Project Structure

```
Spyder_parse/
├── .env.example          # Environment template
├── .gitignore           # Git exclusions
├── README.md            # Documentation
├── pyproject.toml       # Poetry dependencies
├── scrapy.cfg          # Scrapy configuration
├── settings.py         # Scrapy settings
├── run.py              # Simple runner script
└── spiders/
    ├── __init__.py
    └── proxy_spider.py  # Main spider
```

## Technical Details

- **Framework**: Pure Scrapy
- **Headers**: All requests include required `sec-fetch-mode: navigate`
- **Security**: Personal tokens stored in `.env` file

## License

This project is for educational and testing purposes only.