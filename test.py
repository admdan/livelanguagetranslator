from app.translate import translate_text, _get_idiom_mapping, _tag_idioms

s = "I'm feeling under the weather, break a leg tonight and don't spill the beans."

mapping = _get_idiom_mapping("en", "es")
print("idioms loaded:", len(mapping))

tagged, repls = _tag_idioms(s, mapping)
print("TAGGED:", tagged)
print("REPLS:", repls)

print("FINAL:", translate_text(s, "en", "es"))

# this is just for debugging idiom mappings