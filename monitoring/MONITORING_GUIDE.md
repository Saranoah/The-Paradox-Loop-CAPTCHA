# Monitoring Setup Guide

This guide explains how to set up **Prometheus**, **Grafana**, and **log aggregation** to monitor the `paradox-captcha` service.

---

## 1. Prometheus Configuration

Prometheus scrapes metrics exposed by the Flask app at `/metrics`.

### prometheus.yml
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'paradox-captcha'
    static_configs:
      - targets: ['captcha:8000']

docker run -d --name prometheus -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

Visit Prometheus UI at http://localhost:9090
.
