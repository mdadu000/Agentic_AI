import ApiService from "../services/apiService.js";

const AUTH_KEY = "easydine_user";

class AuthManager {
    static getUser() {
        try {
            const data = localStorage.getItem(AUTH_KEY);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            return null;
        }
    }

    static setUser(user) {
        localStorage.setItem(AUTH_KEY, JSON.stringify(user));
        AuthManager.updateUI();
    }

    static logout() {
        localStorage.removeItem(AUTH_KEY);
        AuthManager.updateUI();
        window.location.reload();
    }

    static isAdmin() {
        const user = AuthManager.getUser();
        return user && user.role === "admin";
    }

    static init() {
        AuthManager.updateUI();
        AuthManager.bindGateEvents();
    }

    static updateUI() {
        const user = AuthManager.getUser();
        const gateSection = document.getElementById("landing-gate-section");
        const workspaceWrapper = document.getElementById("dashboard-workspace-wrapper");
        const authBtnContainer = document.getElementById("auth-nav-container");
        const adminElements = document.querySelectorAll(".admin-only");

        if (adminElements) {
            adminElements.forEach(el => {
                el.style.display = AuthManager.isAdmin() ? "" : "none";
            });
        }

        // 1. Landing Gate View Switching
        if (gateSection && workspaceWrapper) {
            if (user) {
                gateSection.classList.add("hidden");
                workspaceWrapper.classList.remove("hidden");
            } else {
                gateSection.classList.remove("hidden");
                workspaceWrapper.classList.add("hidden");
            }
        }

        // 2. Auth Profile Badge in Sidebar & Top Bar
        const topBarAuthContainer = document.getElementById("top-bar-auth-container");

        const renderAuthHTML = (container) => {
            if (!container) return;
            if (user) {
                const roleBadge = user.role === "admin" 
                    ? `<span class="badge-role admin"><i class="fa-solid fa-user-shield"></i> Admin</span>` 
                    : `<span class="badge-role user"><i class="fa-solid fa-user"></i> User</span>`;

                container.innerHTML = `
                    <div class="user-profile-badge">
                        ${roleBadge}
                        <span class="user-name">${user.name || user.email}</span>
                        <button class="btn-logout" title="Log Out / Switch Account"><i class="fa-solid fa-right-from-bracket"></i></button>
                    </div>
                `;

                const btn = container.querySelector(".btn-logout");
                if (btn) btn.onclick = AuthManager.logout;
            } else {
                container.innerHTML = `
                    <button class="btn-primary btn-sm btn-open-login">
                        <i class="fa-solid fa-lock"></i> Sign In / Register
                    </button>
                `;
                const btn = container.querySelector(".btn-open-login");
                if (btn) btn.onclick = () => AuthManager.logout();
            }
        };

        renderAuthHTML(authBtnContainer);
        renderAuthHTML(topBarAuthContainer);
    }

    static bindGateEvents() {
        const gateTabLogin = document.getElementById("gate-tab-login");
        const gateTabSignup = document.getElementById("gate-tab-signup");
        const gateLoginForm = document.getElementById("gate-login-form");
        const gateSignupForm = document.getElementById("gate-signup-form");

        const demoUserBtn = document.getElementById("quick-demo-user-btn");
        const demoAdminBtn = document.getElementById("quick-demo-admin-btn");

        if (demoUserBtn) {
            demoUserBtn.onclick = async () => {
                try {
                    const res = await ApiService.post("/auth/login", { email: "user@easydine.com", password: "user123" });
                    AuthManager.setUser(res.user);
                } catch (e) {
                    AuthManager.setUser({ name: "Demo User", email: "user@easydine.com", role: "user" });
                }
            };
        }

        if (demoAdminBtn) {
            demoAdminBtn.onclick = async () => {
                try {
                    const res = await ApiService.post("/auth/login", { email: "admin@easydine.com", password: "admin123" });
                    AuthManager.setUser(res.user);
                } catch (e) {
                    AuthManager.setUser({ name: "System Administrator", email: "admin@easydine.com", role: "admin" });
                }
            };
        }

        if (gateTabLogin && gateTabSignup) {
            gateTabLogin.onclick = () => {
                gateTabLogin.classList.add("active");
                gateTabSignup.classList.remove("active");
                if (gateLoginForm) gateLoginForm.classList.remove("hidden");
                if (gateSignupForm) gateSignupForm.classList.add("hidden");
            };
            gateTabSignup.onclick = () => {
                gateTabSignup.classList.add("active");
                gateTabLogin.classList.remove("active");
                if (gateSignupForm) gateSignupForm.classList.remove("hidden");
                if (gateLoginForm) gateLoginForm.classList.add("hidden");
            };
        }

        if (gateLoginForm) {
            gateLoginForm.onsubmit = async (e) => {
                e.preventDefault();
                const email = document.getElementById("gate-login-email").value;
                const password = document.getElementById("gate-login-password").value;

                try {
                    const res = await ApiService.post("/auth/login", { email, password });
                    AuthManager.setUser(res.user);
                } catch (err) {
                    alert(`Login Error: ${err.message}`);
                }
            };
        }

        if (gateSignupForm) {
            gateSignupForm.onsubmit = async (e) => {
                e.preventDefault();
                const name = document.getElementById("gate-signup-name").value;
                const email = document.getElementById("gate-signup-email").value;
                const password = document.getElementById("gate-signup-password").value;
                const role = document.getElementById("gate-signup-role").value;

                try {
                    const res = await ApiService.post("/auth/signup", { name, email, password, role });
                    AuthManager.setUser(res.user);
                } catch (err) {
                    alert(`Signup Error: ${err.message}`);
                }
            };
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    AuthManager.init();
});

export default AuthManager;
