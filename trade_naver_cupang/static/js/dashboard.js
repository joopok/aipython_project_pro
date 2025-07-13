
        function showOrderDetail() {
    document.getElementById('orderDetailModal').classList.add('active');
}

function closeOrderDetail() {
    document.getElementById('orderDetailModal').classList.remove('active');
}

// 모달 외부 클릭시 닫기
document.getElementById('orderDetailModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeOrderDetail();
    }
});
    