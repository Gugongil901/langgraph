"""
Full Crawler for all tyFlow Operators
Crawls all 172 operator pages from docs.tyflow.com
"""
import json
import time
from pathlib import Path
from poc_crawler import TyFlowPOCCrawler


class TyFlowFullCrawler(TyFlowPOCCrawler):
    """Extended crawler for all operators"""

    def __init__(self, output_dir="data/operators"):
        super().__init__(output_dir)
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    def load_links(self, links_file="operators_links.json"):
        """Load operators links from JSON file"""
        with open(links_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def should_skip(self, url):
        """Check if URL should be skipped (already crawled)"""
        # Extract filename from URL
        url_parts = url.rstrip('/').split('/')
        filename = url_parts[-1] + '.json'
        filepath = self.output_dir / filename

        return filepath.exists()

    def crawl_all(self, links, skip_existing=True):
        """Crawl all operators from links list"""
        self.stats['total'] = len(links)

        print(f"\n📊 Planning to crawl {len(links)} operator pages")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"⏭️  Skip existing: {skip_existing}")
        print()

        for i, link in enumerate(links, 1):
            url = link['url']
            name = link['name']

            # Create filename from URL
            url_parts = url.rstrip('/').split('/')
            filename = url_parts[-1] + '.json'

            # Skip if already exists
            if skip_existing and self.should_skip(url):
                print(f"[{i}/{len(links)}] ⏭️  Skipping {name} (already exists)")
                self.stats['skipped'] += 1
                continue

            print(f"\n[{i}/{len(links)}] 📄 Crawling: {name}")
            print(f"  URL: {url}")

            try:
                success = self.crawl_page(url, filename)

                if success:
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1
                    self.stats['errors'].append({
                        'name': name,
                        'url': url,
                        'reason': 'Parse failed'
                    })

            except Exception as e:
                print(f"  ✗ Exception: {e}")
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'name': name,
                    'url': url,
                    'reason': str(e)
                })

            # Be polite - wait between requests
            if i < len(links):
                wait_time = 2
                print(f"  ⏳ Waiting {wait_time}s...")
                time.sleep(wait_time)

            # Progress summary every 10 pages
            if i % 10 == 0:
                self.print_progress()

    def print_progress(self):
        """Print current progress statistics"""
        done = self.stats['success'] + self.stats['failed'] + self.stats['skipped']
        print()
        print("─" * 60)
        print(f"📊 Progress: {done}/{self.stats['total']} pages")
        print(f"   ✓ Success: {self.stats['success']}")
        print(f"   ⏭️  Skipped: {self.stats['skipped']}")
        print(f"   ✗ Failed: {self.stats['failed']}")
        print("─" * 60)
        print()

    def print_summary(self):
        """Print final crawling summary"""
        print("\n" + "=" * 60)
        print("📊 Final Results")
        print("=" * 60)
        print(f"Total pages: {self.stats['total']}")
        print(f"✓ Successfully crawled: {self.stats['success']}")
        print(f"⏭️  Skipped (existing): {self.stats['skipped']}")
        print(f"✗ Failed: {self.stats['failed']}")

        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:10]:  # Show first 10
                print(f"  - {error['name']}: {error['reason']}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")

        print("=" * 60)

        # Calculate statistics from saved files
        json_files = list(self.output_dir.glob("*.json"))
        total_sections = 0
        total_params = 0

        for json_file in json_files[:10]:  # Sample first 10
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    total_sections += len(data.get('sections', []))
                    for section in data.get('sections', []):
                        total_params += len(section.get('params', []))
            except:
                pass

        if json_files:
            print(f"\n📈 Data Statistics (from {len(json_files)} files):")
            print(f"   Average sections per page: {total_sections / min(10, len(json_files)):.1f}")
            print(f"   Average params per page: {total_params / min(10, len(json_files)):.1f}")

        print()


def main():
    """Main execution"""
    print("=" * 60)
    print("🚀 tyFlow Full Operators Crawler")
    print("=" * 60)

    # Initialize crawler
    crawler = TyFlowFullCrawler(output_dir="../data/operators")

    # Load links
    links_file = "operators_links.json"
    if not Path(links_file).exists():
        print(f"\n❌ Error: {links_file} not found")
        print("Run extract_links.py first to generate the links file")
        return False

    links = crawler.load_links(links_file)
    print(f"\n✓ Loaded {len(links)} operator links from {links_file}")

    # Confirm before crawling
    print(f"\n⚠️  This will crawl {len(links)} pages (estimated time: ~{len(links) * 3 // 60} minutes)")
    print("Press Ctrl+C to cancel, or wait 3 seconds to continue...")
    time.sleep(3)

    # Crawl all
    start_time = time.time()
    crawler.crawl_all(links, skip_existing=True)

    # Print summary
    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed / 60:.1f} minutes")
    crawler.print_summary()

    # Check success rate
    success_rate = crawler.stats['success'] / crawler.stats['total'] if crawler.stats['total'] > 0 else 0
    return success_rate > 0.8  # 80% success rate threshold


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
