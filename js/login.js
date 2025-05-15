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
