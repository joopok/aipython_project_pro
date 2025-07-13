
        function searchOrders() {
    // 검색 로직 구현
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const platform = document.getElementById('platformFilter').value;
    const status = document.getElementById('statusFilter').value;
    
    console.log('검색 조건:', { startDate, endDate, platform, status });
    // 실제 검색 API 호출
}

// 엑셀 다운로드
document.querySelector('.action-btn.excel').addEventListener('click', function() {
    // 엑셀 다운로드 로직
    alert('엑셀 파일을 다운로드합니다.');
});

// 페이지 버튼 클릭 이벤트
document.querySelectorAll('.page-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (!this.disabled) {
            document.querySelector('.page-btn.active').classList.remove('active');
            this.classList.add('active');
        }
    });
});
    