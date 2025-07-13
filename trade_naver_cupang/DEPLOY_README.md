# LogiFlow NAS 수동 배포 가이드

## 개요
이 가이드는 LogiFlow를 시놀로지 NAS에 수동으로 배포하는 방법을 설명합니다.

## 배포 방법

### 방법 1: 자동 스크립트 사용 (권장)

```bash
# 터미널에서 실행
./deploy_manual.sh
```

### 방법 2: GUI 도우미 사용

```bash
# Python GUI 도우미 실행
python3 deploy_helper.py
```

### 방법 3: 완전 수동 배포

#### 3-1. 배포 파일 생성
```bash
# 프로젝트 디렉토리에서
mkdir build
cp -r app/ database/ static/ templates/ build/
cp *.py requirements.txt CLAUDE.md build/
cd build
tar -czf ../logiflow-manual-deploy.tar.gz .
cd ..
```

#### 3-2. NAS에 파일 전송
```bash
# SCP로 파일 전송
scp logiflow-manual-deploy.tar.gz joopok@192.168.0.109:~/
```

#### 3-3. NAS에서 배포
```bash
# NAS에 SSH 접속
ssh joopok@192.168.0.109

# 배포 디렉토리로 이동
cd /volume1/homes/joopok/python/logiflow

# 파일 압축 해제
tar -xzf ~/logiflow-manual-deploy.tar.gz

# 환경 설정
cp .env.nas .env
nano .env  # DB_PASSWORD, SECRET_KEY 수정

# 의존성 설치 (NAS용)
pip install -r requirements_nas.txt

# 데이터베이스 초기화 (첫 설치시만)
python database/init_db.py

# 서비스 시작
python wsgi.py
```

## NAS 설정

### 기본 설정값
- **NAS IP**: 192.168.0.109
- **사용자**: joopok
- **포트**: 7000
- **설치 경로**: `/volume1/homes/joopok/python/logiflow`

### 환경 변수 (.env 파일)
```env
FLASK_ENV=production
FLASK_DEBUG=False
PORT=7000

DB_HOST=192.168.0.109
DB_PORT=3306
DB_NAME=trade_naver_cupang
DB_USER=root
DB_PASSWORD=your_actual_password

SECRET_KEY=your_actual_secret_key
```

## 서비스 관리

### 시작/종료 스크립트
배포 후 다음 스크립트들이 생성됩니다:

```bash
# 서비스 시작
./start_nas.sh

# 데이터베이스 초기화와 함께 시작
./start_nas.sh --init-db

# 서비스 종료
./stop_nas.sh
```

### 수동 관리
```bash
# 실행 중인 프로세스 확인
lsof -i:7000

# 프로세스 종료
kill -9 $(lsof -ti:7000)

# 백그라운드 실행
nohup python wsgi.py &
```

## 접속 확인

### 웹 접속
- **내부 접속**: http://192.168.0.109:7000
- **관리자 계정**: admin / admin123

### 로그 확인
```bash
# 실시간 로그 확인
tail -f nohup.out

# 애플리케이션 로그
tail -f app.log
```

## 문제 해결

### 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :7000

# 프로세스 강제 종료
pkill -f "python wsgi.py"
```

### 권한 문제
```bash
# 실행 권한 부여
chmod +x start_nas.sh stop_nas.sh

# 디렉토리 권한 확인
ls -la /volume1/homes/joopok/python/
```

### 의존성 문제
```bash
# NAS용 requirements 사용
pip install -r requirements_nas.txt

# 개별 설치
pip install Flask Flask-SQLAlchemy Flask-Cors PyMySQL bcrypt gunicorn python-dotenv
```

## 업데이트 방법

### 소스 코드 업데이트
1. 로컬에서 새 배포 파일 생성
2. NAS 서비스 종료: `./stop_nas.sh`
3. 새 파일 전송 및 압축 해제
4. 서비스 재시작: `./start_nas.sh`

### 데이터베이스 업데이트
```bash
# 백업
mysqldump -u root -p trade_naver_cupang > backup.sql

# 스키마 업데이트
python database/init_db.py
```

## 보안 주의사항

1. **.env 파일 보안**
   - 실제 비밀번호 사용
   - 파일 권한 설정: `chmod 600 .env`

2. **방화벽 설정**
   - 필요한 포트만 개방
   - 내부 네트워크에서만 접근

3. **정기 업데이트**
   - 보안 패치 적용
   - 비밀번호 정기 변경

## 지원

문제가 발생하면 다음 정보를 포함하여 문의:
- NAS 모델 및 DSM 버전
- Python 버전
- 에러 메시지
- 실행 로그

---

📝 **주의**: 이 문서는 시놀로지 NAS 환경을 기준으로 작성되었습니다. 다른 NAS나 서버 환경에서는 경로나 명령어가 다를 수 있습니다.