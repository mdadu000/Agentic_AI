from google.adk.agents import LlmAgent
from agent.prompt import *
from agent.tools import (
    # Core
    get_all_restaurants,
    add_restaurant,
    get_menu_items_for_restaurant,
    add_menu_item,
    add_reservation,
    
    # New Functionality
    add_user_review,
    filter_restaurants_by_cuisine_tool, 
    search_for_menu_items_tool, 
    update_menu_item_price_tool, 
    remove_restaurant_tool, 
    remove_menu_item_tool,
    get_reservations_today_tool, 
    get_highest_average_rating_restaurant, 
    get_best_rated_category_dish, 
    get_reservations_per_cuisine_type_tool, 
    
    # Challenges
    get_most_recent_restaurant,
    list_large_reservations,
    get_restaurant_with_most_menu_items
) 
from constants import AGENT_NAME, AGENT_DESCRIPTION, AGENT_MODEL

root_agent = LlmAgent(
    name=AGENT_NAME,
    model=AGENT_MODEL, # Uses gemini-2.0-flash (text-only but available)
    description=AGENT_DESCRIPTION,
    instruction=ROOT_AGENT_PROMPT,
    tools=[
        # Core
        get_all_restaurants,
        add_restaurant,
        get_menu_items_for_restaurant,
        add_menu_item,
        add_reservation,
        
        # New Functionality
        add_user_review,
        filter_restaurants_by_cuisine_tool,
        search_for_menu_items_tool,
        update_menu_item_price_tool,
        remove_restaurant_tool,
        remove_menu_item_tool,
        get_reservations_today_tool,
        get_highest_average_rating_restaurant,
        get_best_rated_category_dish,
        get_reservations_per_cuisine_type_tool,
        
        # Challenges
        get_most_recent_restaurant,
        list_large_reservations,
        get_restaurant_with_most_menu_items
    ]
)