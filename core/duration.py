import re

UNITS = {
    "s" : 1, # Seconds
    "m" : 60, # Minutes
    "h" : 60*60, # Hours
    "d" : 24 * 60*60, # Day
    "w" : 7 * 24 * 60 * 60, # Week
    "mo": 30 * 24 * 60 * 60, # Month
    "y" : 365 * 24 * 60 * 60 # Year
}

PATTERN = re.compile(r"^(\d+)(mo|y|w|d|h|m|s)$")

def parse_duration(text):
    text = text.strip().lower()

    if text == "perm":
        return None

    match = PATTERN.match(text)
    if not match:
        raise ValueError(f"Incorrect time format: {text!r}")
    
    number = int(match.group(1))
    unit = match.group(2)

    if number == 0:
        raise ValueError(f"You can't set time to 0")

    return number * UNITS[unit]

def to_nft(seconds):
    if seconds % UNITS["d"] == 0:
        return f"{seconds // UNITS['d']}d"
    return f"{seconds}s"
