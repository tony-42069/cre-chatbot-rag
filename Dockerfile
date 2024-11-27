FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Make port configurable via environment variable
ENV PORT=8501

EXPOSE ${PORT}

# Use the correct path to app.py and make port configurable
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=${PORT}", "--server.address=0.0.0.0"]
