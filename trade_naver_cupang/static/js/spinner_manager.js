// 공통 스피너 관리자 - 개선된 버전
// 모든 페이지에서 공통으로 사용할 수 있는 스피너 시스템

class SpinnerManager {
    constructor() {
        this.activeSpinners = new Map();
        this.globalSpinner = null;
        this.apiCallTracker = new Map();
        this.customCompletionConditions = new Set();
        this.progressCallbacks = new Map();
        this.statusUpdateCallbacks = new Map();
        this.minDisplayTime = 3000; // 최소 3초 표시
        this.maxDisplayTime = 30000; // 최대 30초
        
        this.setupAPIInterceptors();
        this.setupGlobalEventListeners();
    }

    showGlobal(options = {}) {
        console.log('🔍 DEBUG: showGlobal 메서드 시작:', {
            options: options,
            현재globalSpinner: this.globalSpinner,
            timestamp: new Date().toLocaleTimeString()
        });
        
        const config = {
            message: '페이지를 불러오는 중...',
            type: 'spin',
            showProgress: true,
            maxTime: this.maxDisplayTime,
            autoComplete: true,
            minTime: 3000,  // 최소 3초 표시
            ...options
        };

        if (this.globalSpinner && this.globalSpinner.isActive) {
            console.log('🔍 DEBUG: 이미 활성화된 globalSpinner 있음:', this.globalSpinner.id);
            return this.globalSpinner.id;
        }

        const spinnerId = this.generateId();
        console.log('🔍 DEBUG: 새 스피너 ID 생성:', spinnerId);
        
        this.globalSpinner = {
            id: spinnerId,
            isActive: true,
            config: config,
            startTime: Date.now(),
            element: null,
            progress: 0,
            status: '초기화 중...',
            canHide: false  // 최소 시간 전까지는 숨길 수 없음
        };

        console.log('🔍 DEBUG: createSpinnerElement 호출 전');
        this.createSpinnerElement(this.globalSpinner);
        console.log('🔍 DEBUG: startProgressSimulation 호출 전');
        this.startProgressSimulation(spinnerId);

        // 최소 시간 보장
        setTimeout(() => {
            console.log('🔍 DEBUG: 최소 시간 경과, canHide = true:', spinnerId);
            if (this.globalSpinner && this.globalSpinner.id === spinnerId) {
                this.globalSpinner.canHide = true;
            }
        }, config.minTime);

        // 최대 시간 후 강제 종료
        setTimeout(() => {
            console.log('🔍 DEBUG: 최대 시간 도달, 강제 종료:', spinnerId);
            this.hide(spinnerId);
        }, config.maxTime);

        if (config.autoComplete) {
            this.setupAutoComplete(spinnerId);
        }

        return spinnerId;
    }

    // 특정 컨텍스트용 스피너 (API 호출, 데이터 로딩 등)
    show(context, options = {}) {
        const config = {
            message: '처리 중...',
            type: 'spin',
            showProgress: false,
            minTime: 1000,
            maxTime: 15000,
            autoComplete: false,
            ...options
        };

        const spinnerId = this.generateId();
        const spinner = {
            id: spinnerId,
            context: context,
            isActive: true,
            config: config,
            startTime: Date.now(),
            element: null,
            progress: 0,
            status: config.message
        };

        this.activeSpinners.set(spinnerId, spinner);
        
        // 글로벌 스피너가 없으면 엘리먼트 생성
        if (!this.globalSpinner || !this.globalSpinner.isActive) {
            this.createSpinnerElement(spinner);
        } else {
            // 글로벌 스피너가 있으면 메시지 업데이트
            this.updateSpinnerContent(this.globalSpinner, config.message, config.type);
        }

        // 최소 시간 보장
        setTimeout(() => {
            if (this.activeSpinners.has(spinnerId)) {
                spinner.canHide = true;
            }
        }, config.minTime);

        // 최대 시간 후 강제 종료
        setTimeout(() => {
            this.hide(spinnerId);
        }, config.maxTime);

        return spinnerId;
    }

    // 스피너 숨기기
    hide(spinnerId) {
        console.log('🔍 DEBUG: hide 메서드 호출:', {
            spinnerId: spinnerId,
            globalSpinnerId: this.globalSpinner?.id,
            isGlobalSpinner: this.globalSpinner?.id === spinnerId,
            canHide: this.globalSpinner?.canHide,
            activeSpinners: Array.from(this.activeSpinners.keys()),
            timestamp: new Date().toLocaleTimeString()
        });
        
        let spinner = null;

        if (this.globalSpinner && this.globalSpinner.id === spinnerId) {
            // 최소 시간이 지나지 않았으면 대기
            if (!this.globalSpinner.canHide) {
                console.log('🔍 DEBUG: 최소 시간 미달, hide 지연');
                const checkInterval = setInterval(() => {
                    if (this.globalSpinner && this.globalSpinner.canHide) {
                        clearInterval(checkInterval);
                        this.hide(spinnerId);
                    }
                }, 100);
                return;
            }
            
            console.log('🔍 DEBUG: globalSpinner 숨기기');
            spinner = this.globalSpinner;
            
            // 시뮬레이션 인터벌 정리
            if (spinner.simulationInterval) {
                clearInterval(spinner.simulationInterval);
                spinner.simulationInterval = null;
            }
            
            // 다크모드에서는 바로 숨기기 (투명 효과 제거)
            const isDarkMode = document.body.getAttribute('data-theme') === 'dark';
            if (isDarkMode && spinner.element) {
                // 다크모드에서는 즉시 숨기기
                this.hideSpinnerElement(spinner);
            } else {
                this.hideSpinnerElement(spinner);
            }
            
            this.globalSpinner = null;
        } else if (this.activeSpinners.has(spinnerId)) {
            console.log('🔍 DEBUG: activeSpinner 숨기기');
            spinner = this.activeSpinners.get(spinnerId);
            this.activeSpinners.delete(spinnerId);

            if (this.activeSpinners.size === 0 && (!this.globalSpinner || !this.globalSpinner.isActive)) {
                this.hideSpinnerElement(spinner);
            }
        }
    }

    // 모든 스피너 숨기기
    hideAll() {
        if (this.globalSpinner) {
            this.hideSpinnerElement(this.globalSpinner);
            this.globalSpinner = null;
        }
        
        this.activeSpinners.forEach(spinner => {
            this.hideSpinnerElement(spinner);
        });
        this.activeSpinners.clear();
        
        this.enableInteractions();
    }

    // 진행률 업데이트
    setProgress(spinnerId, progress, status = null) {
        const spinner = this.getSpinner(spinnerId);
        if (!spinner) return;

        // 진행률이 역행하지 않도록 보장
        const newProgress = Math.max(spinner.progress || 0, Math.min(100, progress));
        
        console.log('🔍 DEBUG: setProgress 호출:', {
            spinnerId: spinnerId,
            현재진행률: spinner.progress,
            요청진행률: progress,
            최종진행률: newProgress,
            status: status
        });

        spinner.progress = newProgress;
        if (status) spinner.status = status;

        this.updateProgress(spinner);
        
        // 진행률 콜백 실행
        const callback = this.progressCallbacks.get(spinnerId);
        if (callback) callback(progress, status);
    }

    // 상태 메시지 업데이트
    setStatus(spinnerId, status) {
        const spinner = this.getSpinner(spinnerId);
        if (!spinner) return;

        spinner.status = status;
        this.updateStatus(spinner);
        
        // 상태 콜백 실행
        const callback = this.statusUpdateCallbacks.get(spinnerId);
        if (callback) callback(status);
    }

    // API 호출 추적 시작
    trackApiCall(url, method = 'GET') {
        const callId = this.generateId();
        this.apiCallTracker.set(callId, {
            url: url,
            method: method,
            startTime: Date.now(),
            completed: false
        });
        return callId;
    }

    // API 호출 완료 마킹
    completeApiCall(callId) {
        if (this.apiCallTracker.has(callId)) {
            const call = this.apiCallTracker.get(callId);
            call.completed = true;
            call.endTime = Date.now();
        }
    }

    // 사용자 정의 완료 조건 추가
    addCompletionCondition(condition) {
        if (typeof condition === 'function') {
            this.customCompletionConditions.add(condition);
        }
    }

    // 완료 조건 제거
    removeCompletionCondition(condition) {
        this.customCompletionConditions.delete(condition);
    }

    // 진행률 콜백 등록
    onProgress(spinnerId, callback) {
        this.progressCallbacks.set(spinnerId, callback);
    }

    // 상태 업데이트 콜백 등록
    onStatusUpdate(spinnerId, callback) {
        this.statusUpdateCallbacks.set(spinnerId, callback);
    }

    // 스피너 엘리먼트 생성
    createSpinnerElement(spinner) {
        console.log("[Debug] 1. createSpinnerElement 시작");
        const mainContent = document.getElementById('mainContent');
        if (!mainContent) {
            console.error("[Debug] 1a. #mainContent 요소를 찾을 수 없습니다. 스피너를 생성할 수 없습니다.");
            return;
        }
        console.log("[Debug] 1b. #mainContent 찾음:", mainContent);

        // 기존 스피너 제거
        const existingLoader = mainContent.querySelector('.main-content-loader');
        if (existingLoader) {
            console.log("[Debug] 1c. 기존 스피너 제거");
            existingLoader.remove();
        }

        const loaderElement = document.createElement('div');
        loaderElement.className = `main-content-loader spinner-type-${spinner.config.type}`;
        loaderElement.id = 'global-spinner';
        
        // 현재 테마 확인
        const isDarkMode = document.body.getAttribute('data-theme') === 'dark';
        console.log('🔍 DEBUG: 현재 테마:', isDarkMode ? '다크모드' : '라이트모드');

        loaderElement.innerHTML = `
            <div class="spinner-container">
                ${this.getSpinnerHTML(spinner.config.type)}
                <div class="main-content-loader-text">${spinner.config.message}</div>
                ${spinner.config.showProgress ? this.getProgressHTML() : ''}
                <div class="loader-status">${spinner.status}</div>
            </div>
        `;

        mainContent.appendChild(loaderElement);
        spinner.element = loaderElement;
        console.log("[Debug] 1d. 새로운 스피너 엘리먼트를 #mainContent에 추가했습니다.", loaderElement);
    }

    // 스피너 HTML 생성
    getSpinnerHTML(type) {
        switch (type) {
            case 'dots':
                return `
                    <div class="main-content-spinner">
                        <div class="spinner-dots">
                            <div class="spinner-dot"></div>
                            <div class="spinner-dot"></div>
                            <div class="spinner-dot"></div>
                        </div>
                    </div>
                `;
            case 'pulse':
                return '<div class="main-content-spinner"></div>';
            default: // 'spin'
                return '<div class="main-content-spinner"></div>';
        }
    }

    // 진행률 HTML 생성
    getProgressHTML() {
        return `
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
                <div class="progress-text">0%</div>
            </div>
        `;
    }

    // 스피너 컨텐츠 업데이트
    updateSpinnerContent(spinner, message, type) {
        if (!spinner.element) return;

        const messageEl = spinner.element.querySelector('.main-content-loader-text');
        if (messageEl) messageEl.textContent = message;

        if (type && type !== spinner.config.type) {
            spinner.config.type = type;
            const spinnerEl = spinner.element.querySelector('.main-content-spinner');
            if (spinnerEl) {
                spinnerEl.outerHTML = this.getSpinnerHTML(type);
            }
        }
    }

    // 진행률 업데이트
    updateProgress(spinner) {
        if (!spinner.element) return;

        const progressFill = spinner.element.querySelector('.progress-fill');
        const progressText = spinner.element.querySelector('.progress-text');

        if (progressFill) {
            progressFill.style.width = `${spinner.progress}%`;
        }
        if (progressText) {
            progressText.textContent = `${Math.round(spinner.progress)}%`;
        }
    }

    // 상태 업데이트
    updateStatus(spinner) {
        if (!spinner.element) return;

        const statusEl = spinner.element.querySelector('.loader-status');
        if (statusEl) {
            statusEl.textContent = spinner.status;
        }
    }

    // 스피너 엘리먼트 숨기기
    hideSpinnerElement(spinner) {
        if (!spinner.element) return;

        // 다크모드에서는 즉시 제거, 라이트모드에서만 페이드아웃
        const isDarkMode = document.body.getAttribute('data-theme') === 'dark';
        
        if (isDarkMode) {
            // 다크모드에서는 즉시 제거
            if (spinner.element.parentNode) {
                spinner.element.parentNode.removeChild(spinner.element);
            }
        } else {
            // 라이트모드에서는 페이드아웃 효과
            spinner.element.classList.add('hidden');
            
            setTimeout(() => {
                if (spinner.element && spinner.element.parentNode) {
                    spinner.element.parentNode.removeChild(spinner.element);
                }
            }, 350);
        }
    }

    // 진행률 시뮬레이션 시작
    startProgressSimulation(spinnerId) {
        const spinner = this.getSpinner(spinnerId);
        if (!spinner || !spinner.config.showProgress) return;

        // 시뮬레이션 상태 저장
        spinner.simulationInterval = null;
        spinner.targetProgress = 0;
        spinner.simulationProgress = 0;
        
        const updateProgress = () => {
            if (!this.getSpinner(spinnerId)) {
                if (spinner.simulationInterval) {
                    clearInterval(spinner.simulationInterval);
                }
                return;
            }

            // 목표 진행률 설정 (시간에 따라 자연스럽게 증가)
            const elapsedTime = Date.now() - spinner.startTime;
            const elapsedSeconds = elapsedTime / 1000;
            
            // 로그 함수를 사용한 자연스러운 진행률 곡선
            // 처음엔 빠르게, 나중엔 천천히
            if (elapsedSeconds < 0.5) {
                // 0.5초까지: 빠른 시작 (0% -> 20%)
                spinner.targetProgress = (elapsedSeconds / 0.5) * 20;
            } else if (elapsedSeconds < 1.5) {
                // 0.5-1.5초: 중간 속도 (20% -> 60%)
                spinner.targetProgress = 20 + ((elapsedSeconds - 0.5) / 1) * 40;
            } else if (elapsedSeconds < 3) {
                // 1.5-3초: 느린 진행 (60% -> 85%)
                spinner.targetProgress = 60 + ((elapsedSeconds - 1.5) / 1.5) * 25;
            } else if (elapsedSeconds < 5) {
                // 3-5초: 매우 느린 진행 (85% -> 94%)
                spinner.targetProgress = 85 + ((elapsedSeconds - 3) / 2) * 9;
            } else {
                // 5초 이후: 94%에서 멈춤
                spinner.targetProgress = 94;
            }

            // 랜덤 요소 추가로 더 자연스럽게
            const randomVariation = (Math.random() - 0.5) * 2; // -1 ~ 1
            spinner.targetProgress = Math.max(0, Math.min(94, spinner.targetProgress + randomVariation));

            // 현재 진행률을 목표치에 부드럽게 접근
            const diff = spinner.targetProgress - spinner.simulationProgress;
            const smoothingFactor = 0.08; // 더 부드러운 전환을 위해 감소
            spinner.simulationProgress += diff * smoothingFactor;

            // 진행률이 완료 체크로 100이 되었다면 시뮬레이션 중단
            if (spinner.progress >= 100) {
                if (spinner.simulationInterval) {
                    clearInterval(spinner.simulationInterval);
                    spinner.simulationInterval = null;
                }
                return;
            }
            
            // 실제 진행률 업데이트 (역행 방지)
            if (spinner.simulationProgress > (spinner.progress || 0)) {
                const status = this.getProgressStatus(spinner.simulationProgress);
                this.setProgress(spinnerId, Math.round(spinner.simulationProgress), status);
            }
            
            // 95%에 도달하면 시뮬레이션 중단
            if (spinner.simulationProgress >= 94) {
                if (spinner.simulationInterval) {
                    clearInterval(spinner.simulationInterval);
                    spinner.simulationInterval = null;
                }
                this.setProgress(spinnerId, 95, '완료 확인 중...');
            }
        };

        // 초기 업데이트
        updateProgress();
        
        // 주기적 업데이트 (부드러운 애니메이션을 위해 100ms 간격)
        spinner.simulationInterval = setInterval(updateProgress, 100);
    }

    // 진행률에 따른 상태 메시지
    getProgressStatus(progress) {
        // 더 세분화된 메시지로 자연스러운 전환
        if (progress < 10) return '서버 연결 중...';
        if (progress < 25) return '인증 확인 중...';
        if (progress < 35) return '데이터 요청 중...';
        if (progress < 50) return '데이터 수신 중...';
        if (progress < 65) return '데이터 처리 중...';
        if (progress < 75) return '화면 구성 중...';
        if (progress < 85) return '렌더링 중...';
        if (progress < 92) return '마무리 작업 중...';
        if (progress < 95) return '거의 완료...';
        return '완료 확인 중...';
    }

    // 자동 완료 설정
    setupAutoComplete(spinnerId) {
        const spinner = this.getSpinner(spinnerId);
        if (!spinner) return;

        const checkCompletion = () => {
            if (!this.getSpinner(spinnerId)) return;

            const conditions = [
                this.checkPageDataLoaded(),
                this.checkApiCallsCompleted(),
                this.checkCustomConditions()
            ];

            console.log('🔍 DEBUG: 완료 조건 확인:', conditions);
            
            if (conditions.every(condition => condition)) {
                console.log('🔍 DEBUG: 모든 조건 충족, 완료 처리');
                
                const spinner = this.getSpinner(spinnerId);
                if (!spinner) return;
                
                // 시뮬레이션 중단
                if (spinner.simulationInterval) {
                    clearInterval(spinner.simulationInterval);
                    spinner.simulationInterval = null;
                }
                
                // 현재 진행률에서 100%까지 부드럽게 전환
                const currentProgress = spinner.progress || 0;
                
                // 남은 진행률을 자연스럽게 채우기
                let completionProgress = currentProgress;
                const completionSteps = 8; // 8단계로 나누어 진행
                const progressIncrement = (100 - currentProgress) / completionSteps;
                
                for (let i = 0; i <= completionSteps; i++) {
                    const targetProgress = Math.min(100, currentProgress + (progressIncrement * i));
                    const delay = i * 100; // 100ms 간격으로 더 부드럽게
                    
                    setTimeout(() => {
                        if (this.getSpinner(spinnerId)) {
                            let status;
                            if (targetProgress < 95) {
                                status = this.getProgressStatus(targetProgress);
                            } else if (targetProgress < 100) {
                                status = '거의 완료...';
                            } else {
                                status = '완료!';
                            }
                            
                            this.setProgress(spinnerId, Math.round(targetProgress), status);
                        }
                    }, delay);
                }
                
                // 최소 시간이 지났는지 확인
                const elapsedTime = Date.now() - spinner.startTime;
                const remainingMinTime = Math.max(0, (spinner.config.minTime || 3000) - elapsedTime);
                
                console.log('🔍 DEBUG: 완료 대기 시간:', {
                    경과시간: elapsedTime,
                    최소시간: spinner.config.minTime || 3000,
                    남은시간: remainingMinTime,
                    완료애니메이션: completionSteps * 100,
                    추가대기: 800  // 완료 표시 유지 시간
                });
                
                // 최소 시간 충족 후 완료 애니메이션 대기
                const totalDelay = remainingMinTime + (completionSteps * 100) + 800;
                setTimeout(() => {
                    this.hide(spinnerId);
                }, totalDelay);
            } else {
                setTimeout(checkCompletion, 500); // 0.5초마다 재확인
            }
        };

        // 최초 확인은 약간의 딜레이 후 시작
        setTimeout(checkCompletion, 500);
    }

    // 페이지 데이터 로딩 완료 확인
    checkPageDataLoaded() {
        console.log('🔍 DEBUG: checkPageDataLoaded 호출됨');
        
        // 통합 주문조회 페이지인 경우 플래그 확인
        if (window.location.pathname.includes('/integrated/orders')) {
            const dataComplete = window.dataLoadingComplete || false;
            const statsComplete = window.statsLoadingComplete || false;
            
            // 추가로 실제 DOM 요소 확인
            const tableBody = document.getElementById('ordersTableBody');
            const hasTableContent = tableBody && (
                tableBody.children.length > 0 || 
                document.getElementById('emptyMessage')?.style.display !== 'none'
            );
            
            // 통계 요소 확인
            const statsElements = document.querySelectorAll('.stat-value');
            const hasStatsContent = statsElements.length > 0;
            
            console.log('🔍 DEBUG: 통합 주문조회 로딩 상태:', {
                dataLoadingComplete: dataComplete,
                statsLoadingComplete: statsComplete,
                hasTableContent: hasTableContent,
                hasStatsContent: hasStatsContent,
                bothComplete: dataComplete && statsComplete && hasTableContent && hasStatsContent
            });
            
            return dataComplete && statsComplete && hasTableContent && hasStatsContent;
        }
        
        // 로딩 스피너가 없는지 확인 (자체 스피너 제외)
        const loadingSpinners = document.querySelectorAll('.loading-spinner:not(#global-spinner .loading-spinner)');
        if (loadingSpinners.length > 0) {
            console.log('🔍 DEBUG: 아직 로딩 스피너가 있음:', loadingSpinners.length);
            return false;
        }

        // 테이블 데이터 또는 빈 메시지가 있는지 확인
        const tableBody = document.querySelector('#ordersTableBody, .excel-table tbody');
        const emptyMessage = document.querySelector('#emptyMessage');
        
        if (tableBody) {
            // 테이블 내에 로딩 중 메시지가 있는지 확인
            const loadingText = tableBody.querySelector('td[colspan]');
            if (loadingText && loadingText.textContent.includes('데이터를 불러오는 중')) {
                console.log('🔍 DEBUG: 테이블이 아직 로딩 중');
                return false;
            }
            
            const hasData = tableBody.children.length > 0 && !loadingText;
            const hasEmptyMessage = emptyMessage && emptyMessage.style.display !== 'none';
            const isLoaded = hasData || hasEmptyMessage;
            
            console.log('🔍 DEBUG: 테이블 로딩 상태:', {
                hasData: hasData,
                hasEmptyMessage: hasEmptyMessage,
                isLoaded: isLoaded
            });
            
            return isLoaded;
        }

        // 기본 컨텐츠가 있는지 확인
        const content = document.querySelector('.content, .page-header');
        return !!content;
    }

    // API 호출 완료 확인
    checkApiCallsCompleted() {
        return Array.from(this.apiCallTracker.values()).every(call => call.completed);
    }

    // 사용자 정의 조건 확인
    checkCustomConditions() {
        return Array.from(this.customCompletionConditions).every(condition => {
            try {
                return condition();
            } catch (e) {
                console.warn('Custom completion condition error:', e);
                return true;
            }
        });
    }

    // API 인터셉터 설정
    setupAPIInterceptors() {
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            const callId = this.trackApiCall(args[0], args[1]?.method || 'GET');
            
            try {
                const response = await originalFetch(...args);
                this.completeApiCall(callId);
                return response;
            } catch (error) {
                this.completeApiCall(callId);
                throw error;
            }
        };

        // XMLHttpRequest 인터셉터
        const originalXHROpen = XMLHttpRequest.prototype.open;
        const originalXHRSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._callId = window.spinnerManager.trackApiCall(url, method);
            return originalXHROpen.call(this, method, url, ...args);
        };

        XMLHttpRequest.prototype.send = function(...args) {
            this.addEventListener('loadend', () => {
                if (this._callId) {
                    window.spinnerManager.completeApiCall(this._callId);
                }
            });
            return originalXHRSend.call(this, ...args);
        };
    }

    // 글로벌 이벤트 리스너 설정
    setupGlobalEventListeners() {
        // 페이지 언로드 시 모든 스피너 정리
        window.addEventListener('beforeunload', () => {
            this.hideAll();
        });

        // 에러 발생 시 스피너 숨기기
        window.addEventListener('error', () => {
            setTimeout(() => this.hideAll(), 1000);
        });

        // 테마 변경 감지를 위한 MutationObserver
        const themeObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                    console.log('🔍 DEBUG: 테마 변경 감지:', document.body.getAttribute('data-theme'));
                    
                    // 활성 스피너의 배경색 업데이트
                    const activeSpinner = document.querySelector('.main-content-loader');
                    if (activeSpinner && !activeSpinner.classList.contains('hidden')) {
                        const isDarkMode = document.body.getAttribute('data-theme') === 'dark';
                        // CSS 클래스가 자동으로 적용되므로 추가 작업 불필요
                        console.log('🔍 DEBUG: 스피너 테마 자동 업데이트됨');
                    }
                }
            });
        });

        // body 요소의 data-theme 속성 변경 감지
        themeObserver.observe(document.body, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }

    // 상호작용 비활성화
    disableInteractions() {
        const elements = document.querySelectorAll('button, input, select, textarea, a:not(.sidebar a)');
        elements.forEach(el => {
            if (!el.disabled && !el.classList.contains('spinner-disabled')) {
                el.disabled = true;
                el.classList.add('spinner-disabled');
            }
        });
    }

    // 상호작용 활성화
    enableInteractions() {
        const elements = document.querySelectorAll('.spinner-disabled');
        elements.forEach(el => {
            el.disabled = false;
            el.classList.remove('spinner-disabled');
        });
    }

    // 유틸리티 메서드들
    generateId() {
        return 'spinner_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    getSpinner(spinnerId) {
        if (this.globalSpinner && this.globalSpinner.id === spinnerId) {
            return this.globalSpinner;
        }
        return this.activeSpinners.get(spinnerId);
    }

    checkAutoComplete(spinnerId) {
        if (!this.getSpinner(spinnerId)) return;
        
        const conditions = [
            this.checkPageDataLoaded(),
            this.checkApiCallsCompleted(),
            this.checkCustomConditions()
        ];

        if (conditions.every(condition => condition)) {
            this.setProgress(spinnerId, 100, '완료!');
            setTimeout(() => this.hide(spinnerId), 500);
        }
    }
}

// 전역 스피너 매니저 인스턴스 생성
console.log('🔍 DEBUG: SpinnerManager 초기화 시작');
window.spinnerManager = new SpinnerManager();
console.log('🔍 DEBUG: SpinnerManager 인스턴스 생성 완료:', {
    instance: window.spinnerManager,
    methods: Object.getOwnPropertyNames(Object.getPrototypeOf(window.spinnerManager))
});

// 편의 함수들 (기존 코드와의 호환성을 위해)
window.showSpinner = (message, options) => {
    console.log('🔍 DEBUG: showSpinner 호출됨:', { message, options });
    return window.spinnerManager.showGlobal({ message, ...options });
};
window.hideSpinner = (spinnerId) => {
    console.log('🔍 DEBUG: hideSpinner 호출됨:', spinnerId);
    return window.spinnerManager.hide(spinnerId);
};
window.showDataSpinner = (context, message, options) => {
    console.log('🔍 DEBUG: showDataSpinner 호출됨:', { context, message, options });
    return window.spinnerManager.show(context, { message, ...options });
};

console.log('🔍 DEBUG: 전역 스피너 함수들 등록 완료:', {
    showSpinner: typeof window.showSpinner,
    hideSpinner: typeof window.hideSpinner,
    showDataSpinner: typeof window.showDataSpinner
});

// 기존 mainContentLoader와의 호환성
if (!window.mainContentLoader) {
    window.mainContentLoader = {
        show: (message) => window.spinnerManager.showGlobal({ message }),
        hide: () => window.spinnerManager.hideAll(),
        isActive: false
    };
    console.log('🔍 DEBUG: mainContentLoader 생성됨');
}