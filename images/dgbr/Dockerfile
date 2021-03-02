FROM golang:alpine AS builder

ENV GO111MODULE=on \
    CGO_ENABLED=0

RUN go get github.com/AugustDev/dgbr

FROM alpine
RUN mkdir /etc/cron.d
COPY --from=builder /go/bin/dgbr /