FROM debian:stable-slim

ENV SPOT_USERNAME ""
ENV SPOT_PASSWORD ""

RUN apt update && \
    apt install snapserver build-essential libasound2-dev portaudio19-dev cargo git curl -y && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y && \
    git clone https://github.com/librespot-org/librespot.git /tmp/librespot
ENV PATH="/opt/librespot:/root/.cargo/bin:${PATH}"
ENV CARGO_TARGET_DIR /build
ENV CARGO_HOME /build/cache
RUN cd /tmp/librespot && \
    cargo build --release --no-default-features --features alsa-backend && \
    mkdir -p /opt/librespot/ && \
    mv /build/release/* /opt/librespot/ && \
    mkdir -p /root/.config/snapserver && \
    echo "{}" > /root/.config/snapserver/server.json && \
    echo "{}" > /var/lib/snapserver/server.json && \
    rm -rf /tmp/librespot && \
    rm -rf /build
COPY run.sh /usr/bin
CMD /usr/bin/run.sh