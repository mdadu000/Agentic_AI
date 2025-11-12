// The import path is now correct because both files are in the same 'static' folder
import ApiService from "./apiService.js";

document.addEventListener("DOMContentLoaded", async () => {
  const restaurantContainer = document.getElementById("restaurants");
  const restoForm = document.getElementById("restaurant-form");
  const addRestoBtn = document.getElementById("add-restaurant-btn");
  const restoModal = document.getElementById("restaurant-modal");
  const cancelModalBtn = document.getElementById("cancel-modal-btn");

  let restaurants = [];

  async function loadRestaurants() {
    try {
      // This now calls "/restaurants" correctly
      restaurants = await ApiService.get("/restaurants");
      renderRestaurants(restaurants);
    } catch (error) {
      console.error("Failed to load restaurants:", error);
      restaurantContainer.innerHTML = "<p>Could not load restaurants. Is the server running?</p>";
    }
  }
  
  // Initial load
  loadRestaurants();

  function renderRestaurants(data) {
    restaurantContainer.innerHTML = "";

    data.forEach((r, index) => {
      const card = document.createElement("div");
      card.className = "restaurant-card";

      card.innerHTML = `
        <div class="restaurant-header">
          <h3 class="restaurant-name">
            <i class="fa-solid fa-store"></i> ${r.name}
          </h3>
          <div class="restaurant-rating">
            <i class="fa-solid fa-star" style="color:#f7b500;"></i> 
            ${r.rating ?? "N/A"}
          </div>
        </div>
        <div class="restaurant-details">
          <p class="restaurant-info">
            <i class="fa-solid fa-utensils"></i> ${r.cuisine_type || "Cuisine not listed"}
          </p>
          <p class="restaurant-info">
            <i class="fa-solid fa-map-marker-alt"></i> ${r.location || "Location unavailable"}
          </p>
        </div>
        <div class="restaurant-actions">
          <button class="edit-btn"><i class="fa-solid fa-pen"></i> Edit</button>
          <button class="delete-btn"><i class="fa-solid fa-trash"></i> Delete</button>
        </div>
      `;

      // --- Edit Button Logic ---
      const editBtn = card.querySelector(".edit-btn");
      editBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        // Pass the original object 'r' to the modal
        openEditModal(r);
      });

      // --- Delete Button Logic ---
      const deleteBtn = card.querySelector(".delete-btn");
      deleteBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        
        // Simple confirmation before deleting
        if (!confirm(`Are you sure you want to delete ${r.name}?`)) {
            return;
        }

        try {
          // This API call now works because of Step 3
          await ApiService.delete(`/restaurants/${r.id}`);
          // Refresh the list from the server
          await loadRestaurants(); 
        } catch (error) {
          console.error("Error deleting restaurant:", error);
          alert("Failed to delete restaurant. Please try again.");
        }
      });

      restaurantContainer.appendChild(card);
    });
  }

  function openEditModal(restaurant) {
    const modal = document.getElementById("editModal");
    const form = document.getElementById("editForm");

    // Prefill values
    document.getElementById("edit-name").value = restaurant.name;
    document.getElementById("edit-location").value = restaurant.location;
    document.getElementById("edit-cuisine").value = restaurant.cuisine_type;
    document.getElementById("edit-rating").value = restaurant.rating ?? "";

    modal.style.display = "flex";

    // Cancel button closes modal
    form.querySelector(".cancel-btn").onclick = () => {
      modal.style.display = "none";
    };

    // Submit logic
    form.onsubmit = async (e) => {
      e.preventDefault();

      const updatedRestaurantData = {
        // 'id' is in the URL, not the body, but we'll use it
        name: document.getElementById("edit-name").value.trim(),
        location: document.getElementById("edit-location").value.trim(),
        cuisine_type: document.getElementById("edit-cuisine").value.trim(),
        rating: parseFloat(document.getElementById("edit-rating").value) || null,
      };

      try {
        // This API call now works because of Step 3
        await ApiService.put(`/restaurants/${restaurant.id}`, updatedRestaurantData);
        modal.style.display = "none";
        // Refresh the list from the server
        await loadRestaurants(); 
      } catch (err) {
        console.error("Error updating restaurant:", err);
        alert("Failed to update restaurant.");
      }
    };
  }

  // --- Event Listeners for Add Modal ---

  addRestoBtn.addEventListener("click", () => {
    restoModal.classList.remove("hidden");
  });

  cancelModalBtn.addEventListener("click", () => {
    restoModal.classList.add("hidden");
  });

  restoForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const newResto = {
      // The backend (service/repo) will generate the ID
      name: document.getElementById("resto-name").value.trim(),
      location: document.getElementById("resto-location").value.trim(),
      cuisine_type: document.getElementById("resto-cuisine").value.trim(),
      rating: parseFloat(document.getElementById("resto-rating").value) || 0,
    };

    try {
      // This now calls POST /restaurants correctly
      await ApiService.post("/restaurants", newResto);
      restoModal.classList.add("hidden");
      restoForm.reset();
      await loadRestaurants(); // Refresh the list
    } catch (error) {
      console.error("Failed to save restaurant:", error);
      alert("Could not save restaurant. Please check the server and try again.");
    }
  });
});