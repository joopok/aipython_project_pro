# 데이터베이스 설정 가이드

## 1. MariaDB 설치

### macOS (Homebrew)
```bash
brew install mariadb
brew services start mariadb
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install mariadb-server mariadb-client
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

### Windows
1. [MariaDB 공식 사이트](https://mariadb.org/download/)에서 설치 파일 다운로드
2. 설치 마법사를 따라 설치

## 2. MariaDB 초기 설정

```bash
# 보안 설정 (root 비밀번호 설정 등)
sudo mysql_secure_installation

# MariaDB 접속
mysql -u root -p
```

## 3. 데이터베이스 사용자 생성 (선택사항)

```sql
-- 새 사용자 생성
CREATE USER 'logiflow'@'localhost' IDENTIFIED BY 'your_password';

-- 권한 부여
GRANT ALL PRIVILEGES ON trade_naver_cupang.* TO 'logiflow'@'localhost';

-- 권한 적용
FLUSH PRIVILEGES;
```

## 4. 환경 설정

1. `.env.example` 파일을 `.env`로 복사:
```bash
cp .env.example .env
```

2. `.env` 파일에서 데이터베이스 정보 수정:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root  # 또는 생성한 사용자명
DB_PASSWORD=your_password_here  # 실제 비밀번호로 변경
DB_NAME=trade_naver_cupang
```

## 5. 데이터베이스 초기화

### 방법 1: Python 스크립트 사용
```bash
python database/init_db.py
```

### 방법 2: SQL 파일 직접 실행
```bash
mysql -u root -p < database/schema.sql
```

## 6. 연결 테스트

```bash
python database/test_connection.py
```

## 데이터베이스 구조

### 주요 테이블

1. **users** - 사용자 정보
2. **platforms** - 플랫폼 정보 (네이버, 쿠팡 등)
3. **products** - 상품 정보
4. **customers** - 고객 정보
5. **orders** - 주문 정보
6. **order_items** - 주문 상세
7. **shipments** - 배송 추적
8. **inventory** - 재고 관리
9. **inventory_transactions** - 재고 거래 내역
10. **settlements** - 정산 정보
11. **settlement_details** - 정산 상세
12. **api_logs** - API 로그
13. **system_settings** - 시스템 설정

## 문제 해결

### 연결 오류
- MariaDB 서비스가 실행 중인지 확인
- 포트가 올바른지 확인 (기본: 3306)
- 방화벽 설정 확인

### 권한 오류
- 사용자 권한 확인
- 비밀번호가 올바른지 확인

### 한글 깨짐
- 데이터베이스 문자셋이 `utf8mb4`로 설정되어 있는지 확인
- 연결 시 `charset='utf8mb4'` 옵션 사용