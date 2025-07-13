
        function searchOrders() {
    // 검색 로직 구현
    console.log('배송 검색 실행');
}

function resetFilters() {
    // 필터 초기화
    document.getElementById('dateFilter').value = 'all';
    document.getElementById('typeFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('paymentFilter').value = '';
    document.getElementById('trackingNumber').value = '';
    document.getElementById('flagFilter').checked = false;
}

function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => cb.checked = selectAll.checked);
}

// 페이지 버튼 클릭 이벤트
document.querySelectorAll('.page-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (!this.disabled) {
            document.querySelector('.page-btn.active').classList.remove('active');
            this.classList.add('active');
        }
    });
});
    