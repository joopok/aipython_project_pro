#!/usr/bin/env python3
"""
Flask SECRET_KEY 생성 스크립트
"""

import secrets
import string

def generate_secret_key(length=50):
    """안전한 랜덤 SECRET_KEY 생성"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    print("=== Flask SECRET_KEY 생성기 ===")
    print()
    print("생성된 SECRET_KEY:")
    print("-" * 60)
    secret_key = generate_secret_key()
    print(secret_key)
    print("-" * 60)
    print()
    print("위의 키를 .env 파일의 SECRET_KEY= 뒤에 붙여넣으세요.")
    print("예: SECRET_KEY=" + secret_key)