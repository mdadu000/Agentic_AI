import ApiService from "../services/apiService.js";
import AuthManager from "./auth.js";

let allRestaurantsData = [];
let allReservationsData = [];
let activeCuisineFilter = "all";
let searchQuery = "";

const UNIQUE_VENUE_IMAGES = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80", // 0: Luxury Hotel Exterior
    "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=600&q=80", // 1: Resort Hotel & Pool
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80", // 2: Grand Hotel Dining Hall
    "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=600&q=80", // 3: Italian Restaurant Interior
    "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=600&q=80", // 4: Boutique Lounge Restaurant
    "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=600&q=80", // 5: Asian Fine Dining Venue
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=600&q=80", // 6: 5-Star Hotel Suite & Dining
    "https://images.unsplash.com/photo-1578474846511-04ba529f0b88?auto=format&fit=crop&w=600&q=80", // 7: Modern Bistro Bar
    "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=600&q=80", // 8: Cozy Restaurant Terrace
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=600&q=80", // 9: Gourmet Table Venue
    "https://images.unsplash.com/photo-1528605248644-14dd04022da1?auto=format&fit=crop&w=600&q=80", // 10: Garden Hotel Pavilion
    "https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=600&q=80"  // 11: Rooftop Hotel Dining
];

document.addEventListener("DOMContentLoaded", () => {
    loadRestaurants();
    loadReservations();
    bindFilterEvents();
    bindBookingFilterEvents();
    bindSidebarNav();
    bindMenuModalEvents();
    bindBookingModalEvents();
    
    const addBtn = document.getElementById("add-restaurant-btn");
    const modal = document.getElementById("restaurant-modal");
    const cancelBtn = document.getElementById("cancel-modal-btn");
    const form = document.getElementById("restaurant-form");

    const closeIcon = document.getElementById("close-modal-icon");
    const overlay = document.querySelector("#restaurant-modal .modal-overlay");

    if (addBtn) addBtn.addEventListener("click", () => {
        if (!AuthManager.isAdmin()) {
            alert("Admin privileges required to add a restaurant. Please login as admin@easydine.com");
            return;
        }
        modal.classList.remove("hidden");
    });
    
    if (cancelBtn) cancelBtn.addEventListener("click", () => modal.classList.add("hidden"));
    if (closeIcon) closeIcon.addEventListener("click", () => modal.classList.add("hidden"));
    if (overlay) overlay.addEventListener("click", () => modal.classList.add("hidden"));
    if (form) form.addEventListener("submit", handleAddRestaurant);
});

function getRestaurantImageUrl(restaurant) {
    if (!restaurant) return UNIQUE_VENUE_IMAGES[0];

    const n = (restaurant.name || "").toLowerCase();
    if (n.includes("mayura")) return UNIQUE_VENUE_IMAGES[0];
    if (n.includes("vishnu")) return UNIQUE_VENUE_IMAGES[1];
    if (n.includes("preethi")) return UNIQUE_VENUE_IMAGES[2];
    if (n.includes("empire")) return UNIQUE_VENUE_IMAGES[4];
    if (n.includes("ashirvad")) return UNIQUE_VENUE_IMAGES[7];
    if (n.includes("starbiryani")) return UNIQUE_VENUE_IMAGES[8];

    // Fallback deterministic string hash indexing
    const str = (restaurant.id || restaurant.name || "").toString();
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = (hash << 5) - hash + str.charCodeAt(i);
        hash |= 0;
    }
    const idx = Math.abs(hash) % UNIQUE_VENUE_IMAGES.length;
    return UNIQUE_VENUE_IMAGES[idx];
}

function getDishImageUrl(dishName, category) {
    const d = (dishName || "").toLowerCase();
    const c = (category || "").toLowerCase();

    if (d.includes("idli")) {
        return "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("dosa")) {
        return "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("manchurian") || d.includes("chinese") || d.includes("noodles")) {
        return "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("biryani") || d.includes("rice")) {
        return "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("pizza")) {
        return "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("pasta") || d.includes("fettuccine")) {
        return "https://images.unsplash.com/photo-1621996346565-e3d5d6281358?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("chicken") || d.includes("tikka") || d.includes("butter")) {
        return "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("tacos") || d.includes("burrito") || d.includes("nachos")) {
        return "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("burger")) {
        return "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("tiramisu") || d.includes("cake") || d.includes("jamun") || d.includes("churros") || c.includes("dessert")) {
        return "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=300&q=80";
    } else if (d.includes("naan") || d.includes("bread")) {
        return "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=300&q=80";
    } else {
        return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=300&q=80";
    }
}

function bindMenuModalEvents() {
    const modal = document.getElementById("menu-modal");
    const closeIcon = document.getElementById("close-menu-modal");
    const closeBtn = document.getElementById("close-menu-btn");
    const overlay = document.querySelector("#menu-modal .modal-overlay");

    const closeModal = () => {
        if (modal) modal.classList.add("hidden");
    };

    if (closeIcon) closeIcon.onclick = closeModal;
    if (closeBtn) closeBtn.onclick = closeModal;
    if (overlay) overlay.onclick = closeModal;
}

function bindBookingModalEvents() {
    const modal = document.getElementById("booking-modal");
    const openBtn = document.getElementById("open-booking-modal-btn");
    const closeIcon = document.getElementById("close-booking-modal");
    const cancelBtn = document.getElementById("cancel-booking-btn");
    const overlay = document.querySelector("#booking-modal .modal-overlay");
    const form = document.getElementById("booking-form");

    if (openBtn) {
        openBtn.onclick = () => {
            populateBookingRestoSelect();
            if (modal) modal.classList.remove("hidden");
        };
    }

    const closeModal = () => {
        if (modal) modal.classList.add("hidden");
    };

    if (closeIcon) closeIcon.onclick = closeModal;
    if (cancelBtn) cancelBtn.onclick = closeModal;
    if (overlay) overlay.onclick = closeModal;

    if (form) form.onsubmit = handleCreateReservation;
}

function populateBookingRestoSelect() {
    const select = document.getElementById("booking-resto-select");
    if (!select) return;

    select.innerHTML = "";
    if (allRestaurantsData.length === 0) {
        select.innerHTML = "<option value=''>No restaurants available</option>";
        return;
    }

    allRestaurantsData.forEach(resto => {
        const opt = document.createElement("option");
        opt.value = resto.id;
        opt.innerText = `${resto.name} (${resto.cuisine_type}) - ${resto.location}`;
        select.appendChild(opt);
    });
}

async function handleCreateReservation(e) {
    e.preventDefault();
    const restoId = document.getElementById("booking-resto-select").value;
    const timeVal = document.getElementById("booking-time").value;
    const guests = parseInt(document.getElementById("booking-guests").value) || 2;
    const userId = document.getElementById("booking-user-id").value || "Guest User";

    if (!restoId || !timeVal) {
        alert("Please select a restaurant and reservation date/time.");
        return;
    }

    const payload = {
        restaurant_id: restoId,
        user_id: userId,
        reservation_time: new Date(timeVal).isoformat ? new Date(timeVal).isoformat() : new Date(timeVal).toISOString(),
        guests: guests
    };

    try {
        await ApiService.post("/restaurants/reservations", payload);
        alert("Table Reservation Confirmed!");
        document.getElementById("booking-form").reset();
        document.getElementById("booking-modal").classList.add("hidden");
        loadReservations();
    } catch (err) {
        console.error("Booking failed:", err);
        alert(`Booking Error: ${err.message}`);
    }
}

function bindSidebarNav() {
    const sidebarBtns = document.querySelectorAll(".sidebar-nav-btn[data-tab]");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const viewTitle = document.getElementById("current-view-title");
    const viewSub = document.getElementById("current-view-sub");

    const titlesMap = {
        "tab-overview": { title: "Overview Dashboard", sub: "Real-time restaurant metrics & reservations" },
        "tab-restaurants": { title: "Restaurants Directory", sub: "Explore culinary venues and check menus" },
        "tab-bookings": { title: "Reservations & Bookings", sub: "View confirmed diner reservations" },
        "tab-analytics": { title: "Analytics & Insights", sub: "Data intelligence and performance highlights" }
    };

    sidebarBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            sidebarBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            tabPanes.forEach(pane => {
                if (pane.id === targetTab) {
                    pane.classList.remove("hidden");
                    pane.classList.add("active");
                } else {
                    pane.classList.add("hidden");
                    pane.classList.remove("active");
                }
            });

            if (titlesMap[targetTab] && viewTitle && viewSub) {
                viewTitle.innerText = titlesMap[targetTab].title;
                viewSub.innerText = titlesMap[targetTab].sub;
            }
        });
    });
}

function bindFilterEvents() {
    const searchInput = document.getElementById("restaurant-search-input");
    const filterPills = document.querySelectorAll(".filter-pill");

    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            searchQuery = e.target.value.toLowerCase().trim();
            renderFilteredRestaurants();
        });
    }

    if (filterPills) {
        filterPills.forEach(pill => {
            pill.addEventListener("click", () => {
                filterPills.forEach(p => p.classList.remove("active"));
                pill.classList.add("active");
                activeCuisineFilter = pill.getAttribute("data-cuisine");
                renderFilteredRestaurants();
            });
        });
    }
}

async function loadRestaurants() {
    const grid = document.getElementById("restaurants");
    const overviewGrid = document.getElementById("overview-restaurants");
    
    if (grid) grid.innerHTML = "<p class='placeholder-text'>Loading restaurants...</p>";
    if (overviewGrid) overviewGrid.innerHTML = "<p class='placeholder-text'>Loading restaurants...</p>";

    try {
        const data = await ApiService.get("/restaurants/");
        allRestaurantsData = data || [];

        // Update Stat Counter
        const statResto = document.getElementById("stat-resto-count");
        if (statResto) statResto.innerText = allRestaurantsData.length;

        renderFilteredRestaurants();
        renderOverviewRestaurants();
        loadAnalytics();
    } catch (error) {
        console.error("Failed to load restaurants:", error);
        if (grid) grid.innerHTML = `<p class='error-text'>Error loading restaurants: ${error.message}</p>`;
        if (overviewGrid) overviewGrid.innerHTML = `<p class='error-text'>Error loading restaurants: ${error.message}</p>`;
    }
}

function renderOverviewRestaurants() {
    const overviewGrid = document.getElementById("overview-restaurants");
    if (!overviewGrid) return;

    overviewGrid.innerHTML = "";
    const previewList = allRestaurantsData.slice(0, 3);

    if (previewList.length === 0) {
        overviewGrid.innerHTML = "<p class='placeholder-text'>No restaurants available.</p>";
        return;
    }

    previewList.forEach(restaurant => {
        const card = createRestaurantCard(restaurant);
        overviewGrid.appendChild(card);
    });
}

function renderFilteredRestaurants() {
    const grid = document.getElementById("restaurants");
    if (!grid) return;

    grid.innerHTML = "";

    let filtered = allRestaurantsData.filter(resto => {
        const matchesCuisine = activeCuisineFilter === "all" || 
            resto.cuisine_type.toLowerCase().includes(activeCuisineFilter.toLowerCase());
        
        const matchesSearch = !searchQuery || 
            resto.name.toLowerCase().includes(searchQuery) ||
            resto.location.toLowerCase().includes(searchQuery) ||
            resto.cuisine_type.toLowerCase().includes(searchQuery);

        return matchesCuisine && matchesSearch;
    });

    if (filtered.length === 0) {
        grid.innerHTML = "<p class='placeholder-text'>No restaurants match your search or filter criteria.</p>";
        return;
    }

    filtered.forEach(restaurant => {
        const card = createRestaurantCard(restaurant);
        grid.appendChild(card);
    });
}

function createRestaurantCard(restaurant) {
    const card = document.createElement("div");
    card.className = "restaurant-card";
    
    const ratingHTML = restaurant.rating
        ? `<div class="restaurant-rating">
             <i class="fa-solid fa-star"></i> ${restaurant.rating.toFixed(1)}
           </div>`
        : '';

    const isAdmin = AuthManager.isAdmin();
    const adminActionsHTML = isAdmin 
        ? `<button class="btn-delete-resto" data-id="${restaurant.id}" title="Delete Restaurant"><i class="fa-solid fa-trash"></i></button>`
        : '';

    const imageUrl = getRestaurantImageUrl(restaurant);

    card.innerHTML = `
        <div class="restaurant-card-banner">
            <img src="${imageUrl}" alt="${restaurant.name}" class="restaurant-img" loading="lazy" />
            <span class="cuisine-tag-badge">${restaurant.cuisine_type}</span>
        </div>
        <div class="restaurant-card-body">
            <div class="restaurant-header">
                <h3 class="restaurant-name">${restaurant.name}</h3>
                ${ratingHTML}
            </div>
            <div class="restaurant-details">
                <p class="restaurant-info">
                    <i class="fa-solid fa-map-pin"></i>
                    <span>${restaurant.location}</span>
                </p>
            </div>
            <div class="restaurant-card-footer" style="margin-top: 1rem; display: flex; gap: 0.5rem; align-items: center;">
                <button class="btn-primary btn-sm btn-view-menu" style="flex: 1; justify-content: center;"><i class="fa-solid fa-book-open"></i> View Menu & Prices</button>
                ${adminActionsHTML}
            </div>
        </div>
    `;

    const viewMenuBtn = card.querySelector(".btn-view-menu");
    if (viewMenuBtn) {
        viewMenuBtn.onclick = (e) => {
            e.stopPropagation();
            openRestaurantMenuModal(restaurant);
        };
    }

    if (isAdmin) {
        const delBtn = card.querySelector(".btn-delete-resto");
        if (delBtn) {
            delBtn.onclick = async (e) => {
                e.stopPropagation();
                if (confirm(`Admin Action: Delete restaurant '${restaurant.name}'?`)) {
                    try {
                        await ApiService.delete(`/restaurants/${restaurant.id}`);
                        loadRestaurants();
                    } catch (err) {
                        alert(`Failed to delete: ${err.message}`);
                    }
                }
            };
        }
    }

    return card;
}

async function openRestaurantMenuModal(restaurant) {
    const modal = document.getElementById("menu-modal");
    const titleEl = document.getElementById("menu-modal-title");
    const subEl = document.getElementById("menu-modal-subtitle");
    const listEl = document.getElementById("menu-items-list");

    if (!modal || !listEl) return;

    if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-utensils text-violet"></i> ${restaurant.name} Menu`;
    if (subEl) subEl.innerText = `${restaurant.cuisine_type} • ${restaurant.location}`;

    listEl.innerHTML = "<p class='placeholder-text'>Fetching delicious dishes...</p>";
    modal.classList.remove("hidden");

    try {
        const menuItems = await ApiService.get(`/restaurants/${restaurant.id}/menu`);
        listEl.innerHTML = "";

        if (!menuItems || menuItems.length === 0) {
            listEl.innerHTML = "<p class='placeholder-text'>No dishes added yet for this restaurant.</p>";
            return;
        }

        menuItems.forEach(item => {
            const dishCard = document.createElement("div");
            dishCard.className = "dish-card";
            const dishImg = getDishImageUrl(item.name, item.category);
            dishCard.innerHTML = `
                <img src="${dishImg}" alt="${item.name}" class="dish-img-thumb" loading="lazy" />
                <div class="dish-card-content">
                    <div class="dish-card-header">
                        <div class="dish-title-group">
                            <h4>${item.name}</h4>
                            ${item.category ? `<span class="badge-category">${item.category}</span>` : ''}
                        </div>
                        <span class="dish-price">$${item.price.toFixed(2)}</span>
                    </div>
                    <p class="dish-desc">${item.description || 'Freshly prepared signature dish.'}</p>
                </div>
            `;
            listEl.appendChild(dishCard);
        });
    } catch (err) {
        console.error("Failed to load menu:", err);
        listEl.innerHTML = `<p class='error-text'>Failed to load menu: ${err.message}</p>`;
    }
}

async function loadReservations() {
    const container = document.getElementById("reservations-list-container");
    const overviewContainer = document.getElementById("overview-reservations");

    if (container) container.innerHTML = "<p class='placeholder-text'>Loading reservations...</p>";
    if (overviewContainer) overviewContainer.innerHTML = "<p class='placeholder-text'>Loading reservations...</p>";

    try {
        const data = await ApiService.get("/restaurants/reservations/all");
        allReservationsData = data || [];

        const statBookings = document.getElementById("stat-bookings-count");
        if (statBookings) statBookings.innerText = allReservationsData.length;

        renderReservations();
    } catch (error) {
        console.error("Failed to load reservations:", error);
        if (container) container.innerHTML = `<p class='error-text'>Failed to load reservations: ${error.message}</p>`;
        if (overviewContainer) overviewContainer.innerHTML = `<p class='error-text'>Failed to load reservations: ${error.message}</p>`;
    }
}

let activeBookingFilter = "all";
let bookingSearchQuery = "";

function bindBookingFilterEvents() {
    const searchInput = document.getElementById("booking-search-input");
    const filterPills = document.querySelectorAll(".booking-filter-pill");

    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            bookingSearchQuery = e.target.value.toLowerCase().trim();
            renderReservations();
        });
    }

    if (filterPills) {
        filterPills.forEach(pill => {
            pill.addEventListener("click", () => {
                filterPills.forEach(p => p.classList.remove("active"));
                pill.classList.add("active");
                activeBookingFilter = pill.getAttribute("data-filter");
                renderReservations();
            });
        });
    }
}

function renderReservations() {
    const container = document.getElementById("reservations-list-container");
    const overviewContainer = document.getElementById("overview-reservations");

    if (container) {
        container.innerHTML = "";

        let filtered = allReservationsData.filter(res => {
            const matchesSearch = !bookingSearchQuery || 
                (res.restaurant_name && res.restaurant_name.toLowerCase().includes(bookingSearchQuery)) ||
                (res.user_id && res.user_id.toLowerCase().includes(bookingSearchQuery));

            let matchesFilter = true;
            if (activeBookingFilter === "large") {
                matchesFilter = (res.guests || 0) >= 4;
            } else if (activeBookingFilter === "today") {
                const todayStr = new Date().toISOString().split('T')[0];
                matchesFilter = res.reservation_time && res.reservation_time.includes(todayStr);
            }

            return matchesSearch && matchesFilter;
        });

        if (filtered.length === 0) {
            container.innerHTML = "<p class='placeholder-text'>No table reservations match your criteria. Click 'Book a New Table' to create one!</p>";
        } else {
            filtered.forEach(res => {
                const card = createReservationCard(res);
                container.appendChild(card);
            });
        }
    }

    if (overviewContainer) {
        overviewContainer.innerHTML = "";
        const previewList = allReservationsData.slice(0, 3);
        if (previewList.length === 0) {
            overviewContainer.innerHTML = "<p class='placeholder-text'>No table reservations found yet.</p>";
        } else {
            previewList.forEach(res => {
                const card = createReservationCard(res);
                overviewContainer.appendChild(card);
            });
        }
    }
}

function createReservationCard(res) {
    const card = document.createElement("div");
    card.className = "reservation-ticket-card";

    let dateStr = res.reservation_time;
    try {
        const d = new Date(res.reservation_time);
        dateStr = d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch(e) {}

    const matchingResto = allRestaurantsData.find(r => r.id === res.restaurant_id || r.name === res.restaurant_name);
    const cuisine = matchingResto ? matchingResto.cuisine_type : "Fine Dining";
    const resIdCode = res.id ? res.id.slice(0, 6).toUpperCase() : "RES-8921";

    card.innerHTML = `
        <div class="ticket-header">
            <div class="ticket-id-group">
                <span class="ticket-badge"><i class="fa-solid fa-ticket"></i> #${resIdCode}</span>
            </div>
            <span class="status-glow-badge confirmed"><i class="fa-solid fa-circle-check"></i> CONFIRMED</span>
        </div>
        
        <div class="ticket-body">
            <div class="ticket-venue-row">
                <h3 class="ticket-venue-name">${res.restaurant_name}</h3>
                <span class="badge-category">${cuisine}</span>
            </div>

            <div class="ticket-metrics-grid">
                <div class="metric-box">
                    <i class="fa-solid fa-clock text-emerald"></i>
                    <div class="metric-info">
                        <span class="metric-label">Date & Time</span>
                        <span class="metric-val">${dateStr}</span>
                    </div>
                </div>
                
                <div class="metric-box">
                    <i class="fa-solid fa-users text-violet"></i>
                    <div class="metric-info">
                        <span class="metric-label">Party Size</span>
                        <span class="metric-val">${res.guests} Guests</span>
                    </div>
                </div>

                <div class="metric-box">
                    <i class="fa-solid fa-user-tag text-amber"></i>
                    <div class="metric-info">
                        <span class="metric-label">Diner / Guest ID</span>
                        <span class="metric-val">${res.user_id || 'Guest Diner'}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="ticket-actions">
            <button class="btn-secondary btn-sm btn-view-menu"><i class="fa-solid fa-book-open"></i> View Menu & Prices</button>
            <button class="btn-danger-sm btn-cancel-booking" title="Cancel Reservation"><i class="fa-solid fa-calendar-xmark"></i> Cancel</button>
        </div>
    `;

    const viewMenuBtn = card.querySelector(".btn-view-menu");
    if (viewMenuBtn) {
        viewMenuBtn.onclick = (e) => {
            e.stopPropagation();
            if (matchingResto) {
                openRestaurantMenuModal(matchingResto);
            } else {
                openRestaurantMenuModal({ id: res.restaurant_id, name: res.restaurant_name, cuisine_type: cuisine, location: "Venue" });
            }
        };
    }

    const cancelBtn = card.querySelector(".btn-cancel-booking");
    if (cancelBtn) {
        cancelBtn.onclick = async (e) => {
            e.stopPropagation();
            if (confirm(`Cancel reservation for ${res.restaurant_name} (${dateStr})?`)) {
                try {
                    await ApiService.delete(`/restaurants/reservations/${res.id}`);
                    alert("Reservation cancelled successfully!");
                    loadReservations();
                } catch(err) {
                    alert(`Cancellation error: ${err.message}`);
                }
            }
        };
    }

    return card;
}

async function loadAnalytics() {
    const topRatedContainer = document.getElementById("analytics-top-rated");
    const recentRestoContainer = document.getElementById("analytics-recent-resto");
    const categoryContainer = document.getElementById("analytics-category");

    try {
        // Top Rated
        if (topRatedContainer && allRestaurantsData.length > 0) {
            const sortedByRating = [...allRestaurantsData].sort((a, b) => (b.rating || 0) - (a.rating || 0));
            const best = sortedByRating[0];
            topRatedContainer.innerHTML = `
                <div class="analytics-stat-highlight">
                    <h4>${best.name}</h4>
                    <p><i class="fa-solid fa-star text-amber"></i> <strong>${best.rating ? best.rating.toFixed(1) : 'N/A'}</strong> / 5.0</p>
                    <small>${best.cuisine_type} • ${best.location}</small>
                </div>
            `;
        }

        // Recent Resto
        if (recentRestoContainer && allRestaurantsData.length > 0) {
            const recent = allRestaurantsData[0];
            recentRestoContainer.innerHTML = `
                <div class="analytics-stat-highlight">
                    <h4>${recent.name}</h4>
                    <p><i class="fa-solid fa-bowl-food text-violet"></i> ${recent.cuisine_type}</p>
                    <small>${recent.location}</small>
                </div>
            `;
        }

        // Category Highlight
        if (categoryContainer) {
            categoryContainer.innerHTML = `
                <div class="analytics-stat-highlight">
                    <h4>Fine Dining & Italian</h4>
                    <p><i class="fa-solid fa-fire text-emerald"></i> High Demand Cuisine</p>
                    <small>Multimodal Groq AI Query Active</small>
                </div>
            `;
        }
    } catch (e) {
        console.warn("Analytics load error:", e);
    }
}

async function handleAddRestaurant(event) {
    event.preventDefault();
    
    const newRestaurant = {
        name: document.getElementById("resto-name").value,
        location: document.getElementById("resto-location").value,
        cuisine_type: document.getElementById("resto-cuisine").value,
        rating: parseFloat(document.getElementById("resto-rating").value) || null
    };

    try {
        await ApiService.post("/restaurants/", newRestaurant);
        alert("Restaurant added successfully!");
        document.getElementById("restaurant-form").reset();
        document.getElementById("restaurant-modal").classList.add("hidden");
        loadRestaurants();
    } catch (error) {
        console.error("Failed to add restaurant:", error);
        alert(`Error: ${error.message}`);
    }
}