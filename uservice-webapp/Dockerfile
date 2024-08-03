FROM python:3.11.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src src

ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0"]