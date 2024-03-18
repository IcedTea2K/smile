# syntax=docker/dockerfile:1.0
FROM golang:1.22

WORKDIR /app/server

COPY go.mod go.sum* ./
RUN go mod download
COPY *.go .

RUN CGO_ENABLED=0 GOOS=linux go build -o ./bin/server
RUN ln -s /run/secrets/rootCA /usr/local/share/ca-certificates/rootCA.crt

CMD ["./bin/server"]
