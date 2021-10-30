import json
import os


def mkdir(directory):
    try:
        os.mkdir("processed/" + directory)
    except OSError as error:
        pass


def process_pdf(pdf_file, slug):
    os.system(
        "pdfimages -all -p \"{}\" processed/{}/page".format(
            pdf_file,
            slug
        )
    )


if __name__ == "__main__":
    with open('manifest.json', 'r') as manifest_file:
        data = manifest_file.read()

    manifest = json.loads(data)

    for item in manifest:
        slug = item['slug']
        file = item['file']
        mkdir(slug)
        process_pdf(file, slug)