import json
import os


def mkdir(directory):
    try:
        os.mkdir("processed/" + directory)
    except OSError as error:
        pass


def process_pdf(pdf_file, slug):
    os.system(
        "convert -scene 1 -depth 24 -colorspace sRGB -define png:compression-filter=2 -define png:compression-level=9 -define png:compression-strategy=1 -density 150 \"{}\" processed/{}/page-%03d.png".format(
            pdf_file,
            slug
        )
    )

def main():
    with open('manifest.json', 'r') as manifest_file:
        data = manifest_file.read()

    manifest = json.loads(data)

    for item in manifest:
        slug = item['slug']
        file = item['file']
        mkdir(slug)
        print(slug)
        process_pdf(file, slug)


if __name__ == "__main__":
    main()
