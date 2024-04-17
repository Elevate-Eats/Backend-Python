FROM python:3.11-alpine

WORKDIR /usr/src/reportGenerator-api

COPY . .

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev cargo rust && \
    pip install --no-cache-dir -r req.txt && \
    apk --purge del .build-deps

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "main:app"]