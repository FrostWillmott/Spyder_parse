"""Main runner for the proxy scraper.
"""
import sys

from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    """Run the proxy spider"""
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please create .env file with your PERSONAL_TOKEN")
        print("💡 You can copy .env.example to .env and edit it")
        return 1

    # Get settings
    settings = get_project_settings()

    # Create crawler process
    process = CrawlerProcess(settings)

    # Add spider
    process.crawl("proxy_spider")

    # Start crawling
    print("🕷️  Starting proxy scraper...")
    process.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
