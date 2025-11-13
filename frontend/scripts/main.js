import ApiService from "../services/apiService.js";

document.addEventListener("DOMContentLoaded", () => {
    loadRestaurants();
    
    // Modal controls
    const addBtn = document.getElementById("add-restaurant-btn");
    const modal = document.getElementById("restaurant-modal");
    const cancelBtn = document.getElementById("cancel-modal-btn");
    const form = document.getElementById("restaurant-form");

    if (addBtn) addBtn.addEventListener("click", () => modal.classList.remove("hidden"));
    if (cancelBtn) cancelBtn.addEventListener("click", () => modal.classList.add("hidden"));
    if (form) form.addEventListener("submit", handleAddRestaurant);
});

/**
 * Fetches restaurants from the API and renders them.
 * This assumes your backend has a RESTful endpoint at /restaurants/
 */
async function loadRestaurants() {
    const grid = document.getElementById("restaurants");
    if (!grid) return; // Not on the homepage

    grid.innerHTML = ""; // Clear existing

    try {
        // We use the raw endpoint, not the agent tool, for a direct UI feed
        const data = await ApiService.get("/restaurants/");
        
        if (!data || data.length === 0) {
            grid.innerHTML = "<p>No restaurants found. Add one!</p>";
            return;
        }

        data.forEach(restaurant => {
            const card = createRestaurantCard(restaurant);
            grid.appendChild(card);
        });
    } catch (error) {
        console.error("Failed to load restaurants:", error);
        grid.innerHTML = `<p>Error loading restaurants: ${error.message}</p>`;
    }
}

/**
 * Creates a DOM element for a single restaurant.
 */
function createRestaurantCard(restaurant) {
    const card = document.createElement("div");
    card.className = "restaurant-card";
    
    const ratingHTML = restaurant.rating
        ? `<div class="restaurant-rating">
             <i class="fa-solid fa-star"></i> ${restaurant.rating.toFixed(1)}
           </div>`
        : '';

    card.innerHTML = `
        <div class="restaurant-header">
            <h3 class="restaurant-name">${restaurant.name}</h3>
            ${ratingHTML}
        </div>
        <div class="restaurant-details">
            <p class="restaurant-info">
                <i class="fa-solid fa-map-pin"></i>
                <span>${restaurant.location}</span>
            </p>
            <p class="restaurant-info">
                <i class="fa-solid fa-bowl-food"></i>
                <span>${restaurant.cuisine_type}</span>
            </p>
        </div>
    `;
    return card;
}

/**
 * Handles the "Add Restaurant" form submission.
 */
async function handleAddRestaurant(event) {
    event.preventDefault();
    const form = event.target;
    
    const newRestaurant = {
        // ID should be set by the backend
        name: document.getElementById("resto-name").value,
        location: document.getElementById("resto-location").value,
        cuisine_type: document.getElementById("resto-cuisine").value,
        rating: parseFloat(document.getElementById("resto-rating").value) || null
    };

    try {
        // We call the direct API endpoint for creating a restaurant
        await ApiService.post("/restaurants/", newRestaurant);
        
        // Success
        form.reset();
        document.getElementById("restaurant-modal").classList.add("hidden");
        loadRestaurants(); // Refresh the list
    } catch (error) {
        console.error("Failed to add restaurant:", error);
        alert(`Error: ${error.message}`);
    }
}