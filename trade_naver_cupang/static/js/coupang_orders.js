// 쿠팡 주문 관리 JavaScript

// 전역 변수
let currentPage = 1;
let totalPages = 1;
let currentOrders = [];

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
    
    // 전체 선택 체크박스 이벤트
    document.getElementById('selectAll').addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('#ordersTableBody input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
    });
    
    // 초기 데이터 로드
    loadOrders();
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
    currentPage = page;
    
    // 테이블에 로딩 스피너 표시
    const tbody = document.getElementById('ordersTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="13" style="text-align: center; padding: 40px;">
                <div class="loading-spinner" style="margin: 0 auto;"></div>
                <div style="margin-top: 16px; color: #718096;">데이터를 불러오는 중...</div>
            </td>
        </tr>
    `;
    
    const params = new URLSearchParams({
        page: page,
        per_page: 20,
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        status: document.getElementById('orderStatus').value,
        search: document.getElementById('searchText').value
    });
    
    fetch(`/coupang/api/coupang/orders?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayOrders(data.orders);
                updatePagination(data.pagination);
                updateStatistics(data.statistics);
            } else {
                console.error('주문 목록 조회 실패:', data.message);
                showErrorMessage(data.message || '주문 목록을 불러올 수 없습니다.');
                resetStatistics();
                updatePagination({ currentPage: 1, totalPages: 0, totalCount: 0 });
            }
        })
        .catch(error => {
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
        // 빈 데이터도 로딩 완료로 간주
        notifyDataLoadingComplete();
        return;
    }
    
    emptyMessage.style.display = 'none';
    
    orders.forEach(order => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="col-check">
                <div class="checkbox-wrapper">
                    <input type="checkbox" data-shipment-id="${order.shipmentBoxId}">
                </div>
            </td>
            <td class="col-date">${formatDateTime(order.orderedAt)}</td>
            <td class="col-shipment-id">${order.shipmentBoxId}</td>
            <td class="col-order-id">${order.orderId}</td>
            <td class="col-product">${order.orderItems && order.orderItems[0]?.vendorItemName || ''}</td>
            <td class="col-qty">${order.orderItems ? order.orderItems.reduce((sum, item) => sum + item.shippingCount, 0) : 0}</td>
            <td class="col-orderer">${order.orderer?.name || ''}</td>
            <td class="col-receiver">${order.receiver?.name || ''}</td>
            <td class="col-amount">${formatCurrency(order.orderItems ? order.orderItems.reduce((sum, item) => sum + item.orderPrice, 0) : 0)}</td>
            <td class="col-status">${getStatusBadge(order.status)}</td>
            <td class="col-company">${order.deliveryCompanyName || '-'}</td>
            <td class="col-tracking">${order.invoiceNumber || '-'}</td>
            <td class="col-action">
                ${getActionButtons(order)}
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // 데이터 표시 완료 신호
    notifyDataLoadingComplete();
    }
}

// 상태 배지 생성
function getStatusBadge(status) {
    const statusMap = {
        'ACCEPT': { text: '결제완료', class: 'accept' },
        'INSTRUCT': { text: '상품준비중', class: 'instruct' },
        'DEPARTURE': { text: '배송지시', class: 'departure' },
        'DELIVERING': { text: '배송중', class: 'delivering' },
        'FINAL_DELIVERY': { text: '배송완료', class: 'final_delivery' },
        'NONE_TRACKING': { text: '업체직송', class: 'none_tracking' }
    };
    
    const statusInfo = statusMap[status] || { text: status, class: 'default' };
    return `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
}

// 작업 버튼 생성
function getActionButtons(order) {
    let buttons = '';
    
    if (order.status === 'ACCEPT') {
        buttons += `<button class="btn-action" onclick="showAcknowledgeModal('${order.shipmentBoxId}')">발주확인</button> `;
    }
    
    if (order.status === 'INSTRUCT' && !order.invoiceNumber) {
        buttons += `<button class="btn-action" onclick="showShipmentModal('${order.shipmentBoxId}')">송장입력</button>`;
    }
    
    return buttons || '-';
}

// 페이지네이션 업데이트
function updatePagination(pagination) {
    totalPages = pagination.total_pages;
    document.getElementById('totalRecords').textContent = pagination.total_items;
    
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
    document.getElementById('totalOrders').textContent = statistics.total || 0;
    document.getElementById('newOrders').textContent = statistics.new_orders || 0;
    document.getElementById('deliveringOrders').textContent = statistics.delivering || 0;
    document.getElementById('preparingOrders').textContent = statistics.preparing || 0;
}

// 조회 버튼 클릭
function searchOrders() {
    loadOrders(1);
}

// 초기화 버튼 클릭
function resetFilters() {
    document.getElementById('orderStatus').value = '';
    document.getElementById('searchText').value = '';
    
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    document.getElementById('startDate').value = formatDate(thirtyDaysAgo);
    document.getElementById('endDate').value = formatDate(today);
    
    loadOrders(1);
}

// 쿠팡 동기화
function syncOrders() {
    showLoading('쿠팡커머스와 동기화 중...');
    
    fetch('/coupang/api/coupang/sync', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            alert(`동기화 완료!\n조회: ${data.total_count}건\n성공: ${data.success_count}건`);
            loadOrders(currentPage);
        } else {
            alert('동기화 실패: ' + data.message);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('동기화 오류:', error);
        alert('동기화 중 오류가 발생했습니다.');
    });
}

// 엑셀 다운로드
function exportOrders() {
    const params = new URLSearchParams({
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        status: document.getElementById('orderStatus').value,
        search: document.getElementById('searchText').value
    });
    
    window.location.href = `/api/coupang/orders/export?${params}`;
}

// 발주 확인 모달 표시
function showAcknowledgeModal(shipmentBoxId) {
    document.getElementById('modalShipmentBoxId').value = shipmentBoxId;
    document.getElementById('acknowledgeModal').classList.add('active');
}

// 발주 확인 모달 닫기
function closeAcknowledgeModal() {
    document.getElementById('acknowledgeModal').classList.remove('active');
}

// 발주 확인 처리
function acknowledgeOrder() {
    const shipmentBoxId = document.getElementById('modalShipmentBoxId').value;
    
    showLoading('발주 확인 처리 중...');
    
    fetch(`/coupang/api/coupang/orders/${shipmentBoxId}/acknowledge`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            alert('발주 확인이 완료되었습니다.');
            closeAcknowledgeModal();
            loadOrders(currentPage);
        } else {
            alert('발주 확인 실패: ' + data.message);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('발주 확인 오류:', error);
        alert('발주 확인 중 오류가 발생했습니다.');
    });
}

// 송장 입력 모달 표시
function showShipmentModal(shipmentBoxId) {
    document.getElementById('shipmentBoxId').value = shipmentBoxId;
    document.getElementById('invoiceNumber').value = '';
    document.getElementById('shipmentModal').classList.add('active');
}

// 송장 입력 모달 닫기
function closeShipmentModal() {
    document.getElementById('shipmentModal').classList.remove('active');
}

// 송장 정보 저장
function updateShipment() {
    const shipmentBoxId = document.getElementById('shipmentBoxId').value;
    const deliveryCompanyCode = document.getElementById('deliveryCompanyCode').value;
    const invoiceNumber = document.getElementById('invoiceNumber').value;
    
    if (!invoiceNumber) {
        alert('송장번호를 입력해주세요.');
        return;
    }
    
    showLoading('송장 정보 저장 중...');
    
    fetch(`/coupang/api/coupang/orders/${shipmentBoxId}/shipment`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            delivery_company_code: deliveryCompanyCode,
            invoice_number: invoiceNumber
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            alert('송장 정보가 저장되었습니다.');
            closeShipmentModal();
            loadOrders(currentPage);
        } else {
            alert('송장 정보 저장 실패: ' + data.message);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('송장 정보 저장 오류:', error);
        alert('송장 정보 저장 중 오류가 발생했습니다.');
    });
}

// 로딩 표시
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

// 로딩 숨기기
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
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
    document.getElementById('preparingOrders').textContent = '0';
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

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeAcknowledgeModal();
        closeShipmentModal();
    }
});