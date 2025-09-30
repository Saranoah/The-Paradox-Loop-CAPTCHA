# CAPTCHA Customization Guide

This guide explains how to customize the Paradox CAPTCHA system for different projects.

## Areas you can customize
- **Challenge types** (`backend/src/captcha/`)
- **Frontend design** (`frontend/`)
- **Security rules** (`backend/src/security/`)
- **Monitoring** (`monitoring/`)

## Steps
1. Modify challenge factories to add or remove CAPTCHA types.
2. Update frontend templates to match your brand.
3. Adjust configuration values in `config.py`.
4. Restart Docker containers for changes to take effect.
