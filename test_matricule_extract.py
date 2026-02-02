import re

def extract_and_normalize_matricule(text: str) -> list:
    """Test de l'extraction de matricule"""
    text = text.upper().strip()
    
    # PATTERN 1: Lettres suivies IMMÉDIATEMENT de chiffres
    compact_match = re.search(r'([A-Z]{2})(\d{6,})', text)
    
    if compact_match:
        letters = compact_match.group(1)
        all_digits = compact_match.group(2)[:6]
        middle = all_digits[:4]
        end = all_digits[4:6]
        
        formats = []
        formats.append(f"{letters}-{middle}-{end}")
        formats.append(f"{letters}{middle}{end}")
        formats.append(f"{letters} {middle} {end}")
        return formats
    
    # PATTERN 2: Lettres séparées
    letter_match = re.search(r'\b([A-Z]{2})\s', text)
    
    if not letter_match:
        return []
    
    letters = letter_match.group(1)
    remaining_text = text[letter_match.end():]
    digits = re.findall(r'\d+', remaining_text)
    
    if not digits:
        return []
    
    all_digits = ''.join(digits)
    
    if len(all_digits) < 4:
        return []
    
    if len(all_digits) >= 6:
        middle = all_digits[:4]
        end = all_digits[4:6]
    else:
        middle = all_digits[:4]
        end = all_digits[4:].zfill(2) if len(all_digits) > 4 else "00"
    
    formats = []
    formats.append(f"{letters}-{middle}-{end}")
    formats.append(f"{letters}{middle}{end}")
    formats.append(f"{letters} {middle} {end}")
    
    return formats

# Tests
tests = [
    "My number of matricules is AB452122",
    "Mon numéro de matricule est AB452122",
    "AB 45, 21, 22",
    "mon matricule est FC 7834 19",
]

for test in tests:
    result = extract_and_normalize_matricule(test)
    print(f"Test: {test}")
    print(f"  -> {result}")
    print()
