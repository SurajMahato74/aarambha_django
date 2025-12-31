/**
 * Authentication utilities for handling client-side auth state
 * Updated to work consistently with all three login methods
 */

function setToken(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

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

function getToken() {
    return localStorage.getItem('access_token');
}

// Check authentication status with backend
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/users/auth-status/', {
            method: 'GET',
            credentials: 'include', // Include session cookies
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken() || ''}`
            }
        });
        
        const data = await response.json();
        
        if (data.authenticated) {
            // Sync localStorage with backend data
            setUser(data.user);
            if (data.access) {
                setToken(data.access, data.refresh);
            }
            return data.user;
        } else {
            // Clear localStorage if not authenticated
            clearToken();
            return null;
        }
    } catch (error) {
        console.error('Auth status check failed:', error);
        return getUser(); // Fallback to localStorage
    }
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

async function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        try {
            // Call backend logout endpoint
            const token = getToken();
            if (token) {
                await fetch('/api/users/logout/', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });
            }
        } catch (error) {
            console.error('Logout API call failed:', error);
        }
        
        // Clear all localStorage data
        clearToken();
        
        // Redirect directly to home page
        window.location.href = '/';
    }
}

// Initialize auth state on page load
document.addEventListener('DOMContentLoaded', async function() {
    // Check auth status with backend for consistency
    await checkAuthStatus();
    
    // Update navbar
    updateNavbarAuth();
    
    console.log('Auth state initialized');
});