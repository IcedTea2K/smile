# syntax=docker/dockerfile:1.0
FROM golang:1.22

WORKDIR /app/load_balancer

COPY go.mod .
RUN go mod download
COPY *.go .

RUN CGO_ENABLED=0 GOOS=linux go build -o ./bin/balancer

CMD ["./bin/balancer"]

EXPOSE 8000
