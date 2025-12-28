/**
 * Authentication utilities for handling client-side auth state
 */

function clearToken() {
    // Clear all localStorage data
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    console.log('Client-side tokens cleared');
}

function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function updateNavbarAuth() {
    const user = getUser();
    const navAuthItem = document.getElementById('navAuthItem');
    
    if (!navAuthItem) return;
    
    // Always show logout if Django user is authenticated, regardless of localStorage
    if (window.djangoUser && window.djangoUser.isAuthenticated) {
        navAuthItem.innerHTML = `
            <a href="/guest/profile/" class="navigation__level-one-link me-3">
                Profile
            </a>
            <a href="javascript:void(0)" class="navigation__level-one-link" onclick="handleLogout()">
                Logout
            </a>
        `;
    } else if (user) {
        // User is logged in via localStorage - show profile link and logout button
        navAuthItem.innerHTML = `
            <a href="/guest/profile/" class="navigation__level-one-link me-3">
                Profile
            </a>
            <a href="javascript:void(0)" class="navigation__level-one-link" onclick="handleLogout()">
                Logout
            </a>
        `;
    } else {
        // User is not logged in - show login link
        navAuthItem.innerHTML = `
            <a href="javascript:void(0)" id="navLoginLink" class="navigation__level-one-link" onclick="handleNavLoginClick()">Login</a>
        `;
    }
}

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        // Clear all localStorage data
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Redirect directly to home page
        window.location.href = '/';
    }
}



// Initialize auth state on page load
document.addEventListener('DOMContentLoaded', function() {
    // Don't override navbar auth state - let Django template handle it
    console.log('Django user:', window.djangoUser);
});