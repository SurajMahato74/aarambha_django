/**
 * Debug utilities to help with troubleshooting
 */

// Store console logs in memory to prevent them from disappearing
window.debugLogs = [];

// Override console.log to store logs
const originalConsoleLog = console.log;
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

console.log = function(...args) {
    window.debugLogs.push({
        type: 'log',
        timestamp: new Date().toISOString(),
        message: args.join(' ')
    });
    originalConsoleLog.apply(console, args);
};

console.error = function(...args) {
    window.debugLogs.push({
        type: 'error',
        timestamp: new Date().toISOString(),
        message: args.join(' ')
    });
    originalConsoleError.apply(console, args);
};

console.warn = function(...args) {
    window.debugLogs.push({
        type: 'warn',
        timestamp: new Date().toISOString(),
        message: args.join(' ')
    });
    originalConsoleWarn.apply(console, args);
};

// Function to display stored logs
function showDebugLogs() {
    console.log('=== DEBUG LOGS ===');
    window.debugLogs.forEach(log => {
        console.log(`[${log.timestamp}] ${log.type.toUpperCase()}: ${log.message}`);
    });
    console.log('=== END DEBUG LOGS ===');
}

// Function to clear stored logs
function clearDebugLogs() {
    window.debugLogs = [];
    console.log('Debug logs cleared');
}

// Add debug info to window for easy access
window.debugInfo = function() {
    console.log('=== DEBUG INFO ===');
    console.log('Current URL:', window.location.href);
    console.log('User from localStorage:', getUser());
    console.log('Access token:', getToken());
    console.log('Django user:', window.djangoUser);
    console.log('=== END DEBUG INFO ===');
};

// Log authentication state changes
function logAuthState(action) {
    console.log(`AUTH: ${action}`, {
        user: getUser(),
        token: getToken() ? 'present' : 'missing',
        url: window.location.href
    });
}

// Add to window for easy access in console
window.showDebugLogs = showDebugLogs;
window.clearDebugLogs = clearDebugLogs;
window.logAuthState = logAuthState;

console.log('Debug utilities loaded. Use showDebugLogs(), clearDebugLogs(), or debugInfo() in console.');