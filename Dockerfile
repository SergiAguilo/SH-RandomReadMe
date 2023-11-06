FROM --platform=linux/amd64 python:3.9
COPY . .

CMD ["python3", "__main__.py"]
