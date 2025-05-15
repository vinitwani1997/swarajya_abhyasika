// // Load Header and Footer on every page
// document.addEventListener("DOMContentLoaded", function() {
//     // Load Header
//     fetch('components/header.html')
//         .then(response => response.text())
//         .then(data => document.getElementById('header').innerHTML = data);

//     // Load Footer
//     fetch('components/footer.html')
//         .then(response => response.text())
//         .then(data => document.getElementById('footer').innerHTML = data);
// });

// // Mobile Menu Toggle
// const hamburger = document.querySelector('.hamburger');
// const navLinks = document.querySelector('.nav-links');

// hamburger.addEventListener('click', () => {
//   navLinks.classList.toggle('active');
// });

// // Dark Mode Toggle
// const themeToggle = document.querySelector('.theme-toggle');
// themeToggle.addEventListener('click', () => {
//   document.body.setAttribute('data-theme', 
//     document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'
//   );
//   // Save preference to localStorage
//   localStorage.setItem('theme', document.body.getAttribute('data-theme'));
// });

// // Check for saved theme preference
// if (localStorage.getItem('theme') === 'dark') {
//   document.body.setAttribute('data-theme', 'dark');
// }
document.addEventListener("DOMContentLoaded", function() {
    // Load Header and Footer first
    Promise.all([
        fetch('components/header.html').then(r => r.text()),
        fetch('components/footer.html').then(r => r.text())
    ]).then(([headerData, footerData]) => {
        document.getElementById('header').innerHTML = headerData;
        document.getElementById('footer').innerHTML = footerData;
        
        // Now initialize interactive elements
        initMobileMenu();
        initDarkMode();
    });
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

// After your existing DOMContentLoaded code
function initAuthSystem() {
  // Check login status from localStorage/session
  const currentUser = JSON.parse(localStorage.getItem('currentUser'));
  
  if (currentUser) {
    // Hide guest links
    document.getElementById('guest-links').classList.add('hidden');
    
    if (currentUser.role === 'admin') {
      // Show admin links
      document.getElementById('admin-links').classList.remove('hidden');
      
      // Add admin badge to logo
      const logo = document.querySelector('.logo');
      logo.innerHTML += '<span class="admin-badge">Admin</span>';
    } else {
      // Show user links
      document.getElementById('user-links').classList.remove('hidden');
      
      // Add user badge to logo
      const logo = document.querySelector('.logo');
      logo.innerHTML += '<span class="user-badge">User</span>';
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

// Call this after header loads
initAuthSystem();
