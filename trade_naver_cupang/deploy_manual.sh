#!/bin/bash

# LogiFlow 수동 배포 스크립트
# 시놀로지 NAS에 수동으로 배포하기 위한 스크립트

echo "🚀 LogiFlow 수동 배포 스크립트 시작"
echo "=================================="

# 설정 변수
PROJECT_NAME="logiflow"
LOCAL_DIR=$(pwd)
BUILD_DIR="./build"
ARCHIVE_NAME="${PROJECT_NAME}-manual-deploy.tar.gz"

# NAS 설정 (필요시 수정)
NAS_IP="192.168.0.109"
NAS_USER="joopok"
NAS_PATH="/volume1/homes/joopok/python/logiflow"

echo "📁 현재 디렉토리: $LOCAL_DIR"
echo "🏗️  빌드 디렉토리: $BUILD_DIR"

# 1. 이전 빌드 디렉토리 정리
echo "🧹 이전 빌드 파일 정리 중..."
if [ -d "$BUILD_DIR" ]; then
    rm -rf "$BUILD_DIR"
fi

if [ -f "$ARCHIVE_NAME" ]; then
    rm -f "$ARCHIVE_NAME"
fi

# 2. 빌드 디렉토리 생성
echo "📂 빌드 디렉토리 생성 중..."
mkdir -p "$BUILD_DIR"

# 3. 필요한 파일들 복사
echo "📋 필요한 파일들 복사 중..."

# Python 파일들
cp -r app/ "$BUILD_DIR/" 2>/dev/null || echo "⚠️  app/ 디렉토리가 없습니다."
cp -r database/ "$BUILD_DIR/" 2>/dev/null || echo "⚠️  database/ 디렉토리가 없습니다."
cp -r static/ "$BUILD_DIR/" 2>/dev/null || echo "✅ static/ 복사 완료"
cp -r templates/ "$BUILD_DIR/" 2>/dev/null || echo "✅ templates/ 복사 완료"

# 설정 파일들
cp *.py "$BUILD_DIR/" 2>/dev/null || echo "⚠️  Python 파일들 복사"
cp requirements.txt "$BUILD_DIR/" 2>/dev/null || echo "⚠️  requirements.txt가 없습니다."
cp .env.example "$BUILD_DIR/" 2>/dev/null || echo "⚠️  .env.example이 없습니다."

# README 및 문서
cp README.md "$BUILD_DIR/" 2>/dev/null || echo "⚠️  README.md가 없습니다."
cp CLAUDE.md "$BUILD_DIR/" 2>/dev/null || echo "✅ CLAUDE.md 복사 완료"

# 4. 제외할 파일들 정리
echo "🚫 불필요한 파일들 제거 중..."
find "$BUILD_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$BUILD_DIR" -name ".DS_Store" -delete 2>/dev/null || true
find "$BUILD_DIR" -name "*.log" -delete 2>/dev/null || true

# 5. NAS용 설정 파일 생성
echo "⚙️  NAS용 설정 파일 생성 중..."

# 5-1. NAS용 requirements.txt 생성 (mariadb 제외)
if [ -f "requirements.txt" ]; then
    echo "📦 NAS용 requirements.txt 생성 중..."
    grep -v "mariadb" requirements.txt > "$BUILD_DIR/requirements_nas.txt"
    echo "✅ requirements_nas.txt 생성 완료"
fi

# 5-2. NAS 시작 스크립트 생성
cat > "$BUILD_DIR/start_nas.sh" << 'EOF'
#!/bin/bash
# NAS에서 LogiFlow 시작하는 스크립트

echo "🚀 LogiFlow NAS 시작 중..."

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 가상환경 활성화"
fi

# 의존성 설치 (첫 실행시)
if [ ! -f ".deps_installed" ]; then
    echo "📦 의존성 설치 중..."
    pip install -r requirements_nas.txt
    touch .deps_installed
    echo "✅ 의존성 설치 완료"
fi

# 데이터베이스 초기화 (필요시)
if [ "$1" = "--init-db" ]; then
    echo "🗄️  데이터베이스 초기화 중..."
    python database/init_db.py
    echo "✅ 데이터베이스 초기화 완료"
fi

# 애플리케이션 시작
echo "🌐 LogiFlow 시작 중... (포트 7000)"
python wsgi.py

EOF

chmod +x "$BUILD_DIR/start_nas.sh"

# 5-3. NAS 종료 스크립트 생성
cat > "$BUILD_DIR/stop_nas.sh" << 'EOF'
#!/bin/bash
# NAS에서 LogiFlow 종료하는 스크립트

echo "🛑 LogiFlow 종료 중..."

# 포트 7000에서 실행 중인 프로세스 찾아서 종료
PID=$(lsof -ti:7000)
if [ ! -z "$PID" ]; then
    kill -9 $PID
    echo "✅ LogiFlow 프로세스 종료됨 (PID: $PID)"
else
    echo "⚠️  실행 중인 LogiFlow 프로세스를 찾을 수 없습니다."
fi

EOF

chmod +x "$BUILD_DIR/stop_nas.sh"

# 5-4. 환경 설정 파일 생성
cat > "$BUILD_DIR/.env.nas" << 'EOF'
# NAS용 환경 설정
FLASK_ENV=production
FLASK_DEBUG=False
PORT=7000

# 데이터베이스 설정
DB_HOST=192.168.0.109
DB_PORT=3306
DB_NAME=trade_naver_cupang
DB_USER=root
DB_PASSWORD=your_password_here

# 보안 설정
SECRET_KEY=your_secret_key_here

EOF

# 6. 배포 아카이브 생성
echo "📦 배포 아카이브 생성 중..."
cd "$BUILD_DIR"
tar -czf "../$ARCHIVE_NAME" .
cd ..

# 7. 파일 크기 확인
ARCHIVE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
echo "✅ 배포 아카이브 생성 완료: $ARCHIVE_NAME ($ARCHIVE_SIZE)"

# 8. 배포 가이드 출력
echo ""
echo "🎯 수동 배포 가이드"
echo "=================="
echo ""
echo "1. 생성된 파일을 NAS에 전송:"
echo "   scp $ARCHIVE_NAME $NAS_USER@$NAS_IP:~/"
echo ""
echo "2. NAS에 SSH 접속:"
echo "   ssh $NAS_USER@$NAS_IP"
echo ""
echo "3. NAS에서 배포 실행:"
echo "   cd $NAS_PATH"
echo "   tar -xzf ~/$ARCHIVE_NAME"
echo "   cp .env.nas .env"
echo "   # .env 파일의 DB_PASSWORD, SECRET_KEY 수정"
echo "   ./start_nas.sh --init-db"
echo ""
echo "4. 서비스 관리:"
echo "   시작: ./start_nas.sh"
echo "   종료: ./stop_nas.sh"
echo ""
echo "5. 웹 접속:"
echo "   http://$NAS_IP:7000"
echo ""
echo "📁 빌드 파일 위치: $BUILD_DIR"
echo "📦 배포 파일: $ARCHIVE_NAME"
echo ""

# 9. 자동 배포 옵션 (선택사항)
read -p "🤖 자동으로 NAS에 배포하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 자동 배포 시작..."
    
    # SCP로 파일 전송
    echo "📤 파일 전송 중..."
    scp "$ARCHIVE_NAME" "$NAS_USER@$NAS_IP:~/"
    
    if [ $? -eq 0 ]; then
        echo "✅ 파일 전송 완료"
        echo ""
        echo "🔧 NAS에서 수동으로 실행해야 할 명령어:"
        echo "ssh $NAS_USER@$NAS_IP"
        echo "cd $NAS_PATH"
        echo "tar -xzf ~/$ARCHIVE_NAME"
        echo "cp .env.nas .env"
        echo "# .env 파일 수정 후"
        echo "./start_nas.sh --init-db"
    else
        echo "❌ 파일 전송 실패"
    fi
else
    echo "📋 수동 배포 파일이 준비되었습니다."
fi

echo ""
echo "🎉 배포 스크립트 완료!"