// document.addEventListener("DOMContentLoaded", function () {
//     // Load Header and Footer first
//     Promise.all([
//         fetch('components/header.html').then(r => r.text()),
//         fetch('components/footer.html').then(r => r.text())
//     ]).then(([headerData, footerData]) => {
//         document.getElementById('header').innerHTML = headerData;
//         document.getElementById('footer').innerHTML = footerData;

//         // Initialize features after header/footer are loaded
//         initMobileMenu();
//         initDarkMode();
//         initAuthSystem();
//     });
// });
document.addEventListener("DOMContentLoaded", function() {
    // Load header and footer with error handling
    const loadComponents = async () => {
        try {
            // Load header
            const headerResponse = await fetch('../components/header.html');
            if (!headerResponse.ok) throw new Error('Header not found');
            document.getElementById('header').innerHTML = await headerResponse.text();
            
            // Load footer
            const footerResponse = await fetch('../components/footer.html');
            if (!footerResponse.ok) throw new Error('Footer not found');
            document.getElementById('footer').innerHTML = await footerResponse.text();
            
            // Initialize other functions
            initMobileMenu();
            initDarkMode();
            initAuthSystem();
            
        } catch (error) {
            console.error('Component loading failed:', error);
            // Fallback content
            document.getElementById('header').innerHTML = '<h1>Swarajya Abhyasika</h1>';
            document.getElementById('footer').innerHTML = '<footer><p>© 2024 Swarajya Abhyasika</p></footer>';
        }
    };
    
    loadComponents();
});



function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
}

function initDarkMode() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) return;

    // Set initial theme
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.body.setAttribute('data-theme', 'dark');
        themeToggle.textContent = '☀️';
    } else {
        themeToggle.textContent = '🌙';
    }

    // Toggle handler
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    });
}

function initAuthSystem() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));

    if (currentUser) {
        // Hide guest links
        const guestLinks = document.getElementById('guest-links');
        if (guestLinks) guestLinks.classList.add('hidden');

        // Show role-specific links
        if (currentUser.role === 'admin') {
            const adminLinks = document.getElementById('admin-links');
            if (adminLinks) adminLinks.classList.remove('hidden');

            // Optionally, add admin badge to logo
            const logo = document.querySelector('.logo');
            if (logo) logo.innerHTML += '<span class="admin-badge">Admin</span>';
        } else {
            const userLinks = document.getElementById('user-links');
            if (userLinks) userLinks.classList.remove('hidden');

            // Optionally, add user badge to logo
            const logo = document.querySelector('.logo');
            if (logo) logo.innerHTML += '<span class="user-badge">User</span>';
        }
    }

    // Logout functionality
    const logoutButtons = document.querySelectorAll('#logout-btn, #admin-logout');
    logoutButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('currentUser');
            window.location.href = 'index.html';
        });
    });
}
