import os

import json
import sys

from dataclasses import dataclass

from google.cloud import vision
from google.cloud import storage


@dataclass
class Item:
    file: str
    slug: str
    source_path: str
    dest_path: str


def mkdir(directory):
    try:
        os.mkdir("processed/" + directory)
    except OSError:
        pass


def load_items(source_path, dest_path) -> list:
    result = []

    with open('manifest.json', 'r') as manifest_file:
        data = manifest_file.read()

    for item in json.loads(data):
        result.append(
            Item(
                file=item['file'],
                slug=item['slug'],
                source_path="{}/{}.pdf".format(source_path, item['slug']),
                dest_path="{}/{}/".format(dest_path, item['slug'])
            )
        )

    return result


def upload_items(items, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for item in items:
        print(f"Uploading {item.slug}")
        blob = bucket.blob(item.source_path)
        blob.upload_from_filename(item.file, content_type="application/pdf")


def process_files(items, bucket_name):
    mime_type = 'application/pdf'
    client = vision.ImageAnnotatorClient()
    feature = vision.Feature(type_= vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    requests = []

    for item in items:
        source_url = f"gs://{bucket_name}/{item.source_path}"
        dest_url = f"gs://{bucket_name}/{item.dest_path}"
        gcs_source = vision.GcsSource(uri=source_url)
        input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)
        gcs_destination = vision.GcsDestination(uri=dest_url)
        output_config = vision.OutputConfig(gcs_destination=gcs_destination)
        async_request = vision.AsyncAnnotateFileRequest(
            features=[feature],
            input_config=input_config,
            output_config=output_config
        )
        requests.append(async_request)

    operation = client.async_batch_annotate_files(requests=requests)
    operation.result(timeout=1000)


def download_items(items, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for item in items:
        print(f"Downloading {item.slug}")
        output_dir = f"processed/{item.slug}/"
        for blob in list(bucket.list_blobs(prefix=item.dest_path)):
            blob_file_name = blob.name.replace(item.dest_path, "")
            blob_download_path = f"{output_dir}/{blob_file_name}"
            json_string = blob.download_as_string()
            with open(blob_download_path, "wb") as output:
                output.write(json_string)


def main(args):
    bucket_name = args[1]
    source_path = args[2]
    dest_path = args[3]
    items = load_items(source_path, dest_path)
    upload_items(items, bucket_name)
    process_files(items, bucket_name)
    download_items(items, bucket_name)


if __name__ == "__main__":
    main(sys.argv)
