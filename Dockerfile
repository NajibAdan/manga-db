FROM python:3.13.1-slim

WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     software-properties-common \
#     && rm -rf /var/lib/apt/lists/*

COPY .env /app/

COPY src/streamlit/* /app/

COPY data/* /app/data/

COPY pyproject.toml /app/pyproject.toml

EXPOSE 8501

RUN pip install .

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

RUN python add_analytics.py

ENTRYPOINT ["streamlit", "run", "entrypoint.py", "--server.port=8501", "--server.address=0.0.0.0"]