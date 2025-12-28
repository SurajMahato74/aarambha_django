const API_BASE_URL = '/api';

const api = {
    register: `${API_BASE_URL}/users/register/`,
    login: `${API_BASE_URL}/users/login/`,
    profile: `${API_BASE_URL}/users/profile/`
};

function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function clearToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
}

function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function showLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.classList.remove('hidden');
    }
}

function hideLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.classList.add('hidden');
    }
}

async function fetchAPI(url, options = {}) {
    let token = getToken();
    const headers = {
        ...options.headers
    };

    // Don't set Content-Type for FormData - let browser set it automatically
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    let response = await fetch(url, {
        ...options,
        headers
    });

    // Handle token expiration - but don't redirect from profile page
    if (response.status === 401 && localStorage.getItem('refresh_token')) {
        try {
            const refreshResponse = await fetch('/api/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
            });

            if (refreshResponse.ok) {
                const data = await refreshResponse.json();
                setToken(data.access, localStorage.getItem('refresh_token'));
                headers['Authorization'] = `Bearer ${data.access}`;
                response = await fetch(url, { ...options, headers });
            } else {
                clearToken();
                // Don't redirect if we're on profile page
                if (!window.location.pathname.includes('/guest/profile/')) {
                    window.location.href = '/login/';
                }
            }
        } catch (e) {
            clearToken();
            // Don't redirect if we're on profile page
            if (!window.location.pathname.includes('/guest/profile/')) {
                window.location.href = '/login/';
            }
        }
    }

    return response;
}
