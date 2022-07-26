# About

Uses the AWS Textract APIs DetectDocumentText/AnalyzeExpense/AnalyzeDocument to analyze an image or PDF file and store the analysis results as JSON.

https://docs.aws.amazon.com/textract/latest/dg/API_DetectDocumentText.html
https://docs.aws.amazon.com/textract/latest/dg/API_AnalyzeExpense.html
https://docs.aws.amazon.com/textract/latest/dg/API_AnalyzeDocument.html

Uses the synchronous version of this API, which does not require creating S3 files or monitoring the status of the job.

Inspired by [Simon Willison's s3-ocr](https://simonwillison.net/2022/Jun/30/s3-ocr/). I wanted something similar, but without the S3 overhead (and I could deal with the limitations of not supporting multi-page PDFs). Theoretically, this could also be done with `aws-cli`, but that doesn't support synchronous mode.

## Not Supported

Does not support AnalyzeID nor AnalyzeDocument with FeatureTypes = QUERIES.

# Installation

## pipx

My preferred method. Sets up a virtual environment, installs, and adds to your path, without touching system Python install.

https://github.com/pypa/pipx

```
pipx install git+https://github.com/mbafford/textract-cli.git
```

## pip

```
pip install git+https://github.com/mbafford/textract-cli.git
```

## pip (development)

```
python3 -mvenv .env/
git clone https://github.com/mbafford/textract-cli.git
.env/bin/pip install -e textract-cli/
```

# AWS Credentials

This uses [boto3](https://github.com/boto/boto3) for all of the API calls, so configuring the AWS credentials is the same as any other boto3 project. See [using boto3](https://github.com/boto/boto3#using-boto3) for more specifics.

# Supported File Types

- Standard image types (jpeg, png, tiff, gif, etc) should be supported
 - folder mode only checks for a handful of file extensions
 - single file mode submits a job for anything you pass, regardless of file type
- Single-page PDF is supported
- Multi-page PDF is NOT supported (only supported in asynchronous mode, in which case, [s3-ocr](https://simonwillison.net/2022/Jun/30/s3-ocr/) is likely a better choice)


# Usage

```
.env/bin/python textract.py [--text/--expenses/--forms/--tables] <folder with images/image file> [folder with images/image file] [...]
```

Accepts multile files or folders as arguments.

For each folder specified, all files with the extensions JPG, JPEG, GIF, PNG, TIFF in that folder will be selected and uploaded.

For each file specified, the script does not check filetype or extension and assumes/trusts the file can be processed by AWS.

# Resuming

The script looks for images that don't have a corresponding output file already created. 

So if the script hangs, crashes, etc - just re-run, and only files that still need to be processed will be processed.

To force a re-process, delete the relevant output files for the image file and re-run the script.

Since each analysis type creates and looks for its own JSON file, this can be run multiple times for each analysis type.

# Output

Outputs one or two files for each image file input:

## Text Analysis (GetDocumentText)
- [image file].textract.text.json - The exact JSON returned by the AWS API 
- [image file].textract.txt       - The text content for each of the "LINE" blocks in the above JSON response.

## Expenses Analysis (AnalyzeExpense)
- [image file].textract.expenses.json - The exact JSON returned by the AWS API 

## Tables Analysis (AnalyzeDocument, FeatureTypes=TABLES)
- [image file].textract.tables.json - The exact JSON returned by the AWS API 

## Forms Analysis (AnalyzeDocument, FeatureTypes=FORMS)
- [image file].textract.forms.json - The exact JSON returned by the AWS API 
 
