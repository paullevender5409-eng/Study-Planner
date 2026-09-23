/**
 * Smart Study Planner - Client-side Interactions
 * Mobile Navigation, Drawer Controls & Micro-interactions
 */

document.addEventListener('DOMContentLoaded', function () {

    // =============================================
    // Mobile Drawer & Bottom Nav "More" Trigger
    // =============================================
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const mobileToggle = document.getElementById('mobileSidebarToggle');
    const sidebarClose = document.getElementById('sidebarToggle');
    const mobileMoreBtn = document.getElementById('mobileMoreBtn');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('open');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (mobileToggle) mobileToggle.addEventListener('click', openSidebar);
    if (mobileMoreBtn) mobileMoreBtn.addEventListener('click', openSidebar);
    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    if (overlay) overlay.addEventListener('click', closeSidebar);

    // =============================================
    // Auto-Scroll Active Swipeable Chip into View
    // =============================================
    const activeChip = document.querySelector('.swipeable-chips .count-chip.active');
    if (activeChip) {
        activeChip.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }

    // =============================================
    // Auto-dismiss Alerts
    // =============================================
    const alerts = document.querySelectorAll('.modern-alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // =============================================
    // Highlight Active Route in Desktop and Mobile Nav
    // =============================================
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link, .mobile-bottom-nav .mobile-nav-item').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && href !== '#' && (currentPath === href || (href !== '/' && currentPath.startsWith(href)))) {
            link.classList.add('active');
        }
    });

    // =============================================
    // Confirm Actions
    // =============================================
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const msg = form.dataset.confirm || 'Are you sure you want to proceed?';
            if (!confirm(msg)) e.preventDefault();
        });
    });

    // =============================================
    // Set Minimum Date for Date Pickers
    // =============================================
    const todayStr = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"][data-min-today]').forEach(function (el) {
        el.min = todayStr;
    });

    // =============================================
    // Display Formatted Today Date in Welcome Banner
    // =============================================
    const dateSpan = document.getElementById('currentDate');
    if (dateSpan) {
        const now = new Date();
        const options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
        dateSpan.textContent = now.toLocaleDateString(undefined, options);
    }
});
