FROM debian:stable-slim

RUN apt update && \
    apt install build-essential libasound2-dev portaudio19-dev cargo git curl -y && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y && \
    git clone https://github.com/librespot-org/librespot.git /tmp/librespot
ENV PATH="/opt/librespot:/root/.cargo/bin:${PATH}"
ENV CARGO_TARGET_DIR /build
ENV CARGO_HOME /build/cache
RUN cd /tmp/librespot && \
    cargo build --release --no-default-features --features alsa-backend

FROM debian:stable-slim

ENV SPOT_USERNAME ""
ENV SPOT_PASSWORD ""

COPY run.sh /usr/bin

RUN mkdir -p /opt/librespot/ && \
    apt update && \
    apt install snapserver -y && \
    mkdir -p /root/.config/snapserver && \
    echo "{}" > /root/.config/snapserver/server.json && \
    echo "{}" > /var/lib/snapserver/server.json  && \
    chmod +x /usr/bin/run.sh

COPY --from=0 /build/release/* /opt/librespot/

CMD /usr/bin/run.sh