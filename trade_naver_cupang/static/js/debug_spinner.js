// 디버그용 스피너 로그
console.log('🔍 DEBUG: debug_spinner.js 로드 시작');
console.log('🔍 DEBUG: 현재 시간:', new Date().toLocaleTimeString());
console.log('🔍 DEBUG: 현재 URL:', window.location.href);

// 원본 함수들을 저장
const originalFunctions = {};

// 페이지 로드 시점 확인
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 DEBUG: DOMContentLoaded 이벤트 발생');
    console.log('🔍 DEBUG: 현재 URL:', window.location.pathname);
    console.log('🔍 DEBUG: showSpinner 함수 존재 여부:', typeof window.showSpinner);
    console.log('🔍 DEBUG: hideSpinner 함수 존재 여부:', typeof window.hideSpinner);
    console.log('🔍 DEBUG: SpinnerManager 존재 여부:', typeof window.spinnerManager);
    console.log('🔍 DEBUG: window.SpinnerManager 클래스 존재 여부:', typeof window.SpinnerManager);
    
    // 사이드바 링크 클릭 이벤트 모니터링
    const sidebarLinks = document.querySelectorAll('.sidebar a[href]');
    console.log('🔍 DEBUG: 사이드바 링크 개수:', sidebarLinks.length);
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            console.log('🔍 DEBUG: 사이드바 링크 클릭됨:', {
                href: this.href,
                text: this.textContent.trim(),
                classList: this.classList.toString(),
                preventDefault: e.defaultPrevented,
                timestamp: new Date().toLocaleTimeString(),
                spinnerManagerExists: !!window.spinnerManager,
                showSpinnerExists: !!window.showSpinner
            });
            
            // 클릭 직후 스피너 상태 확인
            setTimeout(() => {
                console.log('🔍 DEBUG: 클릭 100ms 후 상태:', {
                    spinnerElements: document.querySelectorAll('[id*="spinner"]').length,
                    loadingElements: document.querySelectorAll('.loading, .spinner, .loader').length,
                    bodyClasses: document.body.className
                });
            }, 100);
        });
    });
    
    // 전역 클릭 이벤트 캡처
    document.addEventListener('click', function(e) {
        const target = e.target.closest('a');
        if (target && target.href) {
            console.log('🔍 DEBUG: 전역 클릭 캡처:', {
                href: target.href,
                text: target.textContent.trim(),
                isSidebarLink: target.closest('.sidebar') !== null,
                isMarketplaceLink: target.href.includes('integrated') || 
                                 target.href.includes('naver') || 
                                 target.href.includes('coupang')
            });
        }
    }, true); // 캡처 단계에서 실행
});

// window.showSpinner 함수 감시
if (window.showSpinner) {
    console.log('🔍 DEBUG: showSpinner 함수 발견됨');
    originalFunctions.showSpinner = window.showSpinner;
    window.showSpinner = function(message) {
        console.log('🔍 DEBUG: showSpinner 호출됨:', {
            message: message,
            timestamp: new Date().toLocaleTimeString(),
            callStack: new Error().stack
        });
        const result = originalFunctions.showSpinner.call(this, message);
        console.log('🔍 DEBUG: showSpinner 결과:', result);
        return result;
    };
} else {
    console.log('🔍 DEBUG: ⚠️ showSpinner 함수가 없음');
}

// window.hideSpinner 함수 감시
if (window.hideSpinner) {
    console.log('🔍 DEBUG: hideSpinner 함수 발견됨');
    originalFunctions.hideSpinner = window.hideSpinner;
    window.hideSpinner = function() {
        console.log('🔍 DEBUG: hideSpinner 호출됨:', {
            timestamp: new Date().toLocaleTimeString(),
            callStack: new Error().stack
        });
        const result = originalFunctions.hideSpinner.call(this);
        console.log('🔍 DEBUG: hideSpinner 결과:', result);
        return result;
    };
} else {
    console.log('🔍 DEBUG: ⚠️ hideSpinner 함수가 없음');
}

// SpinnerManager 감시
if (window.spinnerManager) {
    console.log('🔍 DEBUG: spinnerManager 인스턴스 발견됨');
    console.log('🔍 DEBUG: spinnerManager 메서드들:', Object.getOwnPropertyNames(Object.getPrototypeOf(window.spinnerManager)));
    
    if (window.spinnerManager.showGlobal) {
        originalFunctions.showGlobal = window.spinnerManager.showGlobal;
        window.spinnerManager.showGlobal = function(options) {
            console.log('🔍 DEBUG: spinnerManager.showGlobal 호출됨:', {
                options: options,
                timestamp: new Date().toLocaleTimeString(),
                currentSpinners: this.spinners ? Object.keys(this.spinners) : 'N/A'
            });
            const result = originalFunctions.showGlobal.call(this, options);
            console.log('🔍 DEBUG: showGlobal 결과:', result);
            return result;
        };
    }
    
    if (window.spinnerManager.hide) {
        originalFunctions.hide = window.spinnerManager.hide;
        window.spinnerManager.hide = function(spinnerId) {
            console.log('🔍 DEBUG: spinnerManager.hide 호출됨:', {
                spinnerId: spinnerId,
                timestamp: new Date().toLocaleTimeString(),
                currentSpinners: this.spinners ? Object.keys(this.spinners) : 'N/A'
            });
            const result = originalFunctions.hide.call(this, spinnerId);
            console.log('🔍 DEBUG: hide 결과:', result);
            return result;
        };
    }
    
    if (window.spinnerManager.hideAll) {
        originalFunctions.hideAll = window.spinnerManager.hideAll;
        window.spinnerManager.hideAll = function() {
            console.log('🔍 DEBUG: spinnerManager.hideAll 호출됨:', {
                timestamp: new Date().toLocaleTimeString(),
                currentSpinners: this.spinners ? Object.keys(this.spinners) : 'N/A',
                callStack: new Error().stack
            });
            const result = originalFunctions.hideAll.call(this);
            console.log('🔍 DEBUG: hideAll 결과:', result);
            return result;
        };
    }
} else {
    console.log('🔍 DEBUG: ⚠️ spinnerManager가 없음');
}

// 스피너 엘리먼트 변화 감시
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) { // Element node
                    if (node.id && node.id.includes('spinner')) {
                        console.log('🔍 DEBUG: 스피너 엘리먼트 추가됨:', node.id);
                    }
                    if (node.classList && (
                        node.classList.contains('spinner') ||
                        node.classList.contains('loading') ||
                        node.classList.contains('loader')
                    )) {
                        console.log('🔍 DEBUG: 로딩 관련 엘리먼트 추가됨:', node.className);
                    }
                }
            });
            
            mutation.removedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    if (node.id && node.id.includes('spinner')) {
                        console.log('🔍 DEBUG: 스피너 엘리먼트 제거됨:', node.id);
                    }
                }
            });
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['class', 'style']
});

// 스피너 관련 요소의 스타일 변경 감시
const styleObserver = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'attributes' && mutation.target.id && mutation.target.id.includes('spinner')) {
            console.log('🔍 DEBUG: 스피너 스타일 변경:', {
                id: mutation.target.id,
                attribute: mutation.attributeName,
                oldValue: mutation.oldValue,
                newValue: mutation.target.getAttribute(mutation.attributeName)
            });
        }
    });
});

styleObserver.observe(document.body, {
    subtree: true,
    attributes: true,
    attributeOldValue: true,
    attributeFilter: ['style', 'class']
});

// 페이지 이동 감지
let lastUrl = location.href; 
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        console.log('🔍 DEBUG: URL 변경 감지:', url);
    }
}).observe(document, {subtree: true, childList: true});

// 모든 스크립트 로드 상태 확인
window.addEventListener('load', function() {
    console.log('🔍 DEBUG: 페이지 완전 로드됨');
    console.log('🔍 DEBUG: 로드된 스크립트들:', 
        Array.from(document.scripts).map(s => s.src || 'inline').filter(s => s.includes('.js'))
    );
    console.log('🔍 DEBUG: window.load 시점 스피너 상태:', {
        showSpinner: typeof window.showSpinner,
        hideSpinner: typeof window.hideSpinner,
        SpinnerManager: typeof window.SpinnerManager,
        spinnerManager: typeof window.spinnerManager,
        spinnerManagerMethods: window.spinnerManager ? Object.getOwnPropertyNames(Object.getPrototypeOf(window.spinnerManager)) : 'N/A'
    });
});

// 페이지 언로드 감지
window.addEventListener('beforeunload', function(e) {
    console.log('🔍 DEBUG: 페이지 언로드 시작:', {
        timestamp: new Date().toLocaleTimeString(),
        currentURL: window.location.href,
        activeSpinners: document.querySelectorAll('[id*="spinner"]').length
    });
});

// AJAX 요청 감지
const originalFetch = window.fetch;
window.fetch = function(...args) {
    console.log('🔍 DEBUG: fetch 요청:', {
        url: args[0],
        method: args[1]?.method || 'GET',
        timestamp: new Date().toLocaleTimeString()
    });
    
    return originalFetch.apply(this, args).then(response => {
        console.log('🔍 DEBUG: fetch 응답:', {
            url: args[0],
            status: response.status,
            timestamp: new Date().toLocaleTimeString()
        });
        return response;
    }).catch(error => {
        console.log('🔍 DEBUG: fetch 오류:', {
            url: args[0],
            error: error.message,
            timestamp: new Date().toLocaleTimeString()
        });
        throw error;
    });
};

console.log('🔍 DEBUG: debug_spinner.js 설정 완료');