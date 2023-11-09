#!/bin/bash
FROM python:3.9
COPY . .

RUN python3 -m pip install -r requirements.txt --no-dependencies

CMD ["python3", "__main__.py"]
