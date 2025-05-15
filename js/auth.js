// Check if user is logged in
function checkAuth() {
    return JSON.parse(localStorage.getItem('currentUser'));
}

// Check if user is admin
function isAdmin() {
    const user = checkAuth();
    return user && user.role === 'admin';
}

// Redirect unauthorized users
function authGuard(requireAdmin = false) {
    const user = checkAuth();
    
    if (!user) {
        window.location.href = '/login.html';
    } else if (requireAdmin && !isAdmin()) {
        window.location.href = '/404.html';
    }
}
