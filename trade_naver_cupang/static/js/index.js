
        const searchForm = document.getElementById('searchForm');
        const resultsDiv = document.getElementById('results');
        const loadingDiv = document.getElementById('loading');
        const errorDiv = document.getElementById('error');

        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const keyword = document.getElementById('keyword').value;
            const platform = document.getElementById('platform').value;
            
            // Clear previous results
            resultsDiv.innerHTML = '';
            errorDiv.style.display = 'none';
            loadingDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ keyword, platform }),
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || '검색 중 오류가 발생했습니다.');
                }
                
                displayResults(data.results);
            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.style.display = 'block';
            } finally {
                loadingDiv.style.display = 'none';
            }
        });

        function displayResults(results) {
            if (results.length === 0) {
                resultsDiv.innerHTML = '<p style="text-align: center; width: 100%;">검색 결과가 없습니다.</p>';
                return;
            }
            
            results.forEach(product => {
                const card = document.createElement('div');
                card.className = 'product-card';
                
                const platformClass = product.platform === 'naver' ? 'platform-naver' : 'platform-coupang';
                const platformText = product.platform === 'naver' ? '네이버' : '쿠팡';
                
                card.innerHTML = `
                    <span class="platform-badge ${platformClass}">${platformText}</span>
                    <img src="${product.image_url}" alt="${product.name}" class="product-image" onerror="this.src='https://via.placeholder.com/250x200?text=No+Image'">
                    <div class="product-name">${product.name}</div>
                    <div class="product-price">${product.price.toLocaleString()}원</div>
                    ${product.rating ? `<div>⭐ ${product.rating} (${product.review_count || 0})</div>` : ''}
                    <a href="${product.url}" target="_blank" style="display: inline-block; margin-top: 10px; color: #007bff;">상품 보기 →</a>
                `;
                
                resultsDiv.appendChild(card);
            });
        }
    