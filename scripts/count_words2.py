"""Count words in updated markdown"""
import re

with open(r'E:\2026next\碳排放\论文.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove code blocks
text_no_code = re.sub(r'```[\s\S]*?```', '', text)
# Remove markdown syntax
text_clean = re.sub(r'[#*|`\[\]()!>-]', '', text_no_code)
text_clean = re.sub(r'---+', '', text_clean)
text_clean = re.sub(r'<center>|</center>', '', text_clean)
text_clean = re.sub(r'<.*?>', '', text_clean)

# Count Chinese characters
cn_chars = re.findall(r'[\u4e00-\u9fff]', text_clean)
# Count English words
en_words = re.findall(r'[a-zA-Z]+', text_clean)

print(f"Chinese characters: {len(cn_chars)}")
print(f"English words: {len(en_words)}")
print(f"Est. total (CN + EN*2): {len(cn_chars) + len(en_words)*2}")

# Count by chapter
chapters = re.split(r'## 第(\d)章', text)
print(f"\nChapter breakdown:")
for i in range(1, len(chapters), 2):
    ch_num = chapters[i]
    ch_text = chapters[i+1] if i+1 < len(chapters) else ''
    # Remove code blocks
    ch_clean = re.sub(r'```[\s\S]*?```', '', ch_text)
    ch_clean = re.sub(r'[#*|`\[\]()!>-]', '', ch_clean)
    ch_clean = re.sub(r'<.*?>', '', ch_clean)
    cn = len(re.findall(r'[\u4e00-\u9fff]', ch_clean))
    en = len(re.findall(r'[a-zA-Z]+', ch_clean))
    print(f"  第{ch_num}章: {cn} CN chars, {en} EN words, est={cn+en*2}")
