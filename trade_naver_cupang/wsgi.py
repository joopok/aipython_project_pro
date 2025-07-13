#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
import sys

# 프로젝트 경로를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Production 환경으로 애플리케이션 생성
app = create_app('production')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7000)