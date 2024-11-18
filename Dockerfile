FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y bash

RUN bash ./scripts/build_dev.sh

EXPOSE 8000

CMD ["/bin/bash", "./scripts/start.sh"]
