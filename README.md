# Proxy Scraper

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

- Python 3.8+
- Poetry (recommended) or pip

## Installation

### Using Poetry (recommended)

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install scrapy python-dotenv
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

### Using Poetry

```bash
# Run the spider
poetry run python -m proxy_scraper.run

# Or using the script command
poetry run proxy-scraper

# Or using scrapy directly
poetry run scrapy crawl proxy_spider
```

### Using pip

```bash
# Run the spider
python -m proxy_scraper.run

# Or using scrapy directly
scrapy crawl proxy_spider
```

### Command line token override

```bash
# Override environment token
scrapy crawl proxy_spider -a token=your_token_here
```

## Output Files

The spider generates three files:

### `proxies.json`
```json
[
  {
    "ip": "0.0.0.0",
    "port": 8080,
    "protocols": ["HTTP", "HTTPS"]
  },
  {
    "ip": "1.1.1.1",
    "port": 3180,
    "protocols": ["SOCKS4", "SOCKS5"]
  }
]
```

### `results.json`
```json
{
  "save_id_1": ["proxy1", "proxy2", "..."],
  "save_id_2": ["proxy3", "proxy4", "..."]
}
```

### `time.txt`
```
00:02:45
```

## Project Structure

```
proxy-scraper/
├── proxy_scraper/
│   ├── __init__.py
│   ├── settings.py
│   ├── run.py
│   └── spiders/
│       ├── __init__.py
│       └── proxy_spider.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── scrapy.cfg
└── README.md
```

## Security

- Personal tokens are stored in `.env` file (not committed to Git)
- `.env` is included in `.gitignore`
- Environment variables take precedence over command line arguments

## Development

### Code formatting

```bash
# Format code
poetry run black proxy_scraper/
poetry run isort proxy_scraper/
```

### Running tests

```bash
poetry run pytest
```

## Technical Details

- **Framework**: Pure Scrapy (no external extensions)
- **Performance**: Optimized for <5 minutes execution
- **Headers**: All requests include required `sec-fetch-mode: navigate`
- **Error Handling**: Robust parsing with fallback methods
- **Logging**: Comprehensive logging for debugging

## Troubleshooting

1. **Missing .env file**: Copy `.env.example` to `.env` and add your token
2. **Import errors**: Ensure you're in the Poetry shell or virtual environment
3. **Network errors**: Check internet connection and website availability
4. **Parsing errors**: Check if website structure has changed

## License

This project is for educational and testing purposes only.