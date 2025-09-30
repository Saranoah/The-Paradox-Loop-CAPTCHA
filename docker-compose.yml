version: "3.8"

services:
  paradox-captcha:
    build: ./backend
    container_name: paradox-captcha
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    depends_on:
      - redis

  redis:
    image: redis:7.0
    container_name: paradox-redis
    ports:
      - "6379:6379"

  prometheus:
    image: prom/prometheus
    container_name: paradox-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    depends_on:
      - paradox-captcha

  grafana:
    image: grafana/grafana
    container_name: paradox-grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
