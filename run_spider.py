#!/usr/bin/env python3
"""Poetry-compatible runner for proxy scraper spider.
Follows best practices for dependency management and security.
"""

import subprocess
import sys

from env_manager import EnvManager
from pathlib import Path


def check_poetry_environment():
    """Check if we're in a Poetry environment"""
    try:
        result = subprocess.run(["poetry", "--version"],
                                check=False, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Poetry detected: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("❌ Poetry not found")
    return False


def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = {
        "scrapy": "Web scraping framework",
        "dotenv": "Environment variable management",
        "lxml": "XML/HTML parsing",
    }

    missing_packages = []

    for package, description in required_packages.items():
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description}")
            missing_packages.append(package)

    if missing_packages:
        print("\n📦 Install missing packages:")
        if check_poetry_environment():
            print("   poetry install")
        else:
            print(f"   pip install {' '.join(missing_packages)}")
        return False

    return True


def setup_scrapy_project():
    """Set up Scrapy project structure (Poetry-compatible)"""
    print("📂 Setting up Scrapy project structure...")

    # Create project structure
    project_dir = Path("proxy_scraper")
    project_dir.mkdir(exist_ok=True)

    spiders_dir = project_dir / "spiders"
    spiders_dir.mkdir(exist_ok=True)

    # Create __init__.py files
    (project_dir / "__init__.py").touch()
    (spiders_dir / "__init__.py").touch()

    # Create the spider with proper imports
    spider_content = '''"""
Proxy scraper spider - Poetry compatible version
"""

import scrapy
import json
import time
import os
import re
from dotenv import load_dotenv


class ProxySpider(scrapy.Spider):
    """Main proxy scraper spider"""

    name = 'proxy_spider'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 8,
        'DEFAULT_REQUEST_HEADERS': {
            'sec-fetch-mode': 'navigate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
        }
    }

    def __init__(self, token=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load environment variables
        load_dotenv()

        # Get token (CLI argument takes priority)
        self.personal_token = token or os.getenv('PERSONAL_TOKEN')

        if not self.personal_token or self.personal_token == 'your_personal_token_here':
            raise ValueError(
                "Valid personal token is required! "
                "Set PERSONAL_TOKEN in .env file or pass as argument."
            )

        self.start_time = time.time()
        self.proxies = []
        self.results = {}

        # Log masked token
        masked_token = self._mask_token(self.personal_token)
        self.logger.info(f"Initialized with token: {masked_token}")

    def _mask_token(self, token):
        """Mask token for safe logging"""
        if len(token) <= 8:
            return "*" * len(token)
        return token[:4] + "*" * (len(token) - 8) + token[-4:]

    def start_requests(self):
        """Start scraping proxies"""
        headers = {
            'sec-fetch-mode': 'navigate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        yield scrapy.Request(
            url='https://advanced.name/freeproxy',
            headers=headers,
            callback=self.parse_proxies
        )

    def parse_proxies(self, response):
        """Parse proxies from the website"""
        self.logger.info("Parsing proxies from advanced.name/freeproxy")

        # Try multiple selectors for robustness
        selectors = [
            'table tbody tr',
            'table tr:not(:first-child)',
            'tr:has(td)'
        ]

        proxy_rows = None
        for selector in selectors:
            proxy_rows = response.css(selector)
            if proxy_rows:
                self.logger.info(f"Found {len(proxy_rows)} rows using: {selector}")
                break

        if not proxy_rows:
            self.logger.error("Could not find proxy table")
            return

        # Parse each proxy row
        for i, row in enumerate(proxy_rows[:150]):  # Limit to 150
            proxy_data = self._parse_proxy_row(row, i)
            if proxy_data:
                self.proxies.append(proxy_data)

        self.logger.info(f"Successfully parsed {len(self.proxies)} proxies")

        # Save proxies and start upload
        self._save_proxies()
        yield from self._upload_proxies()

    def _parse_proxy_row(self, row, index):
        """Parse individual proxy row"""
        try:
            cells = row.css('td')
            if len(cells) < 2:
                return None

            # Extract IP
            ip = cells[0].css('::text').get()
            if not ip or not self._is_valid_ip(ip.strip()):
                return None

            # Extract port
            port_text = cells[1].css('::text').get()
            if not port_text:
                return None

            try:
                port = int(port_text.strip())
                if not (1 <= port <= 65535):
                    return None
            except ValueError:
                return None

            # Extract protocols
            protocols = self._extract_protocols(cells[2] if len(cells) > 2 else None)

            return {
                'ip': ip.strip(),
                'port': port,
                'protocols': protocols or ['HTTP']
            }

        except Exception as e:
            self.logger.error(f"Error parsing row {index}: {e}")
            return None

    def _is_valid_ip(self, ip):
        """Validate IP address"""
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False

    def _extract_protocols(self, protocol_cell):
        """Extract protocols from cell"""
        if not protocol_cell:
            return ['HTTP']

        protocols = []
        text = protocol_cell.get().upper()

        if 'HTTP' in text:
            protocols.extend(['HTTP', 'HTTPS'] if 'HTTPS' in text else ['HTTP'])
        if 'SOCKS' in text:
            if 'SOCKS5' in text:
                protocols.append('SOCKS5')
            elif 'SOCKS4' in text:
                protocols.append('SOCKS4')
            else:
                protocols.extend(['SOCKS4', 'SOCKS5'])

        return protocols or ['HTTP']

    def _save_proxies(self):
        """Save proxies to JSON file"""
        try:
            with open('proxies.json', 'w') as f:
                json.dump(self.proxies, f, indent=2)
            self.logger.info(f"Saved {len(self.proxies)} proxies to proxies.json")
        except Exception as e:
            self.logger.error(f"Error saving proxies: {e}")

    def _upload_proxies(self):
        """Upload proxies to form"""
        yield scrapy.Request(
            url='https://test-rg8.ddns.net',
            headers={'sec-fetch-mode': 'navigate'},
            callback=self._parse_upload_form
        )

    def _parse_upload_form(self, response):
        """Parse and submit upload form"""
        # Split proxies into chunks
        proxy_strings = [f"{p['ip']}:{p['port']}" for p in self.proxies]
        chunks = [proxy_strings[i:i+50] for i in range(0, len(proxy_strings), 50)]

        for i, chunk in enumerate(chunks):
            form_data = {
                'personal_token': self.personal_token,
                'proxies': '\\n'.join(chunk)
            }

            yield scrapy.FormRequest(
                url='https://test-rg8.ddns.net',
                formdata=form_data,
                headers={'sec-fetch-mode': 'navigate'},
                callback=self._parse_upload_response,
                meta={'chunk_index': i, 'chunk_proxies': chunk}
            )

    def _parse_upload_response(self, response):
        """Process upload response"""
        chunk_index = response.meta['chunk_index']
        chunk_proxies = response.meta['chunk_proxies']

        # Extract save_id
        save_id = self._extract_save_id(response.text, chunk_index)
        self.results[save_id] = chunk_proxies

        # Check if done
        expected_chunks = (len(self.proxies) + 49) // 50
        if len(self.results) >= expected_chunks:
            self._finalize()

    def _extract_save_id(self, text, chunk_index):
        """Extract save_id from response"""
        patterns = [
            r'save_id["\']?\\s*:\\s*["\']?([^"\'\\>\\s]+)',
            r'save_id=([^&\\s]+)',
            r'"save_id":\\s*"([^"]+)"'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return f"upload_{int(time.time())}_{chunk_index}"

    def _finalize(self):
        """Save results and execution time"""
        # Save results
        with open('results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        # Save execution time
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        with open('time.txt', 'w') as f:
            f.write(time_str)

        self.logger.info(f"Spider completed in {time_str}")
        self.logger.info(f"Proxies: {len(self.proxies)}, Uploads: {len(self.results)}")
'''

    with open(spiders_dir / "proxy_spider.py", "w") as f:
        f.write(spider_content)

    # Create scrapy.cfg
    cfg_content = """[settings]
default = proxy_scraper.settings

[deploy]
project = proxy_scraper
"""

    with open("scrapy.cfg", "w") as f:
        f.write(cfg_content)

    print("✅ Project structure created")


def run_spider(token=None):
    """Run the spider using appropriate method"""
    # Determine run method
    is_poetry = check_poetry_environment()

    if is_poetry:
        # Use poetry run
        cmd = ["poetry", "run", "scrapy", "crawl", "proxy_spider"]
    else:
        # Use direct scrapy
        cmd = ["scrapy", "crawl", "proxy_spider"]

    # Add token if provided
    if token:
        cmd.extend(["-a", f"token={token}"])

    try:
        print(f"🕷️  Running: {' '.join(cmd[:4])}...")
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Spider completed successfully!")
            return True
        print("❌ Spider failed!")
        print("Error:", result.stderr)
        return False

    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        if is_poetry:
            print("💡 Try: poetry install && poetry shell")
        else:
            print("💡 Try: pip install scrapy")
        return False


def main():
    """Main execution function"""
    print("🚀 Proxy Scraper - Poetry Edition")
    print("=" * 40)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Setup environment security
    env_manager = EnvManager()
    if not env_manager.setup_environment():
        sys.exit(1)

    # Get token
    cli_token = sys.argv[1] if len(sys.argv) > 1 else None
    token = env_manager.get_token(cli_token)

    if not token:
        print("❌ No valid token provided")
        sys.exit(1)

    # Setup project and run
    setup_scrapy_project()

    success = run_spider(token)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
