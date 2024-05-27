ARG BUILD_FROM=ghcr.io/hassio-addons/base:9.1.3
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install dependencies
RUN apk add --no-cache python3 py3-pip

# Copy data
COPY run.sh /
COPY veolia_client.py /

# Set execute permission
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
