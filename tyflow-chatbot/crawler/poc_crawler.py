"""
POC Crawler for docs.tyflow.com
Collects 2 sample pages: Mapping and Birth operators
"""
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class TyFlowPOCCrawler:
    def __init__(self, output_dir="data/operators"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://docs.tyflow.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # Don't set Accept-Encoding - let requests handle it automatically
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def fetch_page(self, url, retries=3):
        """Fetch a page with retry logic"""
        for attempt in range(retries):
            try:
                print(f"  Fetching {url} (attempt {attempt + 1}/{retries})...")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                print(f"  ✓ Success! Status: {response.status_code}")
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Error: {e}")
                if attempt < retries - 1:
                    wait_time = 3 * (attempt + 1)  # 3s, 6s, 9s
                    print(f"  Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"  ✗ Failed after {retries} attempts")
                    return None

    def parse_page(self, html, url):
        """Parse HTML and extract structured content"""
        soup = BeautifulSoup(html, 'lxml')

        # Extract main content
        content_elem = soup.find(id='body-inner')

        if not content_elem:
            print(f"  ⚠ Warning: Could not find #body-inner")
            return None

        # Extract title from first h1 or h2
        title_elem = content_elem.find('h1') or content_elem.find('h2')
        if title_elem:
            # Remove ** markdown if present
            title = title_elem.get_text(strip=True).replace('**', '')
            # Clean up "Birth operator" -> "Birth"
            title = title.replace(' operator', '').replace(' Operator', '')
        else:
            title = "Unknown"

        # Remove navigation, sidebar, footer
        for selector in ['.highlightable', 'nav', 'footer', '.header_menu']:
            for elem in content_elem.select(selector):
                elem.decompose()

        # Extract sections (H2, H3, H4)
        sections = []
        current_section = None

        for elem in content_elem.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'table', 'pre']):
            if elem.name in ['h2', 'h3', 'h4']:
                # Save previous section
                if current_section:
                    sections.append(current_section)

                # Start new section
                heading_text = elem.get_text(strip=True)
                anchor = elem.get('id', '') or self._make_anchor(heading_text)
                current_section = {
                    'heading': heading_text,
                    'level': elem.name,
                    'anchor': anchor,
                    'content': [],
                    'params': []
                }
            elif current_section:
                # Add content to current section
                text = elem.get_text(strip=True)
                if text:
                    current_section['content'].append(text)
                    # Extract parameter names (format: "Param Name: description")
                    import re
                    param_matches = re.findall(r'^([^:]+):', text)
                    for param_name in param_matches:
                        param_name = param_name.strip()
                        if param_name and len(param_name) < 50 and param_name not in current_section['params']:
                            current_section['params'].append(param_name)

        # Add last section
        if current_section:
            sections.append(current_section)

        # Combine section content
        for section in sections:
            section['content'] = '\n\n'.join(section['content'])
            section['params'] = list(set(section['params']))  # Remove duplicates

        return {
            'url': url,
            'title': title,
            'category': 'Operators',
            'operator': title,
            'sections': sections,
            'crawled_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }

    def _make_anchor(self, text):
        """Create anchor ID from heading text"""
        return text.lower().replace(' ', '-').replace('/', '-')

    def crawl_page(self, url, filename):
        """Crawl a single page and save to JSON"""
        print(f"\n📄 Crawling: {url}")

        html = self.fetch_page(url)
        if not html:
            return False

        data = self.parse_page(html, url)
        if not data:
            return False

        # Save to file
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved to {output_path}")
        print(f"  - Title: {data['title']}")
        print(f"  - Sections: {len(data['sections'])}")
        return True

    def run_poc(self):
        """Run POC: crawl 2 sample pages"""
        print("=" * 60)
        print("🚀 tyFlow Documentation POC Crawler")
        print("=" * 60)

        pages = [
            {
                'url': 'https://docs.tyflow.com/tyflow_particles/operators/mapping/',
                'filename': 'mapping.json'
            },
            {
                'url': 'https://docs.tyflow.com/tyflow_particles/operators/birth/',
                'filename': 'birth.json'
            }
        ]

        results = []
        for page in pages:
            success = self.crawl_page(page['url'], page['filename'])
            results.append(success)
            time.sleep(2)  # Be polite

        print("\n" + "=" * 60)
        print(f"📊 Results: {sum(results)}/{len(results)} pages successfully crawled")
        print("=" * 60)

        return all(results)


if __name__ == "__main__":
    crawler = TyFlowPOCCrawler(output_dir="../data/operators")
    success = crawler.run_poc()
    exit(0 if success else 1)
