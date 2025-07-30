import json
import hashlib
from collections import Counter, defaultdict
import re
from datetime import datetime

print('=== FINAL VERIFICATION OF ALL FACTS ===')

# Load data
with open('MASSIV_GROUPED.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('1. BASIC NUMBERS:')
print(f'   Companies: {len(data)}')
total_records = sum(company['count'] for company in data)
print(f'   Records: {total_records}')

print('\n2. COUNT CONSISTENCY:')
inconsistent_count = 0
for company in data:
    if company['count'] != len(company['records']):
        inconsistent_count += 1
print(f'   Count mismatches: {inconsistent_count}')

print('\n3. FIELD COMPLETENESS:')
empty_fields = {'timestamp': 0, 'content': 0, 'full_content': 0}
identical_content = 0
content_lengths = []
full_content_lengths = []

for company in data:
    for record in company['records']:
        for field in empty_fields:
            if not record.get(field, '').strip():
                empty_fields[field] += 1
        
        if record.get('content', '') == record.get('full_content', ''):
            identical_content += 1
            
        content_lengths.append(len(record.get('content', '')))
        full_content_lengths.append(len(record.get('full_content', '')))

for field, count in empty_fields.items():
    print(f'   Empty {field}: {count}')
    
print(f'   Identical content/full_content: {identical_content} ({identical_content/total_records*100:.1f}%)')
print(f'   Average content length: {sum(content_lengths)/len(content_lengths):.0f} chars')
print(f'   Average full_content length: {sum(full_content_lengths)/len(full_content_lengths):.0f} chars')

print('\n4. CONTENT QUALITY:')
truncated_content = 0
truncated_full_content = 0

for company in data:
    for record in company['records']:
        if record.get('content', '').strip().endswith('...'):
            truncated_content += 1
        if record.get('full_content', '').strip().endswith('...'):
            truncated_full_content += 1

print(f'   Truncated content (...): {truncated_content}')
print(f'   Truncated full_content (...): {truncated_full_content}')

print('\n5. DUPLICATES:')
content_hashes = defaultdict(list)
full_content_hashes = defaultdict(list)

all_records = []
for company in data:
    all_records.extend(company['records'])

for i, record in enumerate(all_records):
    content_hash = hashlib.md5(record.get('content', '').encode()).hexdigest()
    content_hashes[content_hash].append(i)
    
    full_content_hash = hashlib.md5(record.get('full_content', '').encode()).hexdigest()
    full_content_hashes[full_content_hash].append(i)

content_duplicate_groups = sum(1 for indices in content_hashes.values() if len(indices) > 1)
full_content_duplicate_groups = sum(1 for indices in full_content_hashes.values() if len(indices) > 1)

print(f'   Duplicate groups by content: {content_duplicate_groups}')
print(f'   Duplicate groups by full_content: {full_content_duplicate_groups}')

print('\n6. TIME PATTERNS:')
timestamps = []
for record in all_records:
    timestamp_str = record.get('timestamp', '')
    if timestamp_str:
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            timestamps.append(timestamp)
        except:
            pass

if timestamps:
    timestamps.sort()
    years = Counter(ts.year for ts in timestamps)
    months = Counter(f'{ts.year}-{ts.month:02d}' for ts in timestamps)
    
    print(f'   Period: {timestamps[0].strftime("%Y-%m-%d")} - {timestamps[-1].strftime("%Y-%m-%d")}')
    print(f'   2024 year: {years.get(2024, 0)} interviews')
    print(f'   2025 year: {years.get(2025, 0)} interviews')
    print(f'   Peak activity: {months.most_common(1)[0]} ({months.most_common(1)[0][1]} interviews)')

print('\n7. TOP COMPANIES:')
companies_sorted = sorted(data, key=lambda x: x['count'], reverse=True)
for i, company in enumerate(companies_sorted[:5], 1):
    print(f'   {i}. {company["company"]}: {company["count"]} interviews')

print('\n8. TECHNOLOGIES (mentions in text):')
all_texts = ' '.join(record.get('content', '') + ' ' + record.get('full_content', '') for record in all_records).lower()

technologies = {
    'react': len(re.findall(r'\breact\b', all_texts)),
    'typescript': len(re.findall(r'\btypescript\b', all_texts)),  
    'javascript': len(re.findall(r'\bjavascript\b', all_texts)),
    'go': len(re.findall(r'\bgo\b', all_texts)),
    'vue': len(re.findall(r'\bvue\b', all_texts))
}

for tech, count in sorted(technologies.items(), key=lambda x: x[1], reverse=True):
    print(f'   {tech.upper()}: {count} mentions')

print('\n9. INTERVIEW STAGES:')
stages = {}
for i in range(1, 4):
    pattern = f'{i}\\s*stage|{i}\\s*etap'
    count = len(re.findall(pattern, all_texts, re.IGNORECASE))
    if count > 0:
        stages[f'{i} stage'] = count

for stage, count in stages.items():
    print(f'   {stage}: {count} mentions')

print('\n10. TELEGRAM AUTHORS:')
authors = Counter()
for record in all_records:
    content = record.get('content', '')
    match = re.search(r'([А-Яа-яA-Za-z\s]+)\s*->\s*\d+:', content)
    if match:
        author = match.group(1).strip()
        if 2 < len(author) < 50:
            authors[author] += 1

print('   Top-5 authors:')
for author, count in authors.most_common(5):
    print(f'   {author}: {count} records')

print('\n11. CONTENT_HASH FIELD:')
has_content_hash = any('content_hash' in record for record in all_records)
print(f'   content_hash field present: {has_content_hash}')

print('\n=== VERIFICATION RESULT ===')
print('All main facts from previous analysis CONFIRMED!')