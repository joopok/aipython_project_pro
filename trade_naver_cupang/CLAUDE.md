# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LogiFlow - Korean E-commerce Logistics Management System
- Integrates with Naver Commerce and Coupang marketplaces
- Flask web application with MariaDB backend
- Handles order management, inventory tracking, and settlement processing

## Development Commands

### Running the Application
```bash
# Development server (port 5001)
python app.py

# Production server (port 7000)
python wsgi.py

# Kill existing process on port if needed
kill -9 $(lsof -ti:5001)  # Development
kill -9 $(lsof -ti:7000)  # Production
```

### Database Setup
```bash
# Initialize database
python database/init_db.py

# Test database connection
python database/test_connection.py

# Create admin user
python database/create_admin_user.py

# Check admin user credentials
python database/check_admin_user.py

# Reset admin password
python database/reset_admin_password.py
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Core dependencies without mariadb package (which requires system libraries):
pip install Flask Flask-SQLAlchemy Flask-Cors PyMySQL bcrypt gunicorn python-dotenv

# For Synology NAS deployment (skip mariadb package):
grep -v "mariadb" requirements.txt > requirements_no_mariadb.txt
pip install -r requirements_no_mariadb.txt
```

### Testing
```bash
# Run tests
pytest

# Run specific test
pytest test_app.py
```

## Architecture Overview

### Application Structure
```
trade_naver_cupang/
├── app/                      # Flask application package
│   ├── __init__.py          # App factory, extension initialization
│   ├── models/              # SQLAlchemy models (Product, SearchHistory, User)
│   ├── routes/              # Blueprint routes
│   │   ├── main.py         # Main routes (login, dashboard, orders, tracking, users)
│   │   └── api.py          # API endpoints
│   ├── services/            # Business logic
│   │   └── scraper.py      # Naver/Coupang scraping (currently disabled)
│   └── utils/               # Utilities
│       └── auth.py         # Password hashing/verification
├── database/                # Database layer
│   ├── models/             # Database models (separate from app models)
│   ├── db_config.py        # Database configuration
│   └── init_db.py          # Schema initialization
├── static/                  # Static assets
│   ├── css/
│   │   ├── common_sidebar.css  # Shared sidebar styles
│   │   └── [page].css          # Page-specific styles
│   └── js/
│       ├── common_sidebar.js   # Sidebar menu functionality
│       └── theme_toggle.js     # Dark mode toggle
├── templates/               # Jinja2 templates
│   └── includes/           # Reusable components
│       ├── sidebar.html    # Navigation sidebar
│       └── header.html     # Page header
├── config.py               # Application configuration
├── wsgi.py                 # WSGI entry point for production
├── deploy_manual.sh        # Manual NAS deployment script
└── logiflow-nas-deploy.tar.gz  # Ready-to-deploy package
```

### Key Design Patterns

1. **Blueprint Architecture**: Routes organized into blueprints (main, api)
2. **Template Inheritance**: Using Jinja2 includes for reusable components
3. **CSS Organization**: Common styles extracted to shared files, page-specific styles separate
4. **Session-based Authentication**: Using Flask sessions for user authentication
5. **Dual Model System**: App models (SQLAlchemy) and database models (separate ORM)

## Design System & UI Guidelines

### Visual Design Principles

1. **Modern & Clean**: Minimalist approach with generous whitespace
2. **Professional**: Business-oriented interface suitable for logistics management
3. **Korean-First**: All UI text in Korean, optimized for Korean typography
4. **Responsive**: Mobile-friendly design with collapsible sidebar

### Color Palette

```css
/* Primary Colors */
--primary-color: #6a61ed;  /* Purple gradient base */
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Status Colors */
--success: #22c55e;  /* Green - active, completed */
--warning: #f59e0b;  /* Orange - pending */
--danger: #ef4444;   /* Red - error, delete */
--info: #6366f1;     /* Blue - information */

/* Neutral Colors */
--text-primary: #1a202c;   /* Main text */
--text-secondary: #718096; /* Secondary text */
--border-color: #e2e8f0;   /* Borders */
--bg-primary: #ffffff;     /* Main background */
--bg-secondary: #f7fafc;   /* Secondary background */

/* Dark Mode */
--dark-bg: #1a202c;
--dark-surface: #2d3748;
--dark-border: #4a5568;
```

### Typography

- **Font Family**: 'Noto Sans KR' for Korean text, system fonts for English
- **Font Sizes**: 
  - Headers: 32px (h1), 24px (h2), 18px (h3)
  - Body: 14px (default), 13px (tables), 12px (labels)
- **Font Weights**: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Component Patterns

1. **Cards**: White background, 12px border-radius, subtle shadow
2. **Buttons**: 
   - Primary: Purple gradient with hover effects
   - Secondary: White with border
   - Icon buttons: 40px square with subtle hover
3. **Forms**:
   - Input fields: 8px border-radius, focus states with purple glow
   - Labels: 600 font-weight, 14px size
   - Error states: Red border with error message
4. **Tables**:
   - Excel-style grid with sticky headers
   - Alternating row colors (#f7fafc)
   - Compact padding (10px 8px)
5. **Badges**: Small rounded rectangles with status colors

### Animation & Transitions

- **Duration**: 0.2s for quick interactions, 0.3s for page transitions
- **Easing**: ease or ease-in-out
- **Common animations**:
  - Hover states: transform, box-shadow
  - Page elements: slideIn, fadeIn
  - Loading states: pulse or spin

### Tone & Manner

1. **Professional yet Friendly**: Business-appropriate but not stiff
2. **Clear & Direct**: Simple Korean language, avoiding technical jargon
3. **Action-Oriented**: Use verbs for buttons (추가하기, 저장하기, 삭제하기)
4. **Respectful**: Use formal Korean endings (-습니다, -세요)
5. **Informative**: Provide clear feedback for all user actions

### UI Text Guidelines

- **Success Messages**: "✓ [작업]이(가) 완료되었습니다"
- **Error Messages**: "⚠️ [문제 설명]. 다시 시도해주세요."
- **Empty States**: "[항목]이(가) 없습니다" with action button
- **Loading States**: "[작업] 중..." with spinner
- **Confirmation Dialogs**: "정말로 [작업]하시겠습니까?"

## Database Configuration

- **Host**: 192.168.0.109 (Remote MariaDB on Synology NAS)
- **Port**: 3306
- **Database**: trade_naver_cupang
- **User**: root
- **Character Set**: utf8mb4 for Korean text support
- **Connection**: Using PyMySQL driver

### Database Tables (13 total)

1. **users** - 사용자 정보
2. **platforms** - 플랫폼 정보 (네이버, 쿠팡)
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

## Current State & Known Issues

1. **Production Deployment**: Running on Synology NAS at port 7000
2. **Deployment Path**: `/volume1/homes/joopok/python/logiflow`
3. **Scraper Service**: Temporarily disabled (selenium import commented out)
4. **Development Port**: 5001 (to avoid conflicts)
5. **Production Port**: 7000
6. **Menu State**: Using localStorage to persist sidebar menu expansion state
7. **Admin Login**: Default admin account with username: admin, password: admin123
8. **Session Keys**: Fixed mismatch issue - using 'role' instead of 'user_role'
9. **Date Format**: Using YYYY.MM.DD and YYYY.MM.DD HH:MM:SS format
10. **Admin permission checks**: Temporarily disabled in API routes for testing

## API Integration Points

- **Naver Commerce API**: Documentation URL stored, implementation pending
  - URL: https://apicenter.commerce.naver.com/docs/commerce-api/current/seller-confirm-placed-product-orders-pay-order-seller
- **Coupang API**: Configuration present, implementation pending

## Frontend Features

1. **Dark Mode**: Toggle between light/dark themes
2. **Responsive Sidebar**: Collapsible navigation with submenu support
3. **Menu State Persistence**: Remembers expanded menus across page loads
4. **Korean UI**: Full Korean language interface
5. **Excel-style Grid Tables**: Orders and users pages use compact grid layout
6. **Spinner System**: Multiple spinner implementations (emergency_spinner.js, super_simple_spinner.js)

## Common Development Tasks

When fixing UI issues:
1. Check if common styles are in `common_sidebar.css`
2. Page-specific styles go in respective CSS files
3. JavaScript functionality often split between common and page-specific files

When updating database schema:
1. Update models in both `app/models/` and `database/models/`
2. Run `database/init_db.py` to recreate schema
3. Test with `database/test_connection.py`

When adding new pages:
1. Create route in `app/routes/main.py`
2. Create template in `templates/` with sidebar and header includes
3. Create page-specific CSS in `static/css/`
4. Add menu item in `templates/includes/sidebar.html`

When implementing new UI components:
1. Follow the established color palette and typography
2. Maintain consistent spacing (8px, 16px, 24px, 32px)
3. Add hover states and transitions for interactive elements
4. Ensure dark mode compatibility
5. Use Korean language with formal tone

## Deployment & Production

### Quick Deploy to NAS
```bash
# Use ready-made package
scp logiflow-nas-deploy.tar.gz joopok@192.168.0.109:~/
ssh joopok@192.168.0.109
cd /volume1/homes/joopok/python/logiflow
tar -xzf ~/logiflow-nas-deploy.tar.gz
./install.sh
```

### Manual Deployment
```bash
# Create deployment package
./deploy_manual.sh

# Deploy to NAS
scp logiflow-manual-deploy.tar.gz joopok@192.168.0.109:~/
```

### Environment Files
- `.env` - Development environment
- `.env.production` - Production environment (do not commit)
- `.env.example` - Template for environment variables
- `.env.nas` - NAS-specific configuration (auto-generated)

### Access URLs
- Development: `http://localhost:5001`
- Production (Internal): `http://192.168.0.109:7000`
- SSH Access: `ssh -p 22 joopok@192.168.0.109`

## Important Notes

- Development runs on port 5001, production on port 7000
- Use `common_sidebar.js` for menu functionality
- Theme toggle uses separate `theme_toggle.js`
- Header is now a reusable component in `includes/header.html`
- CSS has been refactored to eliminate duplication between pages
- When creating forms, follow the existing pattern in `create_user.html` for consistent styling
- Use Excel-style grid tables for data lists (see `orders.html` and `users.html` for examples)
- Maintain the established tone & manner in all UI text and user communications
- For NAS deployment, skip the mariadb package as it requires system libraries not available on Synology
- Use PyMySQL instead of mariadb connector for better compatibility