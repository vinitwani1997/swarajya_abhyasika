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
