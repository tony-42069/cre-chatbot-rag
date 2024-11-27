FROM python:3.10-slim

WORKDIR /home/user/app

# Install git-lfs and other dependencies
RUN apt-get update && \
    apt-get install -y git git-lfs poppler-utils && \
    rm -rf /var/lib/apt/lists/* && \
    git lfs install

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Initialize git-lfs and copy the application
COPY .gitattributes .
COPY Dataset/Commercial\ Lending\ 101.pdf Dataset/
RUN ls -la Dataset && \
    stat Dataset/Commercial\ Lending\ 101.pdf

# Copy the rest of the application
COPY . .

# Make port configurable via environment variable
ENV PORT=8501

EXPOSE ${PORT}

# Use the correct path to app.py and make port configurable
CMD ["streamlit", "run", "app.py", "--server.port=${PORT}", "--server.address=0.0.0.0"]
