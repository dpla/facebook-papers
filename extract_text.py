import json
import os
import re
import pprint

with open("manifest.json", "rb") as manifest_data:
    manifest = json.loads(manifest_data.read())

slugs = [item['slug'] for item in manifest]

ocr_file_re = re.compile(r"output-(\d+)-to-\d+.json")

json_files = {}

for slug in slugs:
    slug_files = {}
    json_files[slug] = slug_files
    dir_name = f"processed/{slug}"

    for file_name in os.listdir(dir_name):
        re_result = ocr_file_re.match(file_name)
        if not re_result:
            continue
        page_start = int(re_result.group(1))
        slug_files[page_start] = f"processed/{slug}/{file_name}"


for slug in slugs:  # for every document
    print(f"Extracting {slug}")
    page_num = 1  # keep track of document page numbers
    slug_files = json_files[slug]  # get the document
    for key in sorted(slug_files.keys()):  # sort the ocr files by initial page range
        file_name = slug_files[key]  # get the next ocr file
        with open(file_name, 'r') as file:
            data = json.loads(file.read())
            for idx in range(len(data['responses'])):  # an ocr file has multiple pages in it
                page = data['responses'][idx]  # get the next page
                annotation = page['fullTextAnnotation']
                output_file_idx_str = str(page_num).zfill(3)
                output_file_name = f"page-{output_file_idx_str}.txt"
                output_file_path = f"processed/{slug}/{output_file_name}"
                with open(output_file_path, "w") as output_file:
                    output_file.write(annotation['text'])
                page_num += 1
