
        // 로그아웃 시 localStorage 초기화
        window.addEventListener('DOMContentLoaded', function() {
            // URL 파라미터 확인
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('logout') === '1') {
                // localStorage 초기화
                localStorage.clear();
                // 세션 스토리지도 초기화 (필요한 경우)
                sessionStorage.clear();
                // URL에서 logout 파라미터 제거 (깔끔한 URL 유지)
                const url = new URL(window.location);
                url.searchParams.delete('logout');
                window.history.replaceState({}, document.title, url.pathname);
            }
        });

        // 메시지 알림을 표시하는 함수
        function showAlert(message, type) {
            // 기존 알림 제거
            const existingAlerts = document.querySelectorAll('.alert');
            existingAlerts.forEach(alert => alert.remove());
            
            // 새 알림 생성
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.style.cssText = 'display: block; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; animation: fadeIn 0.3s ease-out;';
            
            // 타입별 스타일 설정
            const styles = {
                error: 'background-color: #fee; color: #c33;',
                success: 'background-color: #e6f7e6; color: #2e7d2e;',
                warning: 'background-color: #fff3cd; color: #856404;',
                info: 'background-color: #d1ecf1; color: #0c5460;'
            };
            
            alertDiv.style.cssText += styles[type] || styles.error;
            
            // 아이콘 추가
            const icons = {
                error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block; vertical-align: middle; margin-right: 8px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
                success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block; vertical-align: middle; margin-right: 8px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
                warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block; vertical-align: middle; margin-right: 8px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
                info: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block; vertical-align: middle; margin-right: 8px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
            };
            
            alertDiv.innerHTML = (icons[type] || icons.error) + message;
            
            // 로그인 폼 앞에 삽입
            const loginForm = document.getElementById('loginForm');
            loginForm.parentNode.insertBefore(alertDiv, loginForm);
            
            // 5초 후 자동으로 사라지게
            setTimeout(() => {
                alertDiv.style.animation = 'fadeOut 0.3s ease-out';
                setTimeout(() => alertDiv.remove(), 300);
            }, 5000);
        }
        
        // CSS 애니메이션 추가
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(-10px); }
            }
            .login-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .login-button.loading {
                position: relative;
                color: transparent;
            }
            .login-button.loading::after {
                content: '';
                position: absolute;
                width: 20px;
                height: 20px;
                top: 50%;
                left: 50%;
                margin-left: -10px;
                margin-top: -10px;
                border: 2px solid #ffffff;
                border-radius: 50%;
                border-top-color: transparent;
                animation: spinner 0.8s linear infinite;
            }
            @keyframes spinner {
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
        
        // 로그인 폼 처리
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitButton = this.querySelector('.login-button');
            const originalText = submitButton.textContent;
            
            // 버튼 상태 변경
            submitButton.disabled = true;
            submitButton.classList.add('loading');
            
            // 폼 데이터 수집
            const formData = new FormData(this);
            
            try {
                const loginUrl = this.dataset.loginUrl;
                const response = await fetch(loginUrl, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert(data.message || '로그인 성공!', 'success');
                    // 성공 시 리다이렉트
                    setTimeout(() => {
                        window.location.href = data.redirect || '{{ url_for("main.dashboard") }}';
                    }, 500);
                } else {
                    // 에러 메시지 표시
                    showAlert(data.message || '로그인에 실패했습니다.', 'error');
                    submitButton.disabled = false;
                    submitButton.classList.remove('loading');
                }
            } catch (error) {
                console.error('Login error:', error);
                showAlert('서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.', 'error');
                submitButton.disabled = false;
                submitButton.classList.remove('loading');
            }
        });
        
        // 엔터키 처리
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const form = document.getElementById('loginForm');
                    const submitButton = form.querySelector('.login-button');
                    if (!submitButton.disabled) {
                        form.dispatchEvent(new Event('submit'));
                    }
                }
            });
        });
    