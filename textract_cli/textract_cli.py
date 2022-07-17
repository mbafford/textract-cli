#!.env/bin/python

import boto3
import sys
import os
from io import BytesIO
import json
from pathlib import Path
from tqdm import tqdm

def json_filename(filename):
    return filename + ".textract.json"

def txt_filename(filename):
    return filename + ".textract.txt"

def main():
    client = boto3.client('textract')

    extensions = set(['jpeg', 'jpg', 'png', 'pdf', 'tiff'])

    if len(sys.argv) == 1:
        print(f"Usage: {sys.argv[0]} [files or globs]")
        print("")
        print(f"If a folder is provided, files with extensions of: [{' '.join(extensions)}] will be considered.")
        print("If a file is provided, then that file will be submitted, regardless of file type.")
        sys.exit(1)

    os.environ["AWS_PROFILE"] = 'mbafford'

    files = []
    for path in sys.argv[1:]:
        if os.path.isdir(path):
            for ext in extensions:
                files += [str(p) for p in Path(path).glob("*." + ext)]

        elif os.path.isfile(path):
            files += [ path ]
        else:
            print("Not a file or directory: {path} - ignoring.")
            continue

    needs_ocr = list(filter(lambda f: not os.path.isfile(json_filename(f)), files))

    print("Found %d image files, %d need to be OCRed" % (len(files), len(needs_ocr)))

    if len(needs_ocr) == 0:
        sys.exit(0)

    errors = []
    pbar = tqdm(needs_ocr)
    for file in pbar:
        pbar.set_description(file)

        try:
            with open(file, "rb") as f:
                bytes = f.read()

            response = client.detect_document_text(
                Document={
                    'Bytes': bytes
                }
            )

            text = "\n".join([
                b['Text'] for b in response["Blocks"] if b['BlockType'] == 'LINE'
            ])

            response = json.dumps(response, indent=2)

            out_json = json_filename(file)
            out_txt  = txt_filename(file)
            with open(out_json, "w") as out:
                out.write(response);
                out.write("\n")
            with open(out_txt, "w") as out:
                out.write(text);
                out.write("\n");
        except Exception as ex:
            errors.append(f"{file}: {str(ex)}")

    if errors:
        print("Completed with %d errors." % len(errors))
        for err in errors:
            print("    " + err);
    else:
        print("Processed %d files successfully." % len(needs_ocr))

if __name__ == "__main__":
    main()
