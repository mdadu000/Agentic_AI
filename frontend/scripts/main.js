import ApiService from "../services/apiService.js";

document.addEventListener("DOMContentLoaded", () => {
    loadRestaurants();
    
    const addBtn = document.getElementById("add-restaurant-btn");
    const modal = document.getElementById("restaurant-modal");
    const cancelBtn = document.getElementById("cancel-modal-btn");
    const form = document.getElementById("restaurant-form");

    if (addBtn) addBtn.addEventListener("click", () => modal.classList.remove("hidden"));
    if (cancelBtn) cancelBtn.addEventListener("click", () => modal.classList.add("hidden"));
    if (form) form.addEventListener("submit", handleAddRestaurant);
});

async function loadRestaurants() {
    const grid = document.getElementById("restaurants");
    if (!grid) return; 

    grid.innerHTML = "<p>Loading...</p>";

    try {
        const data = await ApiService.get("/restaurants/");
        grid.innerHTML = ""; 
        
        if (!data || data.length === 0) {
            grid.innerHTML = "<p>No restaurants found. Add one!</p>";
            return;
        }

        // Sort by created_at descending if available, otherwise just show
        data.reverse(); 

        data.forEach(restaurant => {
            const card = createRestaurantCard(restaurant);
            grid.appendChild(card);
        });
    } catch (error) {
        console.error("Failed to load restaurants:", error);
        grid.innerHTML = `<p>Error loading restaurants: ${error.message}</p>`;
    }
}

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

async function handleAddRestaurant(event) {
    event.preventDefault(); // Prevents page reload on submit
    
    // Gather data from form
    // Note: We do NOT send 'id', the backend will generate it.
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
        loadRestaurants(); // Reload the list immediately
    } catch (error) {
        console.error("Failed to add restaurant:", error);
        // Now this will show the specific error (e.g., "Field X is required")
        alert(`Error: ${error.message}`);
    }
}