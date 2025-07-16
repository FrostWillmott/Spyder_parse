"""Proxy scraper spider.
Scrapes proxies from advanced.name and uploads to test-rg8.ddns.net
"""
import json
import os
import re
import scrapy
import time

from dotenv import load_dotenv

load_dotenv()


class ProxySpider(scrapy.Spider):
    """Spider for scraping and uploading proxies"""

    name = "proxy_spider"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 8,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "DEFAULT_REQUEST_HEADERS": {
            "sec-fetch-mode": "navigate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en",
        },
    }

    def __init__(self, token: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.personal_token = token or os.getenv("PERSONAL_TOKEN")

        if not self.personal_token:
            raise ValueError(
                "Personal token is required! "
                "Set PERSONAL_TOKEN in .env file or pass as argument",
            )

        self.start_time = time.time()
        self.proxies: list[dict] = []
        self.results: dict[str, list[str]] = {}

    def start_requests(self):
        """Start scraping proxies"""
        yield scrapy.Request(
            url="https://advanced.name/freeproxy",
            headers={"sec-fetch-mode": "navigate"},
            callback=self.parse_proxies,
        )

    def parse_proxies(self, response):
        """Parse proxies from the website"""
        self.logger.info("Parsing proxies from advanced.name/freeproxy")

        rows = response.css("table tbody tr")
        if not rows:
            rows = response.css("table tr:not(:first-child)")

        if not rows:
            self.logger.error("Could not find proxy table")
            return

        for i, row in enumerate(rows[:150]):
            proxy = self._parse_proxy_row(row, i + 1)
            if proxy:
                self.proxies.append(proxy)

        self.logger.info(f"Successfully parsed {len(self.proxies)} proxies")

        self._save_proxies()

        yield from self._upload_proxies()

    def _parse_proxy_row(self, row, row_num: int) -> dict | None:
        """Parse individual proxy row"""
        try:
            cells = row.css("td")
            if len(cells) < 2:
                return None

            ip = cells[0].css("::text").get()
            if not ip:
                return None
            ip = ip.strip()

            port_text = cells[1].css("::text").get()
            if not port_text:
                return None

            try:
                port = int(port_text.strip())
            except ValueError:
                return None

            protocols = self._extract_protocols(cells[2] if len(cells) > 2 else None)

            proxy = {
                "ip": ip,
                "port": port,
                "protocols": protocols,
            }

            self.logger.debug(f"Parsed proxy {row_num}: {ip}:{port} - {protocols}")
            return proxy

        except Exception as e:
            self.logger.error(f"Error parsing row {row_num}: {e}")
            return None

    def _extract_protocols(self, protocol_cell) -> list[str]:
        """Extract protocols from table cell"""
        if not protocol_cell:
            return ["HTTP"]

        cell_text = protocol_cell.get().upper()
        protocols = []

        if "HTTPS" in cell_text:
            protocols.extend(["HTTP", "HTTPS"])
        elif "HTTP" in cell_text:
            protocols.append("HTTP")

        if "SOCKS5" in cell_text:
            protocols.append("SOCKS5")
        elif "SOCKS4" in cell_text:
            protocols.append("SOCKS4")
        elif "SOCKS" in cell_text:
            protocols.extend(["SOCKS4", "SOCKS5"])

        return protocols or ["HTTP"]

    def _save_proxies(self):
        """Save proxies to JSON file"""
        try:
            with open("proxies.json", "w") as f:
                json.dump(self.proxies, f, indent=2)
            self.logger.info(f"Saved {len(self.proxies)} proxies to proxies.json")
        except Exception as e:
            self.logger.error(f"Error saving proxies: {e}")

    def _upload_proxies(self):
        """Upload proxies to the form"""
        if not self.proxies:
            self.logger.error("No proxies to upload")
            return

        yield scrapy.Request(
            url="https://test-rg8.ddns.net",
            headers={"sec-fetch-mode": "navigate"},
            callback=self._submit_form,
        )

    def _submit_form(self, response):
        """Submit proxies to the upload form"""
        self.logger.info("Submitting proxies to upload form")

        # Prepare proxy strings
        proxy_strings = [f"{proxy['ip']}:{proxy['port']}" for proxy in self.proxies]

        # Split into chunks of 50
        chunk_size = 50
        chunks = [
            proxy_strings[i : i + chunk_size]
            for i in range(0, len(proxy_strings), chunk_size)
        ]

        self.logger.info(f"Uploading {len(chunks)} chunks of proxies")

        # Submit each chunk
        for chunk_index, chunk in enumerate(chunks):
            form_data = {
                "personal_token": self.personal_token,
                "proxies": "\n".join(chunk),
            }

            yield scrapy.FormRequest(
                url="https://test-rg8.ddns.net",
                formdata=form_data,
                headers={"sec-fetch-mode": "navigate"},
                callback=self._parse_upload_response,
                meta={"chunk_index": chunk_index, "chunk_proxies": chunk},
            )

    def _parse_upload_response(self, response):
        """Parse upload response and extract save_id"""
        chunk_index = response.meta["chunk_index"]
        chunk_proxies = response.meta["chunk_proxies"]

        self.logger.info(f"Processing upload response for chunk {chunk_index + 1}")

        save_id = self._extract_save_id(response.text, chunk_index)

        self.results[save_id] = chunk_proxies

        self.logger.info(f"Chunk {chunk_index + 1} uploaded with save_id: {save_id}")

        expected_chunks = (len(self.proxies) + 49) // 50  # Ceiling division
        if len(self.results) >= expected_chunks:
            self._finalize_spider()

    def _extract_save_id(self, response_text: str, chunk_index: int) -> str:
        """Extract save_id from upload response"""
        patterns = [
            r'save_id["\']?\s*:\s*["\']?([^"\'>\s]+)',
            r"save_id=([^&\s]+)",
            r'"save_id":\s*"([^"]+)"',
            r"Success[^a-zA-Z0-9]*([a-zA-Z0-9\-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                save_id = match.group(1)
                self.logger.debug(f"Found save_id using pattern: {save_id}")
                return save_id

        save_id = f"upload_{int(time.time())}_{chunk_index}"
        self.logger.warning(f"Could not extract save_id, using: {save_id}")
        return save_id

    def _finalize_spider(self):
        """Save results and execution time"""
        try:
            with open("results.json", "w") as f:
                json.dump(self.results, f, indent=2)
            self.logger.info(f"Saved upload results with {len(self.results)} entries")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

        self._save_execution_time()

        self.logger.info("Spider execution completed successfully")
        self.logger.info(f"Proxies scraped: {len(self.proxies)}")
        self.logger.info(f"Upload batches: {len(self.results)}")

    def _save_execution_time(self):
        """Save execution time to file"""
        try:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            with open("time.txt", "w") as f:
                f.write(time_str)

            self.logger.info(f"Execution time: {time_str}")
        except Exception as e:
            self.logger.error(f"Error saving execution time: {e}")
