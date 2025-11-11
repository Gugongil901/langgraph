"""
Universal Crawler for all tyFlow documentation
Crawls all categories except Operators (already done)
"""
import json
import time
from pathlib import Path
from poc_crawler import TyFlowPOCCrawler


class UniversalCrawler(TyFlowPOCCrawler):
    """Universal crawler for all categories"""

    def __init__(self, base_output_dir="data"):
        # Don't call parent __init__ yet
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

        # Stats
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'by_category': {}
        }

        # Initialize session (from parent)
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get_category_dir(self, category):
        """Get output directory for category"""
        # Map category to folder name
        folder_map = {
            'Modifiers': 'modifiers',
            'AI': 'ai',
            'FAQ': 'faq',
            'SDK': 'sdk',
            'Particles_Docs': 'particles_docs',
            'Other_Misc': 'misc'
        }
        folder_name = folder_map.get(category, category.lower())
        cat_dir = self.base_output_dir / folder_name
        cat_dir.mkdir(parents=True, exist_ok=True)
        return cat_dir

    def get_filename(self, url, name):
        """Generate filename from URL"""
        # Extract last part of URL
        parts = url.rstrip('/').split('/')
        filename = parts[-1]

        # Fallback to name if URL part is empty
        if not filename or filename in ['tyflow_modifiers', 'tyflow_ai', 'faq']:
            filename = name.lower().replace(' ', '_').replace('/', '_')

        return filename + '.json'

    def should_skip(self, category, filename):
        """Check if file already exists"""
        cat_dir = self.get_category_dir(category)
        filepath = cat_dir / filename
        return filepath.exists()

    def crawl_category(self, category, links, skip_existing=True):
        """Crawl all pages in a category"""
        if category not in self.stats['by_category']:
            self.stats['by_category'][category] = {
                'total': len(links),
                'success': 0,
                'failed': 0,
                'skipped': 0
            }

        cat_dir = self.get_category_dir(category)

        print(f"\n{'='*60}")
        print(f"📁 Category: {category} ({len(links)} pages)")
        print(f"📂 Output: {cat_dir}")
        print(f"{'='*60}\n")

        for i, link in enumerate(links, 1):
            url = link['url']
            name = link['name']
            filename = self.get_filename(url, name)

            # Skip if exists
            if skip_existing and self.should_skip(category, filename):
                print(f"[{i}/{len(links)}] ⏭️  {name} (exists)")
                self.stats['skipped'] += 1
                self.stats['by_category'][category]['skipped'] += 1
                continue

            print(f"\n[{i}/{len(links)}] 📄 {name}")
            print(f"  {url}")

            try:
                # Set output directory for this category
                self.output_dir = cat_dir

                # Crawl page
                html = self.fetch_page(url)
                if not html:
                    self.stats['failed'] += 1
                    self.stats['by_category'][category]['failed'] += 1
                    continue

                # Parse page
                data = self.parse_page(html, url)
                if data:
                    # Add category to data
                    data['category'] = category

                    # Save
                    output_path = cat_dir / filename
                    import json as json_lib
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json_lib.dump(data, f, indent=2, ensure_ascii=False)

                    print(f"  ✓ {data['title']} ({len(data['sections'])} sections)")
                    self.stats['success'] += 1
                    self.stats['by_category'][category]['success'] += 1
                else:
                    self.stats['failed'] += 1
                    self.stats['by_category'][category]['failed'] += 1

            except Exception as e:
                print(f"  ✗ Error: {e}")
                self.stats['failed'] += 1
                self.stats['by_category'][category]['failed'] += 1
                self.stats['errors'].append({
                    'category': category,
                    'name': name,
                    'url': url,
                    'error': str(e)
                })

            # Be polite
            if i < len(links):
                time.sleep(2)

        # Category summary
        cat_stats = self.stats['by_category'][category]
        print(f"\n{'─'*60}")
        print(f"✅ {category} complete:")
        print(f"   Success: {cat_stats['success']}/{cat_stats['total']}")
        print(f"   Skipped: {cat_stats['skipped']}")
        print(f"   Failed: {cat_stats['failed']}")
        print(f"{'─'*60}\n")

    def crawl_all(self, all_links, categories_to_crawl=None, skip_existing=True):
        """Crawl all or selected categories"""

        # Default: all except Operators/Download/License/About
        if categories_to_crawl is None:
            categories_to_crawl = [
                'Modifiers', 'Particles_Docs', 'FAQ', 'AI',
                'Other_Misc', 'SDK'
            ]

        # Calculate total
        self.stats['total'] = sum(
            len(all_links[cat])
            for cat in categories_to_crawl
            if cat in all_links
        )

        print(f"\n📊 Planning to crawl {self.stats['total']} pages")
        print(f"   Categories: {', '.join(categories_to_crawl)}")
        print(f"   Skip existing: {skip_existing}\n")

        start_time = time.time()

        # Crawl each category
        for category in categories_to_crawl:
            if category in all_links:
                self.crawl_category(category, all_links[category], skip_existing)

        # Final summary
        elapsed = time.time() - start_time
        self.print_summary(elapsed)

    def print_summary(self, elapsed_time):
        """Print final summary"""
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS")
        print("=" * 60)
        print(f"Total pages: {self.stats['total']}")
        print(f"✓ Success: {self.stats['success']}")
        print(f"⏭️ Skipped: {self.stats['skipped']}")
        print(f"✗ Failed: {self.stats['failed']}")
        print(f"⏱️  Time: {elapsed_time/60:.1f} minutes")

        print(f"\n📂 By Category:")
        for cat, stats in self.stats['by_category'].items():
            print(f"  {cat:20s}: {stats['success']:3d}/{stats['total']:3d} "
                  f"(skip: {stats['skipped']}, fail: {stats['failed']})")

        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:
                print(f"  {error['category']}/{error['name']}: {error['error']}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")

        print("=" * 60)


def main():
    print("=" * 60)
    print("🌐 tyFlow Universal Documentation Crawler")
    print("=" * 60)

    # Load links
    links_file = "all_links.json"
    if not Path(links_file).exists():
        print(f"❌ {links_file} not found")
        return False

    with open(links_file, 'r') as f:
        raw_links = json.load(f)

    # Recategorize
    from collections import defaultdict
    all_links = defaultdict(list)

    for link in raw_links.get('Other', []):
        href = link['href'].lower()
        if '/tyflow_modifiers/' in href:
            all_links['Modifiers'].append(link)
        elif '/tyflow_particles/' in href and '/operators/' not in href:
            all_links['Particles_Docs'].append(link)
        else:
            all_links['Other_Misc'].append(link)

    # Add other categories
    for cat in ['AI', 'FAQ', 'SDK']:
        if cat in raw_links:
            all_links[cat] = raw_links[cat]

    # Initialize crawler
    crawler = UniversalCrawler(base_output_dir="../data")

    # Confirm
    total = sum(len(v) for k, v in all_links.items()
                if k in ['Modifiers', 'Particles_Docs', 'FAQ', 'AI', 'Other_Misc', 'SDK'])
    print(f"\n⚠️  Will crawl {total} pages")
    print("Press Ctrl+C to cancel, or wait 3 seconds...")
    time.sleep(3)

    # Crawl
    start_time = time.time()
    crawler.crawl_all(all_links, skip_existing=True)

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
