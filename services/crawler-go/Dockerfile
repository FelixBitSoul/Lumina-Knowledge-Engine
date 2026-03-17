# Crawler Go Dockerfile
# Multi-stage build for Go crawler service

# Build stage
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Install git for fetching dependencies
RUN apk add --no-cache git

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o crawler ./cmd/crawler

# Production stage
FROM alpine:latest

WORKDIR /app

# Install ca-certificates for HTTPS requests
RUN apk --no-cache add ca-certificates curl

# Create directories
RUN mkdir -p /app/config /app/logs

# Copy binary from builder
COPY --from=builder /app/crawler .

# Set environment variables
ENV LOG_LEVEL=info
ENV CRAWLER_CONFIG=/app/config/crawler-config.yaml

# Expose no ports (crawler doesn't expose HTTP)

# Health check (check if process is running)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep crawler || exit 1

# Run the crawler
CMD ["./crawler"]
