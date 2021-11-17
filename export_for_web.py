import json
import os
import re
from pathlib import Path
from PIL import Image

def mkdir(directory):
    try:
        os.mkdir(directory)
    except OSError as error:
        pass


def main():
    page_num_re = re.compile(r"^page-(\d{3}).txt$")
    documents = {}

    with open('manifest.json', 'r') as manifest_file:
        manifest = json.loads(manifest_file.read())

    for slug in [item['slug'] for item in manifest]:
        print(slug)
        processed_dir = f"processed/{slug}"
        output_dir = f"web/public/{slug}"
        mkdir(output_dir)
        pages = {}
        documents[slug] = pages

        for file in sorted(os.listdir(processed_dir)):
            re_result = page_num_re.match(file)
            if not re_result:
                continue
            page_num = str(re_result.group(1))
            with open(f"{processed_dir}/page-{page_num}.txt", "r") as text_file:
                text = text_file.read()
            pages[page_num] = text
            picture_file = f"{processed_dir}/page-{page_num}.png"
            with Image.open(picture_file, mode='r', formats=None) as img:
                output_filename = Path(picture_file).stem
                output_path = f"{output_dir}/{output_filename}.jpg"
                img = img.convert("RGB")
                img.save(output_path, "JPEG")

    manifest_json = json.dumps(documents)
    with open("web/public/manifest.json", "w") as manifest_file:
        manifest_file.write(manifest_json)

if __name__ == "__main__":
    main()
