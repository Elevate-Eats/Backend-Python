FROM python:3.11-alpine

WORKDIR /usr/src/reportGenerator-api

COPY . .

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev cargo rust cmake && \
    pip install --no-cache-dir -r req.txt && \
    apk --purge del .build-deps

EXPOSE 8080

CMD ["uvicorn", "--host", "0.0.0.0","--port","8080", "main:app"]