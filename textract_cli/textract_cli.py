#!.env/bin/python

from typing import List, Literal
import boto3
import sys
import os
from io import BytesIO
import json
from pathlib import Path
from tqdm import tqdm
import click
    
IMAGE_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'pdf', 'tiff'])
ANALYZE_TYPES = Literal['text', 'tables', 'forms', 'expenses']

def json_filename(filename:str, analyze_type:ANALYZE_TYPES) -> str:
    return f"{filename}.textract.{analyze_type}.json"

def txt_filename(filename:str) -> str:
    return filename + ".textract.txt"

def expand_paths(paths:List[str]) -> List[str]:
    ret = []
    for path in paths:
        if os.path.isdir(path):
            for ext in IMAGE_EXTENSIONS:
                ret += [str(p) for p in Path(path).glob("*." + ext)]

        elif os.path.isfile(path):
            ret += [ path ]
        else:
            print(f"Not a file or directory: {path} - ignoring.", file=sys.stderr)
            continue
    return ret

@click.command()
@click.option('--text',      'analyze_type', flag_value = 'text', default = True)
@click.option('--tables',    'analyze_type', flag_value = 'tables')
@click.option('--forms',     'analyze_type', flag_value = 'forms')
@click.option('--expenses',  'analyze_type', flag_value = 'expenses')
@click.argument('paths', nargs=-1, required=True, type=click.Path(exists=True))
def main(analyze_type: ANALYZE_TYPES, paths:List[str]):
    print(f"Running analysis with type: {analyze_type}", file=sys.stderr)

    client = boto3.client('textract')

    src_files = expand_paths(paths)
    needs_ocr = list(filter(lambda f: not os.path.isfile(json_filename(f, analyze_type)), src_files))

    print("Found %d image files, %d need to be OCRed" % (len(src_files), len(needs_ocr)))

    if len(needs_ocr) == 0:
        sys.exit(0)

    errors = []
    pbar = tqdm(needs_ocr)
    for file in pbar:
        pbar.set_description(file)

        try:
            with open(file, "rb") as f:
                bytes = f.read()
            
            text = None

            if analyze_type == 'text':
                response = client.detect_document_text( Document={ 'Bytes': bytes } )

                text = "\n".join([
                    b['Text'] for b in response["Blocks"] if b['BlockType'] == 'LINE'
                ])

            elif analyze_type == 'expenses':
                response = client.analyze_expense( Document={ 'Bytes': bytes } )

            elif analyze_type == 'forms':
                response = client.analyze_document( Document={ 'Bytes': bytes }, FeatureTypes=['FORMS'] )

            elif analyze_type == 'tables':
                response = client.analyze_document( Document={ 'Bytes': bytes }, FeatureTypes=['TABLES'] )

            else:
                errors.append(f"Unknown analyze_type={analyze_type}")
                break
            
            response = json.dumps(response, indent=2)
            out_json = json_filename(file, analyze_type)
            with open(out_json, "w") as out:
                out.write(response);
                out.write("\n")

            if text:
                out_txt = txt_filename(file)
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
