# test.py (one level above app/)
from app.translate import translate_text, _get_idiom_items, _tag_idioms_with_items

sentences = [
    "It's raining cats and dogs",
    "It's raining cats and dogs.",
    "It's raining cats and dogs so I should go inside.",
    "I should go inside because it's raining cats and dogs."
]

# Get idiom items for EN->ES
items = _get_idiom_items("en", "es")
print("idioms loaded:", len(items))

for s in sentences:
    print("\n---")
    print("INPUT :", repr(s))

    tagged = _tag_idioms_with_items(s, items)
    print("TAGGED:", tagged)

    final = translate_text(s, "en", "es")
    print("FINAL :", final)
