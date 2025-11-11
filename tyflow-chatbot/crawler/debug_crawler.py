"""Debug crawler to inspect actual HTML"""
import requests
from bs4 import BeautifulSoup

url = "https://docs.tyflow.com/tyflow_particles/operators/birth/"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Fetching {url}...")
response = session.get(url, timeout=10)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)} chars")

# Save raw HTML
with open("debug_birth.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"\nFirst 1000 chars:")
print(response.text[:1000])

print(f"\n\nParsing with BeautifulSoup...")
soup = BeautifulSoup(response.text, 'lxml')
print(f"Title tag: {soup.title}")
print(f"Has body: {soup.body is not None}")

if soup.body:
    print(f"Body children: {len(list(soup.body.children))}")
    print(f"First 500 chars of body: {soup.body.get_text()[:500]}")

# Find all top-level divs
divs = soup.find_all('div', limit=10)
print(f"\nFirst 10 divs:")
for i, div in enumerate(divs, 1):
    print(f"  {i}. id={div.get('id')}, class={div.get('class')}")
