FROM python:3.10-slim

WORKDIR /home/user/app

# Install git and git-lfs
RUN apt-get update && \
    apt-get install -y git git-lfs && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Explicitly copy and verify the PDF file
COPY Dataset/Commercial\ Lending\ 101.pdf /home/user/app/Dataset/
RUN ls -l /home/user/app/Dataset/Commercial\ Lending\ 101.pdf && \
    echo "PDF file size: $(stat -f%z /home/user/app/Dataset/Commercial\ Lending\ 101.pdf) bytes"

# Make port configurable via environment variable
ENV PORT=8501

EXPOSE ${PORT}

# Use the correct path to app.py and make port configurable
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=${PORT}", "--server.address=0.0.0.0"]
