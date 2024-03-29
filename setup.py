#!/usr/bin/env python

from distutils.core import setup

setup(name='textract-cli',
      version='1.1',
      description='CLI utility for using AWS Textract DetectDocumentText or AWS Rekognition DetectText to OCR image files in synchronous mode without uploading to S3.',
      author='Matthew Bafford',
      author_email='matthew@bafford.us',
      url='https://github.com/mbafford/textract-cli',
      install_requires=[
          'boto3==1.24.31', 
          'tqdm==4.64.0',
          'click==8.1.3'
      ],
      entry_points = {
        'console_scripts': ['textract-cli=textract_cli.textract_cli:main'],
      }
)
