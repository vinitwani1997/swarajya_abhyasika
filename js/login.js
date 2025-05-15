// document.getElementById('login-form').addEventListener('submit', function(e) {
//   e.preventDefault();
  
//   const email = document.getElementById('email').value;
//   const password = document.getElementById('password').value;
  
//   // In a real app, you would verify against your backend
//   if (email === 'admin@swarajya.com' && password === 'admin123') {
//     localStorage.setItem('currentUser', JSON.stringify({
//       email: email,
//       name: 'Admin User',
//       role: 'admin'
//     }));
//     window.location.href = 'admin/dashboard.html';
//   } 
//   else if (email === 'user@swarajya.com' && password === 'user123') {
//     localStorage.setItem('currentUser', JSON.stringify({
//       email: email,
//       name: 'Regular User',
//       role: 'user'
//     }));
//     window.location.href = 'dashboard.html';
//   }
//   else {
//     alert('Invalid credentials');
//   }
// });

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    
    // Hardcoded admin credentials (in production, use server-side auth)
    const ADMIN_CREDENTIALS = {
        email: "admin@swarajya.com",
        password: "SwarajyaAdmin@2024", // CHANGE THIS IN PRODUCTION
        name: "System Administrator",
        role: "admin"
    };

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        // 1. Check against hardcoded admin first
        if (email === ADMIN_CREDENTIALS.email && password === ADMIN_CREDENTIALS.password) {
            localStorage.setItem('currentUser', JSON.stringify(ADMIN_CREDENTIALS));
            return window.location.href = "admin/dashboard.html";
        }

        // 2. Check registered users
        const users = JSON.parse(localStorage.getItem('users')) || [];
        const user = users.find(u => u.email === email && u.password === password);

        if (user) {
            localStorage.setItem('currentUser', JSON.stringify(user));
            window.location.href = user.role === 'admin' 
                ? "admin/dashboard.html" 
                : "pages/dashboard.html";
        } else {
            alert("Invalid email or password");
        }
    });
});
