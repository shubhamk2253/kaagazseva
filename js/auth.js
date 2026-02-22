// js/auth.js

function getToken(){
    return localStorage.getItem("access_token");
}

function getRole(){
    return localStorage.getItem("role");
}

function requireRole(expectedRole){
    const token = getToken();
    const role = getRole();

    if(!token || role !== expectedRole){
        localStorage.clear();
        window.location.href = "/login.html";
    }
}

function logout(){
    localStorage.clear();
    window.location.href = "/login.html";
}

async function authFetch(url, options = {}) {

    const token = getToken();

    options.headers = {
        ...(options.headers || {}),
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    };

    const res = await fetch(API_BASE + url, options);

    if(res.status === 401){
        localStorage.clear();
        window.location.href = "/login.html";
        return;
    }

    return res.json();
}
