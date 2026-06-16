/**
 * auth.js — Shared JWT authentication utilities
 * Include this AFTER config.js on every authenticated page.
 *
 * Provides:
 *   getValidToken()  — returns a valid access token, auto-refreshing if expired
 *   authFetch(url, options) — drop-in fetch() wrapper with auto token refresh
 *   logout()         — clears auth data and redirects to login
 */

/**
 * Decode a JWT token payload without a library.
 * Returns null if the token is invalid.
 */
function _decodeJWT(token) {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;
        const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
        return payload;
    } catch (e) {
        return null;
    }
}

/**
 * Check if a JWT token is expired (or will expire within 60 seconds).
 */
function _isTokenExpired(token) {
    const payload = _decodeJWT(token);
    if (!payload || !payload.exp) return true;
    // Consider expired if less than 60 seconds remaining
    return (payload.exp * 1000) < (Date.now() + 60000);
}

/**
 * Attempt to refresh the access token using the stored refresh token.
 * Returns the new access token, or null if refresh failed.
 */
async function _refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return null;

    try {
        const res = await fetch(`${API_BASE}/api/auth/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (!res.ok) {
            console.warn('[auth] Token refresh failed with status', res.status);
            return null;
        }

        const data = await res.json();
        if (data.access) {
            localStorage.setItem('access_token', data.access);
            console.log('[auth] Access token refreshed successfully');
            return data.access;
        }
        return null;
    } catch (e) {
        console.error('[auth] Token refresh error:', e);
        return null;
    }
}

/**
 * Get a valid access token. If the current token is expired,
 * it will be automatically refreshed. If refresh fails, returns null.
 */
async function getValidToken() {
    let token = localStorage.getItem('access_token');
    if (!token) return null;

    if (_isTokenExpired(token)) {
        console.log('[auth] Access token expired, attempting refresh...');
        token = await _refreshAccessToken();
        if (!token) {
            console.warn('[auth] Could not refresh token');
            return null;
        }
    }
    return token;
}

/**
 * Drop-in replacement for fetch() that automatically:
 * 1. Adds the Authorization header with a valid token
 * 2. Refreshes the token if expired before making the request
 * 3. Retries once on 401 (in case the token expired mid-flight)
 *
 * Usage: const res = await authFetch('/api/profile/');
 */
async function authFetch(url, options = {}) {
    let token = await getValidToken();

    if (!token) {
        logout();
        throw new Error('Authentication required');
    }

    // Merge auth header
    if (!options.headers) options.headers = {};

    // Don't override Content-Type for FormData (let browser set boundary)
    if (options.body instanceof FormData) {
        delete options.headers['Content-Type'];
    }

    options.headers['Authorization'] = `Bearer ${token}`;

    let res = await fetch(url, options);

    // If 401, try refreshing token once and retry
    if (res.status === 401) {
        console.log('[auth] Got 401, attempting token refresh and retry...');
        token = await _refreshAccessToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
            res = await fetch(url, options);
        } else {
            logout();
            throw new Error('Session expired');
        }
    }

    return res;
}

/**
 * Logout — clear all auth data and redirect to login page.
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}
