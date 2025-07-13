#!/usr/bin/env python3
"""
LogiFlow NAS 배포 도우미
간단한 GUI로 배포 과정을 안내합니다.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class DeployHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LogiFlow NAS 배포 도우미")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 설정
        self.nas_ip = "192.168.0.109"
        self.nas_user = "joopok"
        self.nas_path = "/volume1/homes/joopok/python/logiflow"
        
        self.setup_ui()
        
    def setup_ui(self):
        # 제목
        title = tk.Label(self.root, text="LogiFlow NAS 배포 도우미", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # 설정 프레임
        config_frame = ttk.LabelFrame(self.root, text="NAS 설정", padding=10)
        config_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(config_frame, text="NAS IP:").grid(row=0, column=0, sticky="w")
        self.ip_entry = tk.Entry(config_frame, width=20)
        self.ip_entry.insert(0, self.nas_ip)
        self.ip_entry.grid(row=0, column=1, padx=10)
        
        tk.Label(config_frame, text="사용자:").grid(row=1, column=0, sticky="w")
        self.user_entry = tk.Entry(config_frame, width=20)
        self.user_entry.insert(0, self.nas_user)
        self.user_entry.grid(row=1, column=1, padx=10)
        
        tk.Label(config_frame, text="경로:").grid(row=2, column=0, sticky="w")
        self.path_entry = tk.Entry(config_frame, width=40)
        self.path_entry.insert(0, self.nas_path)
        self.path_entry.grid(row=2, column=1, padx=10)
        
        # 단계별 배포 프레임
        steps_frame = ttk.LabelFrame(self.root, text="배포 단계", padding=10)
        steps_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 단계 1: 배포 파일 생성
        step1_frame = tk.Frame(steps_frame)
        step1_frame.pack(fill="x", pady=5)
        
        self.step1_btn = tk.Button(step1_frame, text="1. 배포 파일 생성", 
                                  command=self.create_deploy_package, 
                                  bg="#4CAF50", fg="white", width=20)
        self.step1_btn.pack(side="left")
        
        self.step1_status = tk.Label(step1_frame, text="대기 중", fg="gray")
        self.step1_status.pack(side="left", padx=10)
        
        # 단계 2: NAS에 파일 전송
        step2_frame = tk.Frame(steps_frame)
        step2_frame.pack(fill="x", pady=5)
        
        self.step2_btn = tk.Button(step2_frame, text="2. NAS에 파일 전송", 
                                  command=self.upload_to_nas, 
                                  bg="#2196F3", fg="white", width=20, state="disabled")
        self.step2_btn.pack(side="left")
        
        self.step2_status = tk.Label(step2_frame, text="대기 중", fg="gray")
        self.step2_status.pack(side="left", padx=10)
        
        # 단계 3: NAS 명령어 생성
        step3_frame = tk.Frame(steps_frame)
        step3_frame.pack(fill="x", pady=5)
        
        self.step3_btn = tk.Button(step3_frame, text="3. NAS 명령어 생성", 
                                  command=self.generate_nas_commands, 
                                  bg="#FF9800", fg="white", width=20, state="disabled")
        self.step3_btn.pack(side="left")
        
        self.step3_status = tk.Label(step3_frame, text="대기 중", fg="gray")
        self.step3_status.pack(side="left", padx=10)
        
        # 진행률 표시
        self.progress = ttk.Progressbar(steps_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=10)
        
        # 로그 출력
        log_frame = ttk.LabelFrame(self.root, text="실행 로그", padding=5)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 닫기 버튼
        close_btn = tk.Button(self.root, text="닫기", command=self.root.quit, 
                             bg="#f44336", fg="white")
        close_btn.pack(pady=10)
        
    def log(self, message):
        """로그 메시지 출력"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def create_deploy_package(self):
        """배포 패키지 생성"""
        def run_deploy():
            try:
                self.step1_status.config(text="진행 중...", fg="orange")
                self.progress.start()
                
                self.log("🚀 배포 파일 생성 시작...")
                
                # 배포 스크립트 실행
                result = subprocess.run(['./deploy_manual.sh'], 
                                      capture_output=True, text=True, 
                                      input='N\n')  # 자동 배포 거부
                
                if result.returncode == 0:
                    self.step1_status.config(text="완료", fg="green")
                    self.step2_btn.config(state="normal")
                    self.log("✅ 배포 파일 생성 완료")
                    self.log(f"📦 파일: logiflow-manual-deploy.tar.gz")
                else:
                    self.step1_status.config(text="실패", fg="red")
                    self.log(f"❌ 오류: {result.stderr}")
                    
            except Exception as e:
                self.step1_status.config(text="실패", fg="red")
                self.log(f"❌ 예외 발생: {str(e)}")
            finally:
                self.progress.stop()
                
        # 별도 스레드에서 실행
        threading.Thread(target=run_deploy, daemon=True).start()
        
    def upload_to_nas(self):
        """NAS에 파일 전송"""
        def run_upload():
            try:
                self.step2_status.config(text="진행 중...", fg="orange")
                self.progress.start()
                
                nas_ip = self.ip_entry.get()
                nas_user = self.user_entry.get()
                
                self.log(f"📤 NAS에 파일 전송 중... ({nas_user}@{nas_ip})")
                
                # SCP 명령어 실행
                cmd = f"scp logiflow-manual-deploy.tar.gz {nas_user}@{nas_ip}:~/"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.step2_status.config(text="완료", fg="green")
                    self.step3_btn.config(state="normal")
                    self.log("✅ 파일 전송 완료")
                else:
                    self.step2_status.config(text="실패", fg="red")
                    self.log(f"❌ 전송 실패: {result.stderr}")
                    self.log("💡 수동으로 파일을 전송해주세요.")
                    
            except Exception as e:
                self.step2_status.config(text="실패", fg="red")
                self.log(f"❌ 예외 발생: {str(e)}")
            finally:
                self.progress.stop()
                
        # 별도 스레드에서 실행
        threading.Thread(target=run_upload, daemon=True).start()
        
    def generate_nas_commands(self):
        """NAS에서 실행할 명령어 생성"""
        try:
            self.step3_status.config(text="완료", fg="green")
            
            nas_ip = self.ip_entry.get()
            nas_user = self.user_entry.get()
            nas_path = self.path_entry.get()
            
            commands = f"""
🔧 NAS에서 실행할 명령어들:

1. SSH 접속:
   ssh {nas_user}@{nas_ip}

2. 디렉토리 이동 및 파일 압축 해제:
   cd {nas_path}
   tar -xzf ~/logiflow-manual-deploy.tar.gz

3. 환경설정 파일 복사 및 수정:
   cp .env.nas .env
   nano .env
   # DB_PASSWORD와 SECRET_KEY를 실제 값으로 수정

4. 데이터베이스 초기화 (첫 설치시만):
   ./start_nas.sh --init-db

5. 서비스 시작:
   ./start_nas.sh

6. 웹 접속 확인:
   http://{nas_ip}:7000

🛠️ 서비스 관리 명령어:
   시작: ./start_nas.sh
   종료: ./stop_nas.sh
"""
            
            self.log(commands)
            
            # 클립보드에 SSH 명령어 복사
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(f"ssh {nas_user}@{nas_ip}")
                self.log("📋 SSH 명령어가 클립보드에 복사되었습니다.")
            except:
                pass
                
        except Exception as e:
            self.step3_status.config(text="실패", fg="red")
            self.log(f"❌ 예외 발생: {str(e)}")
            
    def run(self):
        """GUI 실행"""
        self.log("🎯 LogiFlow NAS 배포 도우미가 시작되었습니다.")
        self.log("📋 각 단계를 순서대로 실행해주세요.")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = DeployHelper()
        app.run()
    except ImportError:
        print("⚠️  Tkinter가 설치되지 않았습니다.")
        print("💻 터미널에서 다음 명령어를 실행하세요:")
        print("./deploy_manual.sh")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💻 터미널에서 다음 명령어를 실행하세요:")
        print("./deploy_manual.sh")