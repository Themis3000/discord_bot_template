"""
Converts various things to discord emoji form
"""

emoji_number = {"0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣",
                "7": "7️⃣", "8": "8️⃣", "9": "9️⃣"}
# reversed emoji_number dict for reverse conversions
number_emoji = dict(zip(emoji_number.values(), emoji_number.keys()))


def from_numbers(number):
    """
    converts any given int (or string of numbers) to their discord emoji equivalents
    """
    emojis = ""
    for char in str(number):
        emojis += emoji_number[char]
    return emojis


def to_number(emoji: str):
    """
    converts a discord number emoji to an int
    """
    return int(number_emoji[emoji])
