from datetime import datetime, timedelta

def generate_dummy_data():
    projects = [
        {
            "id": "1",
            "name": "2024년 전사 시스템 고도화 프로젝트",
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=180),
            "progress": 25,
            "manager": "김프로",
            "budget": 500000000,
            "priority": "HIGH",
            "status": "진행중",
            "children": [
                {
                    "id": "1-1",
                    "name": "프로젝트 기획 및 분석",
                    "start_date": datetime.now(),
                    "end_date": datetime.now() + timedelta(days=30),
                    "progress": 90,
                    "manager": "이과장",
                    "priority": "HIGH",
                    "status": "진행중",
                    "resources": ["기획팀", "PM팀"],
                    "children": [
                        {
                            "id": "1-1-1",
                            "name": "현행 시스템 분석",
                            "start_date": datetime.now(),
                            "end_date": datetime.now() + timedelta(days=10),
                            "progress": 100,
                            "manager": "박대리",
                            "resources": ["기획팀"],
                            "deliverables": ["현행 시스템 분석서"],
                            "status": "완료"
                        },
                        {
                            "id": "1-1-2",
                            "name": "요구사항 정의",
                            "start_date": datetime.now() + timedelta(days=10),
                            "end_date": datetime.now() + timedelta(days=20),
                            "progress": 85,
                            "manager": "이과장",
                            "resources": ["기획팀", "개발팀"],
                            "dependencies": ["1-1-1"],
                            "status": "진행중"
                        }
                    ]
                },
                {
                    "id": "1-2",
                    "name": "시스템 설계",
                    "start_date": datetime.now() + timedelta(days=30),
                    "end_date": datetime.now() + timedelta(days=90),
                    "progress": 30,
                    "manager": "최차장",
                    "priority": "MEDIUM",
                    "status": "진행중",
                    "resources": ["설계팀", "아키텍처팀"],
                    "children": [
                        {
                            "id": "1-2-1",
                            "name": "아키텍처 설계",
                            "start_date": datetime.now() + timedelta(days=30),
                            "end_date": datetime.now() + timedelta(days=50),
                            "progress": 60,
                            "manager": "정수석",
                            "resources": ["아키텍처팀"],
                            "dependencies": ["1-1-2"],
                            "status": "진행중"
                        },
                        {
                            "id": "1-2-2",
                            "name": "데이터베이스 설계",
                            "start_date": datetime.now() + timedelta(days=45),
                            "end_date": datetime.now() + timedelta(days=70),
                            "progress": 20,
                            "manager": "김과장",
                            "resources": ["DB팀"],
                            "dependencies": ["1-2-1"],
                            "status": "진행중"
                        }
                    ]
                }
            ]
        }
    ]
    return projects 