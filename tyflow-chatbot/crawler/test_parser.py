"""Test parser with saved HTML"""
from poc_crawler import TyFlowPOCCrawler

crawler = TyFlowPOCCrawler()

# Load saved HTML
with open('debug_birth.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"HTML length: {len(html)}")

# Parse
url = "https://docs.tyflow.com/tyflow_particles/operators/birth/"
data = crawler.parse_page(html, url)

if data:
    print(f"\n✓ Parsing successful!")
    print(f"  Title: {data['title']}")
    print(f"  Sections: {len(data['sections'])}")
    for i, section in enumerate(data['sections'][:3], 1):
        print(f"\n  Section {i}:")
        print(f"    Heading: {section['heading']}")
        print(f"    Level: {section['level']}")
        print(f"    Anchor: {section['anchor']}")
        print(f"    Content length: {len(section['content'])}")
        print(f"    Params: {section['params'][:3] if section['params'] else []}")
else:
    print("\n✗ Parsing failed")
