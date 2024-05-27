ARG BUILD_FROM=ghcr.io/hassio-addons/base:9.1.3
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    libffi-dev

# Install Python packages
RUN pip install --no-cache-dir requests xmltodict

# Copy data
COPY run.sh /run.sh
COPY veolia_client.py /veolia_client.py

# Set execute permission
RUN chmod +x /run.sh

# Run script
CMD [ "/run.sh" ]
