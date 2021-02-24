# modified from the Dockerfile provided here:
# https://levelup.gitconnected.com/complete-guide-to-create-docker-container-for-your-golang-application-80f3fb59a15e
FROM golang:alpine AS builder

ENV GO111MODULE=on \
    CGO_ENABLED=0
#GOOS=linux \
#GOARCH=amd64

WORKDIR /build

COPY . .
RUN go mod download && \
    go build -o main .

FROM scratch

COPY --from=builder /build/main /
ENTRYPOINT ["/main"]