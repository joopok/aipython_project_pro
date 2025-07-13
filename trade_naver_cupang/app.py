import os
import logging
from app import create_app

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7000
    app.run(debug=True, host='0.0.0.0', port=port)