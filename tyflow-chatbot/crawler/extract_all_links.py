"""
Extract ALL documentation links from docs.tyflow.com
Organized by category
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from collections import defaultdict


def extract_all_links():
    """Extract all documentation links organized by category"""
    base_url = "https://docs.tyflow.com"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    print(f"🔍 Fetching main page: {base_url}")
    response = session.get(base_url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    # Find sidebar navigation
    sidebar = soup.find(id='sidebar')
    if not sidebar:
        print("❌ Could not find sidebar")
        return {}

    links_by_category = defaultdict(list)

    # Process all links in sidebar
    for a in sidebar.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        # Skip empty or special links
        if not text or href == '#' or href == '/':
            continue

        full_url = urljoin(base_url, href).rstrip('/')

        # Determine category from URL
        category = determine_category(href)

        # Check if not duplicate
        if not any(link['url'] == full_url for link in links_by_category[category]):
            links_by_category[category].append({
                'url': full_url,
                'name': text,
                'href': href
            })

    return dict(links_by_category)


def determine_category(href):
    """Determine category from URL path"""
    href = href.lower()

    if '/tyflow_particles/operators/' in href:
        return 'Operators'
    elif '/modifiers/' in href:
        return 'Modifiers'
    elif '/tyflow_ai/' in href or '/tydiffusion/' in href:
        return 'AI'
    elif '/faq/' in href:
        return 'FAQ'
    elif '/controllers/' in href:
        return 'Controllers'
    elif '/helpers/' in href:
        return 'Helpers'
    elif '/objects/' in href:
        return 'Objects'
    elif '/tyflow_sdk/' in href:
        return 'SDK'
    elif '/maxscript/' in href:
        return 'MAXScript'
    elif '/spacewarps/' in href:
        return 'Spacewarps'
    elif '/splines/' in href:
        return 'Splines'
    elif '/texmaps/' in href:
        return 'Texmaps'
    elif '/utilities/' in href:
        return 'Utilities'
    elif '/io/' in href:
        return 'IO'
    elif '/materials/' in href:
        return 'Materials'
    elif '/download/' in href or '/version/' in href:
        return 'Download'
    elif '/license/' in href:
        return 'License'
    elif '/why/' in href:
        return 'About'
    else:
        return 'Other'


def main():
    print("=" * 60)
    print("🔗 Extracting ALL Documentation Links")
    print("=" * 60)
    print()

    links = extract_all_links()

    if not links:
        print("❌ No links found")
        return False

    # Print summary
    total_links = sum(len(v) for v in links.values())
    print(f"\n✓ Found {total_links} total pages across {len(links)} categories:\n")

    category_order = [
        'Operators', 'Modifiers', 'AI', 'FAQ',
        'Controllers', 'Helpers', 'Objects', 'SDK',
        'MAXScript', 'Spacewarps', 'Splines', 'Texmaps',
        'Utilities', 'IO', 'Materials', 'Download', 'License', 'About', 'Other'
    ]

    for category in category_order:
        if category in links:
            print(f"  {category:15s}: {len(links[category]):3d} pages")

    # Show sample from each category
    print("\n📄 Sample pages by category:\n")
    for category in category_order[:10]:  # First 10 categories
        if category in links and links[category]:
            print(f"\n{category}:")
            for link in links[category][:3]:
                print(f"  - {link['name']}")
            if len(links[category]) > 3:
                print(f"  ... and {len(links[category]) - 3} more")

    # Save to file
    output_file = "all_links.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to {output_file}")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
