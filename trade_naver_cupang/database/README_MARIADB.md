# MariaDB 설정 가이드

## 1. MariaDB 설치

### macOS
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
MariaDB 공식 사이트에서 설치 프로그램 다운로드: https://mariadb.org/download/

## 2. MariaDB 초기 설정

```bash
# 보안 설정 (root 비밀번호 설정 등)
sudo mysql_secure_installation

# MariaDB 접속
mysql -u root -p
```

## 3. 데이터베이스 및 사용자 생성

```sql
-- 데이터베이스 생성
CREATE DATABASE trade_naver_cupang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 (로컬 접속용)
CREATE USER 'trade_user'@'localhost' IDENTIFIED BY 'your_password';

-- 사용자 생성 (원격 접속용)
CREATE USER 'trade_user'@'%' IDENTIFIED BY 'your_password';

-- 권한 부여
GRANT ALL PRIVILEGES ON trade_naver_cupang.* TO 'trade_user'@'localhost';
GRANT ALL PRIVILEGES ON trade_naver_cupang.* TO 'trade_user'@'%';

-- 권한 적용
FLUSH PRIVILEGES;
```

## 4. 원격 접속 설정 (필요시)

### MariaDB 설정 파일 수정
```bash
# /etc/mysql/mariadb.conf.d/50-server.cnf 또는
# /etc/my.cnf 또는 
# /usr/local/etc/my.cnf

# bind-address 수정
bind-address = 0.0.0.0
```

### 방화벽 설정
```bash
# Ubuntu/Debian
sudo ufw allow 3306

# CentOS/RHEL
sudo firewall-cmd --add-port=3306/tcp --permanent
sudo firewall-cmd --reload
```

## 5. 애플리케이션 설정

### .env 파일 설정
```bash
# 기존 설정
DB_HOST=192.168.0.109
DB_PORT=3306
DB_USER=root
DB_PASSWORD=~Asy10131227
DB_NAME=trade_naver_cupang
```

### 데이터베이스 초기화
```bash
# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 데이터베이스 초기화
python database/init_db.py
```

## 6. 연결 테스트

```bash
# 연결 테스트
python database/test_connection.py
```

## 7. 문제 해결

### 연결 오류 발생시
1. MariaDB 서비스 실행 확인
   ```bash
   sudo systemctl status mariadb  # Linux
   brew services list  # macOS
   ```

2. 포트 확인
   ```bash
   sudo netstat -tlnp | grep 3306  # Linux
   lsof -i :3306  # macOS
   ```

3. 사용자 권한 확인
   ```sql
   SELECT user, host FROM mysql.user;
   SHOW GRANTS FOR 'trade_user'@'localhost';
   ```

### 한글 깨짐 문제
```sql
-- 데이터베이스 문자셋 확인
SHOW VARIABLES LIKE 'character%';

-- 테이블 문자셋 변경 (필요시)
ALTER TABLE table_name CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 8. 백업 및 복구

### 백업
```bash
mysqldump -u root -p trade_naver_cupang > backup_$(date +%Y%m%d).sql
```

### 복구
```bash
mysql -u root -p trade_naver_cupang < backup_20240101.sql
```