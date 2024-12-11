FROM python:3.13-alpine

RUN adduser -D app

WORKDIR /app

COPY ./cli/cli.py /app/cli/cli.py
COPY ./shared /app/shared
COPY ./data /app/data
COPY ./cli/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN chown -R app /app

USER app

CMD ["sh"]
