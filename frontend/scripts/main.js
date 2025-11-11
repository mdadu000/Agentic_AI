import ApiService from "../services/apiService.js";

document.addEventListener("DOMContentLoaded", async () => {
  const restaurantContainer = document.getElementById("restaurants");
  const restoForm = document.getElementById("restaurant-form");
  const addRestoBtn = document.getElementById("add-restaurant-btn");
  const restoModal = document.getElementById("restaurant-modal");
  const cancelModalBtn = document.getElementById("cancel-modal-btn");

  let restaurants = [];

  async function loadRestaurants() {
    restaurants = await ApiService.get("/restaurants");
    renderRestaurants(restaurants);
  }
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
        openEditModal(r, data, index);
      });

      // --- Delete Button Logic ---
      const deleteBtn = card.querySelector(".delete-btn");
      deleteBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        try {
          await ApiService.delete(`/restaurants/${r.id}`);
          data.splice(index, 1);
          renderRestaurants(data);
        } catch (error) {
          console.error("Error deleting restaurant:", error);
          alert("Failed to delete restaurant. Please try again.");
        }
      });

      restaurantContainer.appendChild(card);
    });
  }

  function openEditModal(restaurant, data, index) {
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

      const updated = {
        id: restaurant.id,
        name: document.getElementById("edit-name").value.trim(),
        location: document.getElementById("edit-location").value.trim(),
        cuisine_type: document.getElementById("edit-cuisine").value.trim(),
        rating: parseFloat(document.getElementById("edit-rating").value) || null,
      };

      try {
        await ApiService.put(`/restaurants/${updated.id}`, updated);
        data[index] = updated;
        renderRestaurants(data);
        modal.style.display = "none";
      } catch (err) {
        console.error("Error updating restaurant:", err);
        alert("Failed to update restaurant.");
      }
    };
  }

  addRestoBtn.addEventListener("click", () => {
    restoModal.classList.remove("hidden");
  });

  cancelModalBtn.addEventListener("click", () => {
    restoModal.classList.add("hidden");
  });

  restoForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const newResto = {
      id: new Date().getTime().toString(),
      name: document.getElementById("resto-name").value.trim(),
      location: document.getElementById("resto-location").value.trim(),
      cuisine_type: document.getElementById("resto-cuisine").value.trim(),
      rating: parseFloat(document.getElementById("resto-rating").value) || 0,
    };

    await ApiService.post("/restaurants", newResto);
    restoModal.classList.add("hidden");
    restoForm.reset();
    await loadRestaurants();
  });
});