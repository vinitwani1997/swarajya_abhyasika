document.getElementById('login-form').addEventListener('submit', function(e) {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  // In a real app, you would verify against your backend
  if (email === 'admin@swarajya.com' && password === 'admin123') {
    localStorage.setItem('currentUser', JSON.stringify({
      email: email,
      name: 'Admin User',
      role: 'admin'
    }));
    window.location.href = 'admin/dashboard.html';
  } 
  else if (email === 'user@swarajya.com' && password === 'user123') {
    localStorage.setItem('currentUser', JSON.stringify({
      email: email,
      name: 'Regular User',
      role: 'user'
    }));
    window.location.href = 'dashboard.html';
  }
  else {
    alert('Invalid credentials');
  }
});

// document.getElementById('login-form').addEventListener('submit', function(e) {
//   e.preventDefault();
  
//   const email = document.getElementById('email').value;
//   const password = document.getElementById('password').value;
  
//   // Get all users (including hardcoded admin)
//   const users = JSON.parse(localStorage.getItem('users')) || [];
  
//   // Check hardcoded admin first
//   if (email === "admin@swarajya.com" && password === "Swarajya@2024") {
//     localStorage.setItem('currentUser', JSON.stringify({
//       name: "System Admin",
//       email: email,
//       role: "admin"
//     }));
//     return window.location.href = "admin/dashboard.html";
//   }
  
//   // Check regular users
//   const user = users.find(u => u.email === email && u.password === password);
  
//   if (user) {
//     localStorage.setItem('currentUser', JSON.stringify(user));
//     window.location.href = user.role === 'admin' 
//       ? "admin/dashboard.html" 
//       : "dashboard.html";
//   } else {
//     alert("Invalid credentials");
//   }
// });
