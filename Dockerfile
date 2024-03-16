# syntax=docker/dockerfile:1.0
FROM golang:1.22

WORKDIR /app

COPY backend/go.mod .
RUN go mod download
COPY backend/*.go .

RUN CGO_ENABLED=0 GOOS=darwin go build -o ./server

CMD ["./server"]

EXPOSE 3000
