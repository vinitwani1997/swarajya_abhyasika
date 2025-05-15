// Get current user from localStorage
function getCurrentUser() {
    return JSON.parse(localStorage.getItem('currentUser'));
}

// Check if the user is logged in
function isLoggedIn() {
    return !!getCurrentUser();
}

// Check if the current user is an admin
function isAdmin() {
    const user = getCurrentUser();
    return user && user.role === 'admin';
}

// Enhanced auth guard with optional role requirement and redirect
function authGuard(requiredRole = null) {
    const user = getCurrentUser();

    if (!user) {
        // Redirect to login with return URL
        const redirectUrl = encodeURIComponent(window.location.pathname);
        window.location.href = `/login.html?redirect=${redirectUrl}`;
        return false;
    }

    if (requiredRole && user.role !== requiredRole) {
        // Redirect to appropriate dashboard if user lacks role
        window.location.href = user.role === 'admin'
            ? '/admin/dashboard.html'
            : '/pages/dashboard.html';
        return false;
    }

    return true;
}

// Logout function
function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = '/login.html';
}
