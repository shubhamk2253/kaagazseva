<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KaagazSeva – India’s Premier Document Service Network</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --primary: #0a4fa3;
            --primary-dark: #083d7e;
            --accent: #ffcc00;
            --text-main: #1a202c;
            --text-light: #4a5568;
            --bg-light: #f7fafc;
            --white: #ffffff;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            --founder-neon: #00ffcc;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background: var(--bg-light); color: var(--text-main); line-height: 1.6; overflow-x: hidden; }

        /* --- Header & Navigation --- */
        header {
            background: var(--white);
            padding: 0 40px;
            height: 80px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        }

        .logo {
            font-size: 24px;
            font-weight: 800;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
        }

        .nav-right { display: flex; align-items: center; gap: 20px; }

        .nav-links { display: flex; gap: 25px; margin-right: 15px; }
        .nav-links a {
            color: var(--text-light);
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: 0.2s;
        }
        .nav-links a:hover { color: var(--primary); }

        /* --- Founder Secure Button --- */
        .founder-access-btn {
            background: #1a202c;
            color: var(--founder-neon);
            border: 1px solid var(--founder-neon);
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            display: none; /* Hidden unless triggered */
            align-items: center;
            gap: 8px;
            transition: 0.3s;
            box-shadow: 0 0 10px rgba(0, 255, 204, 0.2);
        }
        .founder-access-btn:hover {
            background: var(--founder-neon);
            color: #1a202c;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.4);
        }
        .pulse {
            width: 6px;
            height: 6px;
            background: var(--founder-neon);
            border-radius: 50%;
            animation: pulse-gfx 1.5s infinite;
        }
        @keyframes pulse-gfx {
            0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 255, 204, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(0, 255, 204, 0); }
            100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 255, 204, 0); }
        }

        .menu-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: 0.3s;
        }
        .menu-btn:hover { background: var(--primary-dark); transform: scale(1.02); }

        /* --- Side Drawer --- */
        .drawer-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(4px);
            visibility: hidden; opacity: 0;
            transition: 0.3s; z-index: 2000;
        }
        .drawer {
            position: fixed;
            top: 0; right: -350px; width: 350px; height: 100%;
            background: var(--white);
            z-index: 2001;
            transition: 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            padding: 40px;
            display: flex;
            flex-direction: column;
            box-shadow: -10px 0 30px rgba(0,0,0,0.1);
        }
        .drawer.active { right: 0; }
        .drawer-overlay.active { visibility: visible; opacity: 1; }

        .drawer-section { margin-bottom: 30px; }
        .drawer-section label {
            display: block; font-size: 11px; text-transform: uppercase;
            letter-spacing: 1.5px; color: #a0aec0; font-weight: 700; margin-bottom: 15px;
        }
        .drawer-link {
            display: block; padding: 12px 0; color: var(--text-main);
            text-decoration: none; font-weight: 600; border-bottom: 1px solid #edf2f7;
            transition: 0.2s;
        }
        .drawer-link:hover { color: var(--primary); padding-left: 8px; }

        /* --- Hero Section --- */
        .hero {
            background: linear-gradient(135deg, #0a4fa3 0%, #0f6ad6 100%);
            color: var(--white);
            padding: 140px 20px;
            text-align: center;
            clip-path: ellipse(150% 100% at 50% 0%);
        }
        .hero h1 { font-size: 56px; font-weight: 800; margin-bottom: 20px; letter-spacing: -1.5px; }
        .hero p { font-size: 20px; opacity: 0.9; max-width: 700px; margin: 0 auto 40px; }
        
        .cta-btn {
            background: var(--accent);
            color: var(--primary-dark);
            padding: 20px 45px;
            border: none;
            border-radius: 14px;
            font-size: 18px;
            font-weight: 800;
            cursor: pointer;
            transition: 0.3s;
            box-shadow: 0 8px 25px rgba(255, 204, 0, 0.3);
        }
        .cta-btn:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(255, 204, 0, 0.4); }

        /* --- Features/Services --- */
        .section { padding: 100px 40px; max-width: 1200px; margin: 0 auto; text-align: center; }
        .section h2 { font-size: 36px; font-weight: 800; margin-bottom: 60px; color: var(--primary-dark); }
        
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 35px;
        }
        .card {
            background: var(--white);
            padding: 45px 35px;
            border-radius: 24px;
            text-align: left;
            transition: 0.4s;
            border: 1px solid #f1f5f9;
        }
        .card:hover { transform: translateY(-12px); box-shadow: var(--shadow); }
        .card .icon-box { 
            width: 50px; height: 50px; background: #eef4ff; border-radius: 12px; 
            display: flex; align-items: center; justify-content: center; color: var(--primary);
            margin-bottom: 25px;
        }
        .card h3 { color: var(--primary-dark); margin-bottom: 15px; font-size: 22px; font-weight: 700; }
        .card p { color: var(--text-light); font-size: 15px; line-height: 1.7; }

        footer {
            background: #111827;
            color: #94a3b8;
            padding: 60px 40px;
            text-align: center;
            font-size: 14px;
        }

        @media (max-width: 768px) {
            .nav-links { display: none; }
            .hero h1 { font-size: 38px; }
            header { padding: 0 20px; }
            .drawer { width: 100%; right: -100%; }
        }
    </style>
</head>

<body>

<header>
    <a href="index.html" class="logo">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="var(--primary)">
            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
        </svg>
        KaagazSeva
    </a>

    <div class="nav-right">
        <button id="founderBtn" class="founder-access-btn" onclick="location.href='founder-login.html'">
            <div class="pulse"></div>
            System Core
        </button>

        <nav class="nav-links">
            <a href="index.html">Home</a>
            <a href="apply-service.html">Services</a>
            <a href="track.html">Track Status</a>
        </nav>

        <button class="menu-btn" onclick="toggleDrawer()">
            <span>Explore</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        </button>
    </div>
</header>

<div class="drawer-overlay" id="overlay" onclick="toggleDrawer()"></div>
<div class="drawer" id="drawer">
    <div class="drawer-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:40px;">
        <h2 style="color: var(--primary); font-weight:800;">Navigation</h2>
        <button onclick="toggleDrawer()" style="background:none; border:none; font-size:32px; cursor:pointer; color:#94a3b8">&times;</button>
    </div>

    <div class="drawer-section">
        <label>Portal Access</label>
        <div id="auth-links">
            <a href="customer-login.html" class="drawer-link">Customer Login</a>
            <a href="agent-login.html" class="drawer-link">Agent Login</a>
            <a href="admin-login.html" class="drawer-link">Staff Portal</a>
        </div>
    </div>

    <div class="drawer-section">
        <label>Join the Network</label>
        <a href="customer-register.html" class="drawer-link">Create Account</a>
        <a href="agent-register.html" class="drawer-link">Apply as Agent</a>
    </div>

    <div class="drawer-section" style="margin-top:auto;">
        <label>Help & Legal</label>
        <a href="#" class="drawer-link">Support Desk</a>
        <a href="#" class="drawer-link">Privacy Policy</a>
    </div>
</div>

<section class="hero">
    <h1>India’s Digital Document Gateway</h1>
    <p>We bridge the gap between citizens and government services through a verified network of expert agents.</p>
    <button class="cta-btn" onclick="location.href='apply-service.html'">Start Application Now</button>
</section>



<section class="section">
    <h2>Premier Solutions</h2>
    <div class="cards">
        <div class="card">
            <div class="icon-box">💳</div>
            <h3>PAN Identity</h3>
            <p>New registration, duplicate issuance, and data correction with automated tracking.</p>
        </div>
        <div class="card">
            <div class="icon-box">📜</div>
            <h3>State Revenue</h3>
            <p>Digital processing for Income, Caste, and Domicile certificates across all states.</p>
        </div>
        <div class="card">
            <div class="icon-box">🛂</div>
            <h3>Passport Seva</h3>
            <p>Full appointment management and documentation for fresh and renewal passports.</p>
        </div>
        <div class="card">
            <div class="icon-box">⚖️</div>
            <h3>Legal & Tax</h3>
            <p>GST, ITR Filing, and Udyam registrations for small businesses and individuals.</p>
        </div>
    </div>
</section>

<footer>
    <div style="margin-bottom: 20px;">
        <strong style="color:white; font-size:18px;">KaagazSeva India</strong>
    </div>
    <p>© 2026 KaagazSeva. All rights reserved. 
    <br>Empowering the nation through transparent documentation.</p>
</footer>

<script src="config.js"></script>
<script>
    function toggleDrawer() {
        document.getElementById('drawer').classList.toggle('active');
        document.getElementById('overlay').classList.toggle('active');
    }

    window.onload = () => {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");
        const urlParams = new URLSearchParams(window.location.search);
        const founderBtn = document.getElementById('founderBtn');

        // Logic for "System Core" Button Visibility
        if(role === 'founder' || urlParams.has('root')) {
            founderBtn.style.display = 'flex';
        }

        // Update Drawer Content if Logged In
        if(token) {
            document.getElementById('auth-links').innerHTML = `
                <div style="padding:15px; background:#f1f5f9; border-radius:12px; margin-bottom:15px;">
                    <p style="font-size:10px; font-weight:800; color:var(--primary);">AUTHORIZED SESSION</p>
                    <p style="font-weight:700; color:var(--text-main);">${role ? role.toUpperCase() : 'USER'}</p>
                </div>
                <a href="dashboard.html" class="drawer-link">Access Dashboard</a>
                <a href="#" class="drawer-link" onclick="logout()" style="color: #ef4444">Secure Logout</a>
            `;
        }
    }

    function logout() {
        if(confirm("Confirm secure logout?")) {
            localStorage.clear();
            window.location.href = "index.html";
        }
    }
</script>

</body>
</html>
