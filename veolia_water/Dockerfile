ARG BUILD_FROM=ghcr.io/hassio-addons/base:9.1.3
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install dependencies
RUN apk add --no-cache python3 py3-pip

# Copy data
COPY run.sh /etc/services.d/veolia/run
COPY veolia_client.py /etc/services.d/veolia/

# Set execute permission
RUN chmod +x /etc/services.d/veolia/run

# Ensure the script runs as PID 1
CMD [ "/init" ]
