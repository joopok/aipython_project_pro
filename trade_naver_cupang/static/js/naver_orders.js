// 네이버 주문 관리 페이지 JavaScript

// 전역 변수
let currentPage = 1;
let currentFilters = {};
let selectedOrders = new Set();

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 스피너 완료 조건 설정
    if (window.spinnerManager) {
        // 테이블 데이터 로딩 완료 조건
        window.spinnerManager.addCompletionCondition(() => {
            const tableBody = document.getElementById('ordersTableBody');
            const emptyMessage = document.getElementById('emptyMessage');
            const loadingSpinner = tableBody ? tableBody.querySelector('.loading-spinner') : null;
            
            if (loadingSpinner) return false;
            
            if (tableBody) {
                const hasData = tableBody.children.length > 0;
                const hasEmptyMessage = emptyMessage && emptyMessage.style.display !== 'none';
                return hasData || hasEmptyMessage;
            }
            return true;
        });
        
        // 통계 카드 로딩 완료 조건
        window.spinnerManager.addCompletionCondition(() => {
            const statsCards = document.querySelector('.stats-cards');
            if (!statsCards) return true;
            
            const statValues = statsCards.querySelectorAll('.stat-value');
            return Array.from(statValues).some(value => {
                const text = value.textContent.trim();
                return text !== '0' && text !== '';
            });
        });
    }
    
    initializePage();
});

// 페이지 초기화
function initializePage() {
    
    // 날짜 필터 기본값 설정 (최근 7일)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);
    
    document.getElementById('startDate').value = formatDate(startDate);
    document.getElementById('endDate').value = formatDate(endDate);
    
    // 전체 선택 체크박스 이벤트
    document.getElementById('selectAll').addEventListener('change', handleSelectAll);
    
    // 엔터키 검색 이벤트
    document.getElementById('searchText').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchOrders();
        }
    });
    
    // 초기 데이터 로드
    loadOrders();
    loadStatistics();
}

// 날짜 포맷 (YYYY-MM-DD)
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 날짜시간 포맷 (YYYY.MM.DD HH:MM)
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}.${month}.${day} ${hours}:${minutes}`;
}

// 금액 포맷 (천단위 콤마)
function formatCurrency(amount) {
    if (!amount) return '0';
    return Number(amount).toLocaleString('ko-KR') + '원';
}

// 주문 목록 조회
async function loadOrders(page = 1) {
    try {
        currentPage = page;
        
        // 테이블에 로딩 스피너 표시
        const tbody = document.getElementById('ordersTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="11" style="text-align: center; padding: 40px;">
                    <div class="loading-spinner" style="margin: 0 auto;"></div>
                    <div style="margin-top: 16px; color: #718096;">데이터를 불러오는 중...</div>
                </td>
            </tr>
        `;
        
        // 필터 값 수집
        currentFilters = {
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value,
            status: document.getElementById('orderStatus').value,
            search: document.getElementById('searchText').value,
            page: page,
            size: 20
        };
        
        // API 호출
        const response = await fetch('/naver/api/orders?' + new URLSearchParams(currentFilters));
        const data = await response.json();
        
        if (data.success) {
            renderOrderTable(data.data);
            renderPagination(data.pages, data.current_page);
            document.getElementById('totalCount').textContent = data.total;
            
            // 빈 상태 표시/숨김
            const emptyMessage = document.getElementById('emptyMessage');
            const tableWrapper = document.querySelector('.excel-table-wrapper');
            
            if (data.total === 0) {
                if (emptyMessage) emptyMessage.style.display = 'block';
                // 테이블은 숨기지 않고 tbody만 비움
                const tbody = document.getElementById('ordersTableBody');
                if (tbody) tbody.innerHTML = '';
            } else {
                if (emptyMessage) emptyMessage.style.display = 'none';
                if (tableWrapper) tableWrapper.style.display = 'block';
            }
        } else {
            console.error('주문 목록 조회 실패:', data.message);
            showErrorMessage(data.message || '주문 목록을 불러올 수 없습니다.');
            resetStatistics();
            renderPagination(0, 1);
            document.getElementById('totalCount').textContent = '0';
        }
    } catch (error) {
        console.error('주문 목록 조회 오류:', error);
        showErrorMessage('서버와의 연결에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.');
        resetStatistics();
        renderPagination(0, 1);
        document.getElementById('totalCount').textContent = '0';
    }
}

// 주문 테이블 렌더링
function renderOrderTable(orders) {
    const tbody = document.getElementById('ordersTableBody');
    tbody.innerHTML = '';
    
    orders.forEach(order => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="col-check">
                <div class="checkbox-wrapper">
                    <input type="checkbox" class="order-checkbox" value="${order.product_order_id}">
                </div>
            </td>
            <td class="col-date">${formatDateTime(order.order.order_date)}</td>
            <td class="col-order-no">
                <a href="/naver/orders/${order.product_order_id}">
                    ${order.product_order_id}
                </a>
            </td>
            <td class="col-product" style="text-align: left;">${order.product_name || '-'}</td>
            <td class="col-option" style="text-align: left;">${order.product_option || '-'}</td>
            <td class="col-qty" style="text-align: right;">${order.quantity || 1}</td>
            <td class="col-orderer">${order.order.orderer_name || '-'}</td>
            <td class="col-amount" style="text-align: right;">${formatCurrency(order.total_product_amount)}</td>
            <td class="col-status">
                <span class="status-badge ${getStatusClass(order.product_order_status)}">
                    ${getStatusText(order.product_order_status)}
                </span>
            </td>
            <td class="col-tracking">${order.tracking_number || '-'}</td>
            <td class="col-action">
                <button class="action-btn-sm" onclick="openStatusModal('${order.product_order_id}')" title="상태 변경">
                    상태변경
                </button>
                <button class="action-btn-sm" onclick="openTrackingModal('${order.product_order_id}')" title="송장 입력">
                    송장입력
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // 체크박스 이벤트 재설정
    document.querySelectorAll('.order-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleOrderSelect);
    });
    
    // 데이터 로딩 완료 신호
    notifyDataLoadingComplete();
    }
}

// 상태별 CSS 클래스
function getStatusClass(status) {
    const statusMap = {
        'PAYED': 'payed',
        'DELIVERING': 'delivering',
        'DELIVERED': 'delivered',
        'PURCHASE_DECIDED': 'purchase-decided',
        'CANCELED': 'canceled',
        'RETURNED': 'returned',
        'EXCHANGED': 'exchanged'
    };
    return statusMap[status] || '';
}

// 상태 텍스트 변환
function getStatusText(status) {
    const statusMap = {
        'PAYED': '결제완료',
        'DELIVERING': '배송중',
        'DELIVERED': '배송완료',
        'PURCHASE_DECIDED': '구매확정',
        'CANCELED': '취소',
        'RETURNED': '반품',
        'EXCHANGED': '교환'
    };
    return statusMap[status] || status;
}

// 페이지네이션 렌더링
function renderPagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    // 페이지네이션 정보 업데이트
    const totalRecords = document.getElementById('totalRecords');
    if (totalRecords) {
        totalRecords.textContent = document.getElementById('totalCount').textContent;
    }
    
    // 데이터가 없는 경우 페이지네이션 비활성화
    const hasData = parseInt(document.getElementById('totalCount').textContent) > 0;
    
    // 이전 버튼
    const prevBtn = document.createElement('button');
    prevBtn.className = 'page-btn';
    prevBtn.innerHTML = '&laquo;';
    prevBtn.disabled = !hasData || currentPage === 1;
    if (hasData && currentPage > 1) {
        prevBtn.onclick = () => loadOrders(currentPage - 1);
    }
    pagination.appendChild(prevBtn);
    
    // 페이지 번호
    if (hasData) {
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, startPage + 4);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = 'page-btn';
            pageBtn.textContent = i;
            pageBtn.classList.toggle('active', i === currentPage);
            pageBtn.onclick = () => loadOrders(i);
            pagination.appendChild(pageBtn);
        }
    }
    
    // 다음 버튼
    const nextBtn = document.createElement('button');
    nextBtn.className = 'page-btn';
    nextBtn.innerHTML = '&raquo;';
    nextBtn.disabled = !hasData || currentPage === totalPages;
    if (hasData && currentPage < totalPages) {
        nextBtn.onclick = () => loadOrders(currentPage + 1);
    }
    pagination.appendChild(nextBtn);
}

// 통계 정보 로드
async function loadStatistics() {
    try {
        const filters = {
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value
        };
        
        // 전체 주문
        const totalResponse = await fetch('/naver/api/orders?' + new URLSearchParams({...filters, size: 1}));
        const totalData = await totalResponse.json();
        if (totalData.success) {
            document.getElementById('totalOrders').textContent = totalData.total;
        }
        
        // 신규 주문 (결제완료)
        const newResponse = await fetch('/naver/api/orders?' + new URLSearchParams({...filters, status: 'PAYED', size: 1}));
        const newData = await newResponse.json();
        if (newData.success) {
            document.getElementById('newOrders').textContent = newData.total;
        }
        
        // 배송중
        const deliveringResponse = await fetch('/naver/api/orders?' + new URLSearchParams({...filters, status: 'DELIVERING', size: 1}));
        const deliveringData = await deliveringResponse.json();
        if (deliveringData.success) {
            document.getElementById('deliveringOrders').textContent = deliveringData.total;
        }
        
        // 클레임 (취소+반품+교환)
        // TODO: 클레임 통계 API 필요
        document.getElementById('claimOrders').textContent = '0';
        
    } catch (error) {
        console.error('통계 로드 실패:', error);
    }
}

// 검색
function searchOrders() {
    loadOrders(1);
    loadStatistics();
}

// 필터 초기화
function resetFilters() {
    document.getElementById('orderStatus').value = '';
    document.getElementById('searchText').value = '';
    
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);
    
    document.getElementById('startDate').value = formatDate(startDate);
    document.getElementById('endDate').value = formatDate(endDate);
    
    searchOrders();
}

// 주문 동기화
async function syncOrders() {
    if (!confirm('네이버커머스 주문을 동기화하시겠습니까?')) {
        return;
    }
    
    try {
        showLoading('주문 동기화 중...');
        
        const response = await fetch('/naver/api/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ hours: 24 })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            showSuccess(data.message);
            loadOrders(currentPage);
            loadStatistics();
        } else {
            showError('동기화 실패: ' + data.message);
        }
    } catch (error) {
        hideLoading();
        showError('동기화 중 오류가 발생했습니다.');
        console.error(error);
    }
}

// 엑셀 다운로드
async function exportOrders() {
    try {
        showLoading('엑셀 파일 생성 중...');
        
        // TODO: 엑셀 다운로드 API 구현
        hideLoading();
        showInfo('엑셀 다운로드 기능은 준비 중입니다.');
        
    } catch (error) {
        hideLoading();
        showError('엑셀 다운로드 중 오류가 발생했습니다.');
        console.error(error);
    }
}

// 전체 선택/해제
function handleSelectAll(event) {
    const isChecked = event.target.checked;
    document.querySelectorAll('.order-checkbox').forEach(checkbox => {
        checkbox.checked = isChecked;
        if (isChecked) {
            selectedOrders.add(checkbox.value);
        } else {
            selectedOrders.delete(checkbox.value);
        }
    });
}

// 개별 주문 선택
function handleOrderSelect(event) {
    const orderId = event.target.value;
    if (event.target.checked) {
        selectedOrders.add(orderId);
    } else {
        selectedOrders.delete(orderId);
    }
    
    // 전체 선택 체크박스 상태 업데이트
    const allCheckboxes = document.querySelectorAll('.order-checkbox');
    const checkedCount = document.querySelectorAll('.order-checkbox:checked').length;
    document.getElementById('selectAll').checked = checkedCount === allCheckboxes.length;
}

// 상태 변경 모달 열기
function openStatusModal(productOrderId) {
    document.getElementById('modalOrderId').value = productOrderId;
    document.getElementById('statusModal').classList.add('show');
}

// 상태 변경 모달 닫기
function closeStatusModal() {
    document.getElementById('statusModal').classList.remove('show');
}

// 주문 상태 변경
async function updateOrderStatus() {
    const productOrderId = document.getElementById('modalOrderId').value;
    const status = document.getElementById('modalStatus').value;
    
    try {
        showLoading('상태 변경 중...');
        
        const response = await fetch(`/naver/api/orders/${productOrderId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            showSuccess('주문 상태가 변경되었습니다.');
            closeStatusModal();
            loadOrders(currentPage);
        } else {
            showError('상태 변경 실패: ' + data.message);
        }
    } catch (error) {
        hideLoading();
        showError('상태 변경 중 오류가 발생했습니다.');
        console.error(error);
    }
}

// 송장 입력 모달 열기
function openTrackingModal(productOrderId) {
    document.getElementById('trackingOrderId').value = productOrderId;
    document.getElementById('trackingModal').classList.add('show');
}

// 송장 입력 모달 닫기
function closeTrackingModal() {
    document.getElementById('trackingModal').classList.remove('show');
}

// 송장 정보 업데이트
async function updateTracking() {
    const productOrderId = document.getElementById('trackingOrderId').value;
    const deliveryCompany = document.getElementById('deliveryCompany').value;
    const trackingNumber = document.getElementById('trackingNumber').value;
    
    if (!trackingNumber) {
        showError('송장번호를 입력해주세요.');
        return;
    }
    
    try {
        showLoading('송장 정보 저장 중...');
        
        const response = await fetch(`/naver/api/orders/${productOrderId}/tracking`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                delivery_company: deliveryCompany,
                tracking_number: trackingNumber
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            showSuccess('송장 정보가 저장되었습니다.');
            closeTrackingModal();
            loadOrders(currentPage);
        } else {
            showError('송장 정보 저장 실패: ' + data.message);
        }
    } catch (error) {
        hideLoading();
        showError('송장 정보 저장 중 오류가 발생했습니다.');
        console.error(error);
    }
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('show');
    }
});

// 로딩 표시
function showLoading(message = '처리 중...') {
    // 로딩 오버레이 생성
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

// 로딩 숨김
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// 성공 메시지
function showSuccess(message) {
    alert('✓ ' + message);
}

// 오류 메시지
function showError(message) {
    alert('⚠️ ' + message);
}

// 정보 메시지
function showInfo(message) {
    alert('ℹ️ ' + message);
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
}

// 통계 초기화
function resetStatistics() {
    document.getElementById('totalOrders').textContent = '0';
    document.getElementById('newOrders').textContent = '0';
    document.getElementById('deliveringOrders').textContent = '0';
    document.getElementById('claimOrders').textContent = '0';
    document.getElementById('totalCount').textContent = '0';
    document.getElementById('totalRecords').textContent = '0';
}

// 데이터 로딩 완료 알림
function notifyDataLoadingComplete() {
    // 스피너 매니저에 데이터 로딩 완료 알림
    if (window.spinnerManager && window.spinnerManager.notifyDataReady) {
        window.spinnerManager.notifyDataReady();
    }
}