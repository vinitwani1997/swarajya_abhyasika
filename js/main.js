// Load Header and Footer on every page
document.addEventListener("DOMContentLoaded", function() {
    // Load Header
    fetch('components/header.html')
        .then(response => response.text())
        .then(data => document.getElementById('header').innerHTML = data);

    // Load Footer
    fetch('components/footer.html')
        .then(response => response.text())
        .then(data => document.getElementById('footer').innerHTML = data);
});

// Mobile Menu Toggle
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('active');
});

// Dark Mode Toggle
const themeToggle = document.querySelector('.theme-toggle');
themeToggle.addEventListener('click', () => {
  document.body.setAttribute('data-theme', 
    document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'
  );
  // Save preference to localStorage
  localStorage.setItem('theme', document.body.getAttribute('data-theme'));
});

// Check for saved theme preference
if (localStorage.getItem('theme') === 'dark') {
  document.body.setAttribute('data-theme', 'dark');
}
