const sidebar = document.getElementById('sidebarMenu');
const toggleButton = document.querySelector('[data-bs-target="#sidebarMenu"]');

// Fecha ao clicar em qualquer link da sidebar
document.querySelectorAll('#sidebarMenu .nav-link').forEach(link => {
    link.addEventListener('click', () => {
        const collapse = bootstrap.Collapse.getInstance(sidebar);
        if (collapse) collapse.hide();
    });
});

// Fecha ao clicar fora da sidebar (em telas pequenas)
document.addEventListener('click', function (event) {
    const isSidebarOpen = sidebar.classList.contains('show');

    if (isSidebarOpen &&
        !sidebar.contains(event.target) &&
        !toggleButton.contains(event.target)) {

        const collapse = bootstrap.Collapse.getInstance(sidebar);
        if (collapse) collapse.hide();
    }
});
