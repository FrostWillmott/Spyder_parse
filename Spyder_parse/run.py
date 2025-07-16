"""Main runner for the proxy scraper.
"""
import sys

from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    """Run the proxy spider"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please create .env file with your PERSONAL_TOKEN")
        print("💡 You can copy .env.example to .env and edit it")
        return 1

    settings = get_project_settings()

    process = CrawlerProcess(settings)

    process.crawl("proxy_spider")

    print("🕷️  Starting proxy scraper...")
    process.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
