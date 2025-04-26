FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install flash-attn --no-build-isolation

RUN mkdir -p /app/data /app/downloads /app/logs

COPY . .

EXPOSE 8506

CMD ["streamlit", "run", "AGentV.py", "--server.address=0.0.0.0", "--server.port=8506"]