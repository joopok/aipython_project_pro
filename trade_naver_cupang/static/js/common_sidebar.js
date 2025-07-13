function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

function toggleSubmenu(event, submenuId) {
    event.preventDefault();
    event.stopPropagation();
    
    const menuItem = event.currentTarget;
    const submenu = document.getElementById(submenuId);
    
    if (!submenu) {
        console.error('Submenu not found:', submenuId);
        return;
    }
    
    // 강제로 스타일 재계산
    submenu.style.display = 'block';
    submenu.offsetHeight; // 리플로우 강제
    submenu.style.display = '';
    
    // 현재 메뉴 토글
    menuItem.classList.toggle('expanded');
    submenu.classList.toggle('expanded');
    
    // 열려있는 메뉴들의 상태를 localStorage에 저장
    const expandedMenus = [];
    document.querySelectorAll('.submenu.expanded').forEach(menu => {
        if (menu.id) {
            expandedMenus.push(menu.id);
        }
    });
    localStorage.setItem('sidebarMenuState', JSON.stringify(expandedMenus));
}

// 페이지 로드 시 현재 페이지에 해당하는 메뉴 열기
document.addEventListener('DOMContentLoaded', function() {
    // 현재 URL 경로 가져오기
    const currentPath = window.location.pathname;
    
    // 로그인 후 첫 진입인지 확인 (대시보드 페이지이고 메뉴 상태가 없는 경우)
    const isFirstLogin = currentPath === '/dashboard' && !localStorage.getItem('sidebarMenuState');
    
    if (isFirstLogin) {
        // 첫 로그인 시 모든 메뉴 닫기
        localStorage.setItem('sidebarMenuState', JSON.stringify([]));
        localStorage.setItem('allMenusExpanded', 'false');
    } else {
        // localStorage에서 메뉴 상태 복원 (이미 인라인 스크립트에서 CSS 적용됨)
        const menuState = localStorage.getItem('sidebarMenuState');
        if (menuState) {
            const state = JSON.parse(menuState);
            state.forEach(menuId => {
                const submenu = document.getElementById(menuId);
                const menuItem = submenu?.previousElementSibling;
                if (submenu && menuItem && menuItem.classList.contains('has-submenu')) {
                    // 클래스만 추가 (CSS는 이미 적용됨)
                    submenu.classList.add('expanded');
                    menuItem.classList.add('expanded');
                }
            });
        }
    }
    
    // 모든 서브메뉴 아이템 확인
    const submenuItems = document.querySelectorAll('.submenu-item');
    submenuItems.forEach(item => {
        // 클릭 이벤트 전파 방지 (href="#"인 경우에만)
        item.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
            }
            e.stopPropagation();
        });
        
        // 현재 페이지에 해당하는 메뉴 찾기
        const href = item.getAttribute('href');
        if (href && href !== '#') {
            // Flask의 url_for로 생성된 경로와 현재 경로 비교
            const hrefPath = new URL(href, window.location.origin).pathname;
            if (currentPath === hrefPath) {
                // 활성 메뉴 표시
                item.classList.add('active');
                
                // 부모 서브메뉴가 아직 열려있지 않다면 열기
                const parentSubmenu = item.closest('.submenu');
                if (parentSubmenu && !parentSubmenu.classList.contains('expanded')) {
                    parentSubmenu.classList.add('expanded');
                    
                    // 부모 메뉴 아이템도 열기
                    const parentMenuItem = parentSubmenu.previousElementSibling;
                    if (parentMenuItem && parentMenuItem.classList.contains('has-submenu')) {
                        parentMenuItem.classList.add('expanded');
                    }
                    
                    // 상태 저장
                    const expandedMenus = [];
                    document.querySelectorAll('.submenu.expanded').forEach(menu => {
                        if (menu.id) {
                            expandedMenus.push(menu.id);
                        }
                    });
                    localStorage.setItem('sidebarMenuState', JSON.stringify(expandedMenus));
                }
            }
        }
    });
    
    // 메인 메뉴 아이템도 확인
    const menuItems = document.querySelectorAll('.menu-item:not(.has-submenu)');
    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && href !== '#') {
            const hrefPath = new URL(href, window.location.origin).pathname;
            if (currentPath === hrefPath) {
                item.classList.add('active');
            }
        }
    });
    
    // 전체 메뉴 토글 버튼 상태 업데이트
    const allMenusExpanded = localStorage.getItem('allMenusExpanded');
    if (allMenusExpanded === 'true') {
        const toggleIcon = document.getElementById('menuToggleIcon');
        const toggleText = document.getElementById('menuToggleText');
        if (toggleIcon && toggleText) {
            toggleIcon.innerHTML = '<path d="M7 14l5-5 5 5z"/>';
            toggleText.textContent = '닫기';
        }
    }
    
    // 초기화 완료 표시
    setTimeout(() => {
        document.getElementById('sidebar').classList.add('initialized');
    }, 100);
    
    // 사이드바 메뉴 링크에 클릭 이벤트 등록
    const sidebarLinks = document.querySelectorAll('.sidebar a[href]:not([href="#"])');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', handleMenuClick);
    });
});

function toggleAllMenus() {
    console.log('toggleAllMenus called');
    const allSubmenus = document.querySelectorAll('.submenu');
    const allMenuItems = document.querySelectorAll('.menu-item.has-submenu');
    const toggleIcon = document.getElementById('menuToggleIcon');
    const toggleText = document.getElementById('menuToggleText');
    
    console.log('Found submenus:', allSubmenus.length);
    console.log('Found menu items:', allMenuItems.length);
    
    // 현재 상태 확인 (하나라도 펼쳐져 있으면 모두 닫기, 모두 닫혀있으면 모두 펼치기)
    const hasExpanded = Array.from(allSubmenus).some(submenu => submenu.classList.contains('expanded'));
    console.log('Has expanded menus:', hasExpanded);
    
    if (!hasExpanded) {
        // 모든 메뉴 펼치기
        allSubmenus.forEach(submenu => {
            submenu.classList.add('expanded');
        });
        allMenuItems.forEach(item => {
            item.classList.add('expanded');
        });
        toggleIcon.innerHTML = '<path d="M7 14l5-5 5 5z"/>';
        toggleText.textContent = '닫기';
        
        // 열려있는 모든 메뉴 ID를 저장
        const expandedMenus = [];
        allSubmenus.forEach(menu => {
            if (menu.id) {
                expandedMenus.push(menu.id);
            }
        });
        localStorage.setItem('sidebarMenuState', JSON.stringify(expandedMenus));
        localStorage.setItem('allMenusExpanded', 'true');
    } else {
        // 모든 메뉴 닫기
        allSubmenus.forEach(submenu => {
            submenu.classList.remove('expanded');
        });
        allMenuItems.forEach(item => {
            item.classList.remove('expanded');
        });
        toggleIcon.innerHTML = '<path d="M7 10l5 5 5-5z"/>';
        toggleText.textContent = '펼치기';
        
        // 상태 초기화
        localStorage.setItem('sidebarMenuState', JSON.stringify([]));
        localStorage.setItem('allMenusExpanded', 'false');
    }
}



function handleMenuClick(event) {
    // 기본 링크 동작을 막아 페이지 이동을 방지 (디버깅용)
    event.preventDefault();
    console.log("[Debug] 0. handleMenuClick 시작:", {
        timestamp: new Date().toLocaleTimeString(),
        target: event.target,
        targetHref: event.target.getAttribute('href'),
        currentURL: window.location.href,
        clickCount: window.menuClickCount = (window.menuClickCount || 0) + 1
    });

    const target = event.target.closest('a');
    if (!target) {
        console.log("[Debug] target이 없음");
        return;
    }

    const href = target.getAttribute('href');
    console.log("[Debug] 1. href 확인:", href);

    if (!href || href === '#' || href.startsWith('http') || href.startsWith('mailto:')) {
        console.log("[Debug] href 무효:", href);
        return;
    }

    const currentPath = window.location.pathname;
    const targetPath = new URL(href, window.location.origin).pathname;
    console.log("[Debug] 2. 경로 비교:", {
        currentPath: currentPath,
        targetPath: targetPath,
        같은페이지: currentPath === targetPath
    });

    if (currentPath === targetPath) {
        console.log("[Debug] 같은 페이지라서 리턴");
        return;
    }

    const menuText = target.textContent.trim();
    const message = menuText ? `${menuText} 페이지 로딩 중...` : '페이지를 불러오는 중...';

    console.log("[Debug] 3. 스피너 호출 직전 상태:", {
        spinnerManagerExists: !!window.spinnerManager,
        spinnerManagerType: typeof window.spinnerManager,
        spinnerManagerMethods: window.spinnerManager ? Object.getOwnPropertyNames(Object.getPrototypeOf(window.spinnerManager)) : 'N/A',
        spinners: window.spinnerManager?.spinners ? Object.keys(window.spinnerManager.spinners) : 'N/A',
        completionConditions: window.spinnerManager?.completionConditions?.length || 0,
        message: message
    });

    if (window.spinnerManager) {
        console.log("[Debug] 4a. spinnerManager.showGlobal 호출 시작");
        try {
            const result = window.spinnerManager.showGlobal({
                message: message,
                showProgress: true,
                autoComplete: true
            });
            console.log("[Debug] 4b. showGlobal 호출 결과:", result);
            
            // 스피너 상태 확인
            setTimeout(() => {
                console.log("[Debug] 5. 스피너 호출 후 100ms 상태:", {
                    spinners: window.spinnerManager?.spinners ? Object.keys(window.spinnerManager.spinners) : 'N/A',
                    spinnerElements: document.querySelectorAll('[id*="spinner"]').length,
                    loadingElements: document.querySelectorAll('.loading, .spinner, .loader').length
                });
            }, 100);
        } catch (error) {
            console.error("[Debug] 4c. showGlobal 호출 중 에러:", error);
        }
    } else {
        console.error("[Debug] 0b. spinnerManager를 찾을 수 없습니다:", {
            window객체들: Object.keys(window).filter(key => key.toLowerCase().includes('spinner')),
            SpinnerManager타입: typeof window.SpinnerManager
        });
    }

    // 2초 후 수동으로 페이지 이동 (디버깅용)
    setTimeout(() => {
        console.log(`[Debug] 6. 2초 후 페이지 이동 실행:`, {
            href: href,
            timestamp: new Date().toLocaleTimeString(),
            현재스피너상태: window.spinnerManager?.spinners ? Object.keys(window.spinnerManager.spinners) : 'N/A'
        });
        window.location.href = href;
    }, 2000);
}