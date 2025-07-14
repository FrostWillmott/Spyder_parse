"""
Scrapy settings for proxy_scraper project.
"""

BOT_NAME = "proxy_scraper"

SPIDER_MODULES = ["proxy_scraper.spiders"]
NEWSPIDER_MODULE = "proxy_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure request settings
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# Configure user agent
USER_AGENT = "proxy_scraper (+http://www.yourdomain.com)"

# Configure headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
    "sec-fetch-mode": "navigate",
}

# Configure retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Configure timeouts
DOWNLOAD_TIMEOUT = 60

# Configure AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Configure logging
LOG_LEVEL = "INFO"

# Disable telnet console
TELNETCONSOLE_ENABLED = False

# Configure cookies and redirects
COOKIES_ENABLED = True
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 30

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

# Set settings whose default value is deprecated
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"