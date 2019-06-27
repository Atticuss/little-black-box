FROM golang:1.12-stretch

RUN apt update && \
go get -u -d github.com/magefile/mage && \
cd /go/src/github.com/magefile/mage && \
go run bootstrap.go 

# stupid hack because "go get" returns non-zero even when successful
RUN go get github.com/elastic/beats; exit 0

# note that arm64 doesn't work as filebeat leverages golang's Dup2
# which isn't supported on arm64. i could patch this, but i'm lazy.
# 32-bit should be good enough for a simple log file monitor.
RUN cd /go/src/github.com/elastic/beats/filebeat && \
git checkout 6.7 && \
GOARCH=arm go build && \
cp filebeat /usr/local/bin && \
touch /etc/filebeat/filebeat.yml && \
chmod go-w /etc/filebeat/filebeat.yml

ENTRYPOINT filebeat -c /etc/filebeat/filebeat.yml