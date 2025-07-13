// 통합 주문조회 JavaScript

// 전역 변수
let currentPage = 1;
let totalPages = 1;
let currentOrders = [];
let isLoading = false;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 날짜 필터 초기값 설정 (오늘 기준 30일)
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    document.getElementById('startDate').value = formatDate(thirtyDaysAgo);
    document.getElementById('endDate').value = formatDate(today);
    
    // 스피너 완료 조건 설정
    if (window.spinnerManager) {
        // 데이터 로딩 완료 플래그
        window.dataLoadingComplete = false;
        window.statsLoadingComplete = false;
        
        // 테이블 데이터 로딩 완료 조건
        window.spinnerManager.addCompletionCondition(() => {
            const tableBody = document.getElementById('ordersTableBody');
            const emptyMessage = document.getElementById('emptyMessage');
            const loadingSpinner = tableBody ? tableBody.querySelector('.loading-spinner') : null;
            
            // 로딩 스피너가 있으면 아직 로딩 중
            if (loadingSpinner) {
                console.log('🔍 DEBUG: 테이블 로딩 스피너 존재');
                return false;
            }
            
            // 데이터 로딩이 완료되었는지 확인
            if (!window.dataLoadingComplete) {
                console.log('🔍 DEBUG: 데이터 로딩 미완료');
                return false;
            }
            
            if (tableBody) {
                const hasData = tableBody.children.length > 0;
                const hasEmptyMessage = emptyMessage && emptyMessage.style.display !== 'none';
                const hasErrorMessage = emptyMessage && emptyMessage.innerHTML.includes('오류가 발생했습니다');
                
                console.log('🔍 DEBUG: 테이블 상태:', {
                    hasData: hasData,
                    hasEmptyMessage: hasEmptyMessage,
                    hasErrorMessage: hasErrorMessage,
                    dataLoadingComplete: window.dataLoadingComplete
                });
                
                return hasData || hasEmptyMessage || hasErrorMessage;
            }
            return true;
        });
        
        // 통계 카드 로딩 완료 조건
        window.spinnerManager.addCompletionCondition(() => {
            const statsCards = document.querySelector('.stats-cards');
            if (!statsCards) return true;
            
            // 통계 로딩이 완료되었는지 확인
            if (!window.statsLoadingComplete) {
                console.log('🔍 DEBUG: 통계 로딩 미완료');
                return false;
            }
            
            const statValues = statsCards.querySelectorAll('.stat-value');
            const hasStats = Array.from(statValues).some(value => {
                const text = value.textContent.trim();
                return text !== '0' && text !== '₩0' && text !== '';
            });
            
            // 에러가 발생한 경우도 완료로 간주
            const hasError = window.dataLoadingComplete && !hasStats;
            
            console.log('🔍 DEBUG: 통계 상태:', {
                hasStats: hasStats,
                hasError: hasError,
                statsLoadingComplete: window.statsLoadingComplete
            });
            
            return hasStats || hasError;
        });
    }
    
    // 초기 데이터 로드
    loadOrders();
    
    // 엔터키 이벤트 처리
    document.getElementById('searchText').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchOrders();
        }
    });
});

// 날짜 포맷팅
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 날짜/시간 포맷팅
function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}.${month}.${day} ${hours}:${minutes}:${seconds}`;
}

// 금액 포맷팅
function formatCurrency(amount) {
    return new Intl.NumberFormat('ko-KR').format(amount);
}

// 주문 목록 조회
function loadOrders(page = 1) {
    if (isLoading) return;
    
    currentPage = page;
    isLoading = true;
    
    // 로딩 시작 시 플래그 초기화
    window.dataLoadingComplete = false;
    window.statsLoadingComplete = false;
    
    const params = new URLSearchParams({
        page: page,
        per_page: 20,
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        platform: document.getElementById('platform').value,
        status: document.getElementById('orderStatus').value,
        search: document.getElementById('searchText').value
    });
    
    // 로딩 표시
    showTableLoading();
    
    fetch(`/integrated/api/orders?${params}`)
        .then(response => response.json())
        .then(data => {
            isLoading = false;
            if (data.success) {
                displayOrders(data.orders);
                updatePagination(data.pagination);
                updateStatistics(data.statistics);
            } else {
                console.error('주문 목록 조회 실패:', data.message);
                showErrorMessage(data.message || '주문 목록을 불러올 수 없습니다.');
                // 통계 초기화
                resetStatistics();
                updatePagination({ currentPage: 1, totalPages: 0, totalCount: 0 });
            }
        })
        .catch(error => {
            isLoading = false;
            console.error('주문 목록 조회 오류:', error);
            showErrorMessage('서버와의 연결에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.');
            resetStatistics();
            updatePagination({ currentPage: 1, totalPages: 0, totalCount: 0 });
        });
}

// 주문 목록 표시
function displayOrders(orders) {
    currentOrders = orders;
    const tbody = document.getElementById('ordersTableBody');
    const emptyMessage = document.getElementById('emptyMessage');
    
    tbody.innerHTML = '';
    
    if (orders.length === 0) {
        emptyMessage.style.display = 'block';
        // 빈 데이터도 렌더링 완료로 처리
        notifyDataRenderingComplete();
        return;
    }
    
    emptyMessage.style.display = 'none';
    
    orders.forEach((order, index) => {
        const row = document.createElement('tr');
        row.style.setProperty('--row-index', index);  // 애니메이션을 위한 인덱스
        row.innerHTML = `
            <td class="col-platform">${getPlatformBadge(order.platform)}</td>
            <td class="col-date">${formatDateTime(order.orderDate)}</td>
            <td class="col-order-id">${order.orderId}</td>
            <td class="col-platform-order">${order.platformOrderId || '-'}</td>
            <td class="col-product" title="${order.productName || ''}">${order.productName || '-'}</td>
            <td class="col-qty">${order.quantity || 0}</td>
            <td class="col-orderer">${order.ordererName || '-'}</td>
            <td class="col-receiver">${order.receiverName || '-'}</td>
            <td class="col-amount">${formatCurrency(order.orderAmount || 0)}</td>
            <td class="col-status">${getStatusBadge(order.status)}</td>
            <td class="col-company">${order.deliveryCompany || '-'}</td>
            <td class="col-tracking">${order.trackingNumber || '-'}</td>
            <td class="col-address" title="${order.shippingAddress || ''}">${order.shippingAddress || '-'}</td>
        `;
        tbody.appendChild(row);
    });
    
    // 모든 행이 추가된 후 렌더링 완료 알림
    notifyDataRenderingComplete();
}

// 플랫폼 배지 생성
function getPlatformBadge(platform) {
    const platformMap = {
        'NAVER': { text: '네이버', class: 'naver' },
        'COUPANG': { text: '쿠팡', class: 'coupang' }
    };
    
    const platformInfo = platformMap[platform] || { text: platform, class: 'default' };
    return `<span class="platform-badge ${platformInfo.class}">${platformInfo.text}</span>`;
}

// 상태 배지 생성
function getStatusBadge(status) {
    const statusMap = {
        'PAYMENT_WAITING': { text: '결제대기', class: 'payment_waiting' },
        'ACCEPT': { text: '결제완료', class: 'accept' },
        'INSTRUCT': { text: '상품준비중', class: 'instruct' },
        'DEPARTURE': { text: '배송지시', class: 'departure' },
        'DELIVERING': { text: '배송중', class: 'delivering' },
        'FINAL_DELIVERY': { text: '배송완료', class: 'final_delivery' }
    };
    
    const statusInfo = statusMap[status] || { text: status, class: 'default' };
    return `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
}

// 페이지네이션 업데이트
function updatePagination(pagination) {
    totalPages = pagination.total_pages;
    document.getElementById('totalRecords').textContent = pagination.total_items;
    document.getElementById('totalCount').textContent = pagination.total_items;
    
    const paginationControls = document.getElementById('pagination');
    paginationControls.innerHTML = '';
    
    // 데이터가 없는 경우 페이지네이션 비활성화
    const hasData = pagination.total_items > 0;
    
    // 이전 버튼
    const prevBtn = document.createElement('button');
    prevBtn.className = 'pagination-btn';
    prevBtn.textContent = '이전';
    prevBtn.disabled = !hasData || currentPage === 1;
    if (hasData && currentPage > 1) {
        prevBtn.onclick = () => loadOrders(currentPage - 1);
    }
    paginationControls.appendChild(prevBtn);
    
    // 페이지 번호
    if (hasData) {
        const maxButtons = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxButtons - 1);
        
        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = 'pagination-btn';
            if (i === currentPage) {
                pageBtn.classList.add('active');
            }
            pageBtn.textContent = i;
            pageBtn.onclick = () => loadOrders(i);
            paginationControls.appendChild(pageBtn);
        }
    }
    
    // 다음 버튼
    const nextBtn = document.createElement('button');
    nextBtn.className = 'pagination-btn';
    nextBtn.textContent = '다음';
    nextBtn.disabled = !hasData || currentPage === totalPages;
    if (hasData && currentPage < totalPages) {
        nextBtn.onclick = () => loadOrders(currentPage + 1);
    }
    paginationControls.appendChild(nextBtn);
}

// 통계 업데이트
function updateStatistics(statistics) {
    // 전체 통계
    document.getElementById('totalOrders').textContent = statistics.total || 0;
    document.getElementById('newOrders').textContent = statistics.new_orders || 0;
    document.getElementById('deliveringOrders').textContent = statistics.delivering || 0;
    document.getElementById('totalRevenue').textContent = '₩' + formatCurrency(statistics.total_amount || 0);
    
    // 플랫폼별 통계
    document.getElementById('naverTotal').textContent = statistics.naver?.total || 0;
    document.getElementById('coupangTotal').textContent = statistics.coupang?.total || 0;
    
    // 통계 렌더링 완료 알림
    notifyStatsRenderingComplete();
}

// 조회 버튼 클릭
function searchOrders() {
    loadOrders(1);
}

// 초기화 버튼 클릭
function resetFilters() {
    document.getElementById('platform').value = '';
    document.getElementById('orderStatus').value = '';
    document.getElementById('searchText').value = '';
    
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    document.getElementById('startDate').value = formatDate(thirtyDaysAgo);
    document.getElementById('endDate').value = formatDate(today);
    
    loadOrders(1);
}

// 엑셀 다운로드
function exportOrders() {
    const spinnerId = window.spinnerManager ? 
        window.spinnerManager.show('export', {
            message: '엑셀 파일을 생성하는 중...',
            type: 'spin',
            showProgress: true,
            minTime: 2000,
            maxTime: 10000
        }) : null;
    
    if (spinnerId) {
        window.spinnerManager.setProgress(spinnerId, 30, '데이터 수집 중...');
    }
    
    const params = new URLSearchParams({
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        platform: document.getElementById('platform').value,
        status: document.getElementById('orderStatus').value,
        search: document.getElementById('searchText').value
    });
    
    if (spinnerId) {
        window.spinnerManager.setProgress(spinnerId, 70, '파일 생성 중...');
    }
    
    // 다운로드 시작
    window.location.href = `/integrated/api/orders/export?${params}`;
    
    // 다운로드 완료 후 스피너 숨김
    if (spinnerId) {
        setTimeout(() => {
            window.spinnerManager.setProgress(spinnerId, 100, '다운로드 완료!');
            setTimeout(() => window.spinnerManager.hide(spinnerId), 1000);
        }, 2000);
    }
}

// 테이블 로딩 표시
function showTableLoading() {
    const tbody = document.getElementById('ordersTableBody');
    const emptyMessage = document.getElementById('emptyMessage');
    
    // 에러 메시지가 표시되어 있으면 숨기기
    if (emptyMessage) {
        emptyMessage.style.display = 'none';
    }
    
    tbody.innerHTML = `
        <tr>
            <td colspan="13" style="text-align: center; padding: 40px;">
                <div class="loading-spinner" style="margin: 0 auto;"></div>
                <div style="margin-top: 16px; color: #718096;">데이터를 불러오는 중...</div>
            </td>
        </tr>
    `;
}

// 빈 메시지 표시
function showEmptyMessage() {
    const tbody = document.getElementById('ordersTableBody');
    const emptyMessage = document.getElementById('emptyMessage');
    tbody.innerHTML = '';
    emptyMessage.style.display = 'block';
}

// 에러 메시지 표시
function showErrorMessage(message) {
    const tbody = document.getElementById('ordersTableBody');
    const emptyMessage = document.getElementById('emptyMessage');
    
    tbody.innerHTML = '';
    emptyMessage.innerHTML = `
        <svg width="64" height="64" viewBox="0 0 24 24" fill="#ef4444">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        <p style="color: #ef4444; font-weight: 500; margin-top: 16px;">오류가 발생했습니다</p>
        <p style="color: #718096; font-size: 14px; margin-top: 8px;">${message}</p>
        <button class="btn btn-primary" style="margin-top: 16px;" onclick="searchOrders()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 8px;">
                <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
            </svg>
            다시 시도
        </button>
    `;
    emptyMessage.style.display = 'block';
    
    // 에러 상태에서도 렌더링 완료로 처리
    notifyDataRenderingComplete();
}

// 통계 초기화
function resetStatistics() {
    document.getElementById('totalOrders').textContent = '0';
    document.getElementById('naverTotal').textContent = '0';
    document.getElementById('coupangTotal').textContent = '0';
    document.getElementById('newOrders').textContent = '0';
    document.getElementById('deliveringOrders').textContent = '0';
    document.getElementById('totalRevenue').textContent = '₩0';
    document.getElementById('totalCount').textContent = '0';
    document.getElementById('totalRecords').textContent = '0';
}

// 로딩 오버레이 표시
function showLoading(message = '처리 중...') {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'loadingOverlay';
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-message">${message}</div>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
}

// 로딩 오버레이 숨기기
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}


// 자동 새로고침 (5분마다)
setInterval(() => {
    if (!isLoading) {
        loadOrders(currentPage);
    }
}, 300000); // 5분

// 데이터 렌더링 완료 알림 함수
function notifyDataRenderingComplete() {
    // 테이블 행들이 실제로 렌더링되었는지 확인하기 위해 짧은 지연 후 체크
    setTimeout(() => {
        const tbody = document.getElementById('ordersTableBody');
        const rows = tbody ? tbody.querySelectorAll('tr') : [];
        const emptyMessage = document.getElementById('emptyMessage');
        
        console.log('🔍 DEBUG: 테이블 행 렌더링 확인:', {
            rowCount: rows.length,
            firstRowVisible: rows[0]?.offsetHeight > 0,
            emptyMessageVisible: emptyMessage?.style.display !== 'none'
        });
        
        // 애니메이션 완료를 위한 추가 대기
        setTimeout(() => {
            window.dataLoadingComplete = true;
            console.log('🔍 DEBUG: 데이터 렌더링 완료 - dataLoadingComplete = true');
            
            // 스피너 매니저에 직접 완료 체크 요청
            if (window.spinnerManager && window.spinnerManager.checkAutoComplete) {
                const spinnerId = window.spinnerManager.globalSpinner?.id;
                if (spinnerId) {
                    window.spinnerManager.checkAutoComplete(spinnerId);
                }
            }
        }, 100); // 애니메이션을 위한 추가 100ms 대기
    }, 50); // DOM 업데이트를 위한 50ms 대기
}

// 통계 렌더링 완료 알림 함수
function notifyStatsRenderingComplete() {
    // 통계 요소들이 실제로 업데이트되었는지 확인하기 위해 짧은 지연
    setTimeout(() => {
        const statsElements = document.querySelectorAll('.stat-value');
        const hasStats = Array.from(statsElements).some(el => el.textContent !== '0');
        
        console.log('🔍 DEBUG: 통계 렌더링 확인:', {
            elementCount: statsElements.length,
            hasNonZeroValues: hasStats
        });
        
        window.statsLoadingComplete = true;
        console.log('🔍 DEBUG: 통계 렌더링 완료 - statsLoadingComplete = true');
        
        // 스피너 매니저에 직접 완료 체크 요청
        if (window.spinnerManager && window.spinnerManager.checkAutoComplete) {
            const spinnerId = window.spinnerManager.globalSpinner?.id;
            if (spinnerId) {
                window.spinnerManager.checkAutoComplete(spinnerId);
            }
        }
    }, 50); // DOM 업데이트를 위한 50ms 대기
}