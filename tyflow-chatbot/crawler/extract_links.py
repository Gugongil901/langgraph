"""
Extract all Operators links from docs.tyflow.com sidebar
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json


def extract_operators_links():
    """Extract all operators links from the documentation"""
    base_url = "https://docs.tyflow.com"
    start_url = f"{base_url}/tyflow_particles/operators/"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    print(f"🔍 Fetching operators page: {start_url}")
    response = session.get(start_url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    # Find sidebar navigation
    sidebar = soup.find(id='sidebar')
    if not sidebar:
        print("❌ Could not find sidebar")
        return []

    # Find all links in sidebar
    links = []
    for a in sidebar.find_all('a', href=True):
        href = a['href']

        # Only include operators links
        if '/tyflow_particles/operators/' in href and href != '/tyflow_particles/operators/':
            full_url = urljoin(base_url, href)

            # Remove trailing slash for consistency
            full_url = full_url.rstrip('/')

            # Get link text
            text = a.get_text(strip=True)

            if full_url not in [l['url'] for l in links]:
                links.append({
                    'url': full_url,
                    'name': text
                })

    return links


def main():
    print("=" * 60)
    print("🔗 Extracting Operators Links")
    print("=" * 60)
    print()

    links = extract_operators_links()

    if not links:
        print("❌ No links found")
        return False

    print(f"\n✓ Found {len(links)} operator pages:\n")

    for i, link in enumerate(links, 1):
        print(f"{i:3d}. {link['name']}")
        print(f"     {link['url']}")

    # Save to file
    output_file = "operators_links.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to {output_file}")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
