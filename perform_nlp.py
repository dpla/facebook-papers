import spacy
import sys
import json

nlp = spacy.load("en_core_web_sm")

noun_phrases = []
entities = []

with open('manifest.json', 'r') as manifest_file:
    data = manifest_file.read()

for item in json.loads(data):
    slug = item["slug"]
    with open(f"processed/{slug}/{slug}.txt", "r") as file:
        text = file.read()

    doc = nlp(text)
    noun_phrases += [chunk.text for chunk in doc.noun_chunks]
    entities += [(entity.text, entity.label_) for entity in doc.ents]

print("ENTITIES")
for entity in entities:
    print(f"{entity[0]} ({entity[1]})")

print("\n\nNOUN PHRASES")
for noun_phrase in noun_phrases:
    print(noun_phrase)
