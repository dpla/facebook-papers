import json
import os
import re


def main():
    with open("manifest.json", "rb") as manifest_data:
        manifest = json.loads(manifest_data.read())

    slugs = [item['slug'] for item in manifest]

    # first collect a dict of slugs to dicts of page range starts to json files
    # we need this to sort the page ranges as integers so the pages come out
    # coordinated
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

    # now we can process the json files and put them in the right places

    for slug in slugs:  # for every document
        print(f"Extracting {slug}")
        # keep track of document page numbers across multiple json files
        page_num = 1
        slug_files = json_files[slug]  # get the document
        full_texts = []  # keeps track of the full text of the doc
        # sort the ocr files by initial page range
        for key in sorted(slug_files.keys()):
            file_name = slug_files[key]  # get the next ocr file
            with open(file_name, 'r') as file:
                data = json.loads(file.read())
                # an ocr file has multiple pages in it
                for idx in range(len(data['responses'])):
                    page = data['responses'][idx]  # get the next page
                    # the remainder gets the full text for the page
                    # and writes it out
                    annotation = page['fullTextAnnotation']
                    output_file_idx_str = str(page_num).zfill(3)
                    output_file_name = f"page-{output_file_idx_str}.txt"
                    output_file_path = f"processed/{slug}/{output_file_name}"
                    page_text = annotation['text']
                    full_texts.append(page_text)
                    with open(output_file_path, "w") as output_file:
                        output_file.write(page_text)
                    page_num += 1
        #  write out the document full text
        with open(f"processed/{slug}/{slug}.txt", "w") as output_file:
            output_file.write("\n".join(full_texts))


if __name__ == "__main__":
    main()
