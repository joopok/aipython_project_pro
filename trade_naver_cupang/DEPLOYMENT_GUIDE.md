# LogiFlow 배포 가이드

이 가이드는 LogiFlow 애플리케이션을 Synology NAS에 배포하는 모든 방법을 포함합니다.

## 목차

1. [개요](#1-개요)
2. [사전 준비](#2-사전-준비)
3. [환경 설정](#3-환경-설정)
4. [배포 방법](#4-배포-방법)
5. [외부 접속 설정](#5-외부-접속-설정)
6. [서비스 관리](#6-서비스-관리)
7. [모니터링 및 로그](#7-모니터링-및-로그)
8. [보안](#8-보안)
9. [문제 해결](#9-문제-해결)
10. [유지보수](#10-유지보수)

## 1. 개요

### 환경별 설정
- **개발 환경**: 포트 5001
- **운영 환경**: 포트 7000
- **배포 서버**: Synology NAS (DSM 7.0+)
- **데이터베이스**: MariaDB 10

### 배포 방법
1. **자동화 배포**: 스크립트를 통한 자동 배포
2. **수동 배포**: 단계별 수동 배포

## 2. 사전 준비

### NAS 환경 준비

```bash
# SSH 접속
ssh -p 22 joopok@192.168.0.109

# Python 3.9 설치 확인
python3 --version

# pip 설치
sudo python3 -m ensurepip

# 필수 패키지 설치
sudo pip3 install virtualenv
```

### 데이터베이스 준비

```bash
# MariaDB 접속
mysql -u root -p

# 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS trade_naver_cupang 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

# 권한 설정
GRANT ALL PRIVILEGES ON trade_naver_cupang.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

### 로컬 환경 준비

```bash
# 프로젝트 복사
cp -r /path/to/local/project /tmp/logiflow-deploy

# 불필요한 파일 제거
cd /tmp/logiflow-deploy
rm -rf __pycache__ *.pyc .DS_Store
rm -rf venv env .venv
```

## 3. 환경 설정

### 설정 파일 구조

```
trade_naver_cupang/
├── .env                    # 개발 환경 설정
├── .env.production        # 운영 환경 설정
├── deploy_config.json     # 배포 설정
└── synology_startup.sh    # 자동 시작 스크립트
```

### deploy_config.json

```json
{
    "nas": {
        "host": "192.168.0.109",
        "port": 22,
        "user": "joopok",
        "deploy_path": "/volume1/homes/joopok/python/logiflow"
    },
    "app": {
        "name": "logiflow",
        "port": 7000,
        "workers": 4
    },
    "environments": {
        "development": {
            "port": 5001,
            "debug": true,
            "workers": 2
        },
        "production": {
            "port": 7000,
            "debug": false,
            "workers": 4
        }
    },
    "files": {
        "archive_name": "logiflow-deploy.tar.gz",
        "exclude_patterns": [
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            "venv/",
            "env/",
            ".env",
            "*.log"
        ]
    }
}
```

### .env.production

```bash
# Flask 설정
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-here

# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-secure-password
DB_NAME=trade_naver_cupang

# 마켓플레이스 API (선택사항)
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret
COUPANG_ACCESS_KEY=your-coupang-access-key
COUPANG_SECRET_KEY=your-coupang-secret-key

# 앱 설정
APP_HOST=0.0.0.0
APP_PORT=7000
```

## 4. 배포 방법

### 4.1 자동화 배포 (권장)

#### 자동 배포 스크립트 사용

```bash
# deploy_synology_auto.sh 실행
./deploy_synology_auto.sh

# 환경 선택 프롬프트에서 선택
# 1) development (포트 5001)
# 2) production (포트 7000)
```

#### 스크립트 동작 과정

1. **설정 파일 로드**: deploy_config.json 읽기
2. **아카이브 생성**: 프로젝트 파일 압축
3. **파일 전송**: SCP로 NAS에 전송
4. **기존 서비스 중지**: 실행 중인 프로세스 종료
5. **파일 압축 해제**: 배포 경로에 압축 해제
6. **가상환경 설정**: venv 생성 및 패키지 설치
7. **데이터베이스 초기화**: 스키마 적용
8. **서비스 시작**: Gunicorn으로 앱 실행
9. **상태 확인**: 서비스 정상 동작 확인

### 4.2 수동 배포

```bash
# 1. 프로젝트 압축
tar -czf logiflow-deploy.tar.gz \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.env' \
    .

# 2. NAS로 전송
scp -P 22 logiflow-deploy.tar.gz joopok@192.168.0.109:/volume1/homes/joopok/python/

# 3. NAS 접속
ssh -p 22 joopok@192.168.0.109

# 4. 기존 서비스 중지
kill -9 $(lsof -ti:7000)

# 5. 배포 디렉토리 생성 및 압축 해제
cd /volume1/homes/joopok/python
mkdir -p logiflow
cd logiflow
tar -xzf ../logiflow-deploy.tar.gz

# 6. 가상환경 설정
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. 환경 파일 설정
cp .env.production .env

# 8. 데이터베이스 초기화
python database/init_db.py
python database/create_admin_user.py

# 9. 서비스 시작
gunicorn -w 4 -b 0.0.0.0:7000 --daemon wsgi:app
```

## 5. 외부 접속 설정

### 옵션 1: QuickConnect (간편)

1. DSM 제어판 → QuickConnect 활성화
2. QuickConnect ID 설정
3. 접속 URL: `https://your-id.quickconnect.to:7000`

### 옵션 2: 포트 포워딩

```bash
# 공유기 설정에서 포트 포워딩
외부 포트 7000 → 내부 192.168.0.109:7000

# 방화벽 규칙 추가 (DSM)
제어판 → 보안 → 방화벽 → 규칙 추가
- 포트: 7000
- 프로토콜: TCP
- 소스 IP: 모두 허용 (또는 특정 IP)
```

### 옵션 3: 리버스 프록시 (권장)

DSM 제어판 → 응용 프로그램 포털 → 역방향 프록시:

```
소스:
- 프로토콜: HTTPS
- 호스트명: logiflow.yourdomain.com
- 포트: 443

대상:
- 프로토콜: HTTP
- 호스트명: localhost
- 포트: 7000
```

## 6. 서비스 관리

### 서비스 시작/중지

```bash
# 서비스 시작
cd /volume1/homes/joopok/python/logiflow
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:7000 --daemon wsgi:app

# 서비스 중지
kill -9 $(lsof -ti:7000)

# 서비스 재시작
kill -9 $(lsof -ti:7000)
sleep 2
gunicorn -w 4 -b 0.0.0.0:7000 --daemon wsgi:app
```

### 자동 시작 설정

```bash
# synology_startup.sh 생성
cat > /volume1/homes/joopok/python/logiflow/synology_startup.sh << 'EOF'
#!/bin/bash
cd /volume1/homes/joopok/python/logiflow
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:7000 --daemon wsgi:app
EOF

chmod +x synology_startup.sh

# DSM 작업 스케줄러에 추가
# 제어판 → 작업 스케줄러 → 생성 → 부팅 시 실행
```

### 상태 확인

```bash
# 프로세스 확인
ps aux | grep gunicorn

# 포트 확인
lsof -i :7000

# 헬스 체크
curl http://localhost:7000/health
```

## 7. 모니터링 및 로그

### 모니터링 메뉴 사용

```bash
# 대화형 모니터링 메뉴
./deploy_monitor.sh

# 메뉴 옵션:
# 1) 서비스 상태 확인
# 2) 실시간 로그 보기
# 3) 에러 로그 확인
# 4) CPU/메모리 사용량
# 5) 서비스 재시작
# 6) 로그 다운로드
```

### 로그 위치

```bash
# 애플리케이션 로그
/volume1/homes/joopok/python/logiflow/logs/app.log

# Gunicorn 액세스 로그
/volume1/homes/joopok/python/logiflow/logs/access.log

# Gunicorn 에러 로그
/volume1/homes/joopok/python/logiflow/logs/error.log

# 실시간 로그 확인
tail -f logs/app.log
tail -f logs/error.log
```

### 성능 모니터링

```bash
# CPU 사용률
top -p $(pgrep -f gunicorn | tr '\n' ',' | sed 's/,$//')

# 메모리 사용량
ps aux | grep gunicorn | awk '{sum+=$6} END {print "Total Memory: " sum/1024 " MB"}'

# 네트워크 연결
netstat -an | grep :7000

# 디스크 사용량
df -h /volume1/homes/joopok/python/logiflow
```

## 8. 보안

### 운영 환경 보안 체크리스트

- [ ] SECRET_KEY 변경 (최소 32자 이상)
- [ ] 데이터베이스 비밀번호 변경
- [ ] DEBUG 모드 비활성화
- [ ] 방화벽 규칙 설정
- [ ] HTTPS 적용
- [ ] 정기적인 보안 업데이트
- [ ] 로그 파일 권한 설정 (644)
- [ ] 민감한 정보 환경 변수로 관리

### HTTPS 설정

```bash
# Let's Encrypt 인증서 발급 (DSM)
제어판 → 보안 → 인증서 → 추가 → Let's Encrypt 인증서 가져오기

# 리버스 프록시에서 HTTPS 강제
소스 프로토콜: HTTPS
HSTS 활성화
HTTP/2 활성화
```

### 권한 설정

```bash
# 파일 권한
chmod 644 .env.production
chmod 755 synology_startup.sh
chmod -R 755 static/
chmod -R 644 logs/

# 소유자 설정
chown -R joopok:users /volume1/homes/joopok/python/logiflow
```

## 9. 문제 해결

### 일반적인 문제

#### 포트 충돌
```bash
# 포트 사용 확인
lsof -i :7000

# 프로세스 강제 종료
kill -9 $(lsof -ti:7000)
```

#### 데이터베이스 연결 실패
```bash
# MariaDB 서비스 확인
systemctl status mariadb

# 연결 테스트
mysql -h localhost -u root -p -e "SELECT 1"

# 권한 확인
mysql -u root -p -e "SHOW GRANTS FOR 'root'@'localhost'"
```

#### 가상환경 문제
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 디버그 명령어

```bash
# Flask 앱 직접 실행 (디버그용)
python app.py

# Gunicorn 포그라운드 실행
gunicorn -w 4 -b 0.0.0.0:7000 --log-level debug wsgi:app

# 환경 변수 확인
python -c "import os; print(os.getenv('DB_HOST'))"
```

## 10. 유지보수

### 백업 전략

```bash
# 일일 백업 스크립트
#!/bin/bash
BACKUP_DIR="/volume1/backup/logiflow"
DATE=$(date +%Y%m%d)

# 데이터베이스 백업
mysqldump -u root -p trade_naver_cupang > $BACKUP_DIR/db_$DATE.sql

# 애플리케이션 백업
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /volume1/homes/joopok/python/logiflow

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 업데이트 절차

```bash
# 1. 백업
./backup.sh

# 2. 서비스 중지
kill -9 $(lsof -ti:7000)

# 3. 코드 업데이트
git pull origin main  # 또는 새 배포 파일 전송

# 4. 의존성 업데이트
source venv/bin/activate
pip install -r requirements.txt

# 5. 데이터베이스 마이그레이션
python database/migrate.py  # 필요한 경우

# 6. 서비스 재시작
gunicorn -w 4 -b 0.0.0.0:7000 --daemon wsgi:app

# 7. 상태 확인
curl http://localhost:7000/health
```

### 성능 최적화

```bash
# Gunicorn 워커 수 조정
# CPU 코어 수 * 2 + 1
WORKERS=$(($(nproc) * 2 + 1))

# 메모리 제한 설정
--max-requests 1000
--max-requests-jitter 50

# 타임아웃 설정
--timeout 30
--graceful-timeout 30
```

### 정기 유지보수

#### 일일
- 로그 파일 확인
- 디스크 사용량 확인
- 서비스 상태 확인

#### 주간
- 보안 업데이트 확인
- 백업 파일 정리
- 성능 메트릭 검토

#### 월간
- 전체 시스템 백업
- 로그 아카이브
- 의존성 업데이트
- 보안 감사

## 부록

### 유용한 스크립트

#### health_check.sh
```bash
#!/bin/bash
URL="http://localhost:7000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ 서비스 정상"
else
    echo "❌ 서비스 오류 (HTTP $RESPONSE)"
    # 알림 또는 재시작 로직
fi
```

#### log_rotate.sh
```bash
#!/bin/bash
LOG_DIR="/volume1/homes/joopok/python/logiflow/logs"
DATE=$(date +%Y%m%d)

# 로그 회전
mv $LOG_DIR/app.log $LOG_DIR/app_$DATE.log
mv $LOG_DIR/access.log $LOG_DIR/access_$DATE.log
mv $LOG_DIR/error.log $LOG_DIR/error_$DATE.log

# 서비스 재시작하여 새 로그 파일 생성
kill -USR1 $(pgrep -f "gunicorn.*master")

# 30일 이상 된 로그 삭제
find $LOG_DIR -name "*.log" -mtime +30 -delete
```

### 연락처 및 지원

- 프로젝트 저장소: [GitHub Repository URL]
- 이슈 트래커: [Issue Tracker URL]
- 문서: [Documentation URL]

---

마지막 업데이트: 2024-01-01