FROM python:3.10-bullseye

WORKDIR /workspace

COPY .env ./.env

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    lsb-release \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir -U \
    google-generativeai \
    yaml

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY . .

RUN if [ -f .env ]; then export $(cat .env | xargs) && \
    echo "Loading .env"; fi

CMD ["/bin/bash"]