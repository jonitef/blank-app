import streamlit as st
from itertools import combinations

# Define constructors and their drivers
constructors = {
    "McLaren": ["Norris", "Piastri"],
    "Red Bull Racing": ["Max", "Lawson"],
    "Ferrari": ["Leclerc", "Hamilton"],
    "Mercedes": ["Russell", "Antonelli"],
    "Williams": ["Sainz", "Albon"],
    "Aston Martin": ["Alonso", "Stroll"],
    "Alpine": ["Gasly", "Doohan"],
    "Racing Bulls": ["Yuki", "Hadjar"],
    "Haas": ["Ocon", "Bearman"],
    "Kick Sauber": ["Nico", "Bortolento"]
}

# Define points for qualifying and race (with the same driver positions)
qualifying_points = {1: 10, 2: 9, 3: 8, 4: 7, 5: 6, 6: 5, 7: 4, 8: 3, 9: 2, 10: 1}
race_points = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

# For positions 11-20, assign 0 points
qualifying_points.update({pos: 0 for pos in range(11, 21)})
race_points.update({pos: 0 for pos in range(11, 21)})

# Default driver prices (same as original static values)
default_driver_prices = {
    "Norris": 29.0, "Piastri": 23.0, "Leclerc": 25.9, "Max": 28.4, "Hamilton": 24.2,
    "Antonelli": 18.4, "Russell": 21.0, "Lawson": 18.0, "Sainz": 13.1, "Gasly": 11.8,
    "Albon": 12.0, "Yuki": 9.6, "Doohan": 7.2, "Ocon": 7.3, "Alonso": 8.8,
    "Bearman": 6.7, "Hadjar": 6.2, "Stroll": 8.1, "Nico": 6.4, "Bortolento": 6.0
}

# Default constructor prices (same as original static values)
default_constructor_prices = {
    "McLaren": 30.0, "Ferrari": 27.1, "Red Bull Racing": 25.2, "Mercedes": 22.7,
    "Williams": 13.1, "Alpine": 9.5, "Aston Martin": 8.5, "Racing Bulls": 8.0,
    "Haas": 7.0, "Kick Sauber": 6.2
}

# Add UI input for budget
st.sidebar.header("Adjust Your Budget")
BUDGET = st.sidebar.number_input("Select your budget", min_value=50.0, max_value=200.0, value=100.0, step=1.0)

# Input for driver prices with default values
st.sidebar.header("Adjust Driver Prices")
driver_prices = {}

for driver, default_price in default_driver_prices.items():
    driver_prices[driver] = st.sidebar.number_input(f"Price of {driver}", min_value=1.0, max_value=100.0, value=default_price, step=0.1)

# Input for constructor prices with default values
st.sidebar.header("Adjust Constructor Prices")
constructor_prices = {}

for constructor, default_price in default_constructor_prices.items():
    constructor_prices[constructor] = st.sidebar.number_input(f"Price of {constructor}", min_value=1.0, max_value=100.0, value=default_price, step=0.1)

# Input for driver order - QUALIFYING (this order will be used for qualifying)
st.header("Enter Driver Order for Qualifying (1st to 20th)")

# Initialize a list to keep track of the selected drivers
selected_qualifying_drivers = []

# Create a dictionary for the driver positions in qualifying
qualifying_driver_order = []

# Create a selectbox for each position for qualifying, ensuring no driver is repeated
for i in range(20):
    available_drivers = [driver for driver in driver_prices.keys() if driver not in selected_qualifying_drivers]
    selected_driver = st.selectbox(f"Qualifying Position {i + 1}", available_drivers)
    qualifying_driver_order.append(selected_driver)
    selected_qualifying_drivers.append(selected_driver)  # Add the selected driver to the list

# Input for driver order - RACE (this order will be used for the race)
st.header("Enter Driver Order for Race (1st to 20th)")

# Initialize a list to keep track of the selected drivers for the race
selected_race_drivers = []

# Create a dictionary for the driver positions in race
race_driver_order = []

# Create a selectbox for each position for the race, ensuring no driver is repeated
for i in range(20):
    available_drivers = [driver for driver in driver_prices.keys() if driver not in selected_race_drivers]
    selected_driver = st.selectbox(f"Race Position {i + 1}", available_drivers)
    race_driver_order.append(selected_driver)
    selected_race_drivers.append(selected_driver)  # Add the selected driver to the list

# Input for 2x Boost Driver Selection
st.sidebar.header("Select Driver for 2x Boost")
boost_driver = st.sidebar.selectbox("Select driver to receive 2x points", list(driver_prices.keys()))

# Create a dictionary for driver positions (for qualifying and race)
qualifying_driver_positions = {driver: i + 1 for i, driver in enumerate(qualifying_driver_order)}
race_driver_positions = {driver: i + 1 for i, driver in enumerate(race_driver_order)}

# Assign points for both qualifying and race based on the input positions
qualifying_driver_points = {driver: qualifying_points[qualifying_driver_positions[driver]] for driver in driver_prices}
race_driver_points = {driver: race_points[race_driver_positions[driver]] for driver in driver_prices}

# Apply the 2x boost to the selected driver (for both qualifying and race)
qualifying_driver_points[boost_driver] *= 2
race_driver_points[boost_driver] *= 2

# Calculate total points for each driver (qualifying + race)
driver_total_points = {driver: qualifying_driver_points[driver] + race_driver_points[driver] for driver in driver_prices}

# Compute total constructor points (sum of driver points)
constructor_total_points = {
    constructor: driver_total_points[drivers[0]] + driver_total_points[drivers[1]]
    for constructor, drivers in constructors.items()
}

# Calculate qualifying bonuses for constructors
def get_qualifying_bonus(constructor_drivers):
    q2_count = sum(1 for driver in constructor_drivers if qualifying_driver_positions[driver] <= 15)
    q3_count = sum(1 for driver in constructor_drivers if qualifying_driver_positions[driver] <= 10)

    if q3_count == 2:
        return 10  # Both drivers in Q3
    elif q3_count == 1:
        return 5   # One driver in Q3
    elif q2_count == 2:
        return 3   # Both drivers in Q2
    elif q2_count == 1:
        return 1   # One driver in Q2
    else:
        return -1  # Neither driver in Q2

# Add the qualifying bonuses to constructor points
constructor_qualifying_bonuses = {
    constructor: get_qualifying_bonus(drivers)
    for constructor, drivers in constructors.items()
}

# Function to calculate the best team
def calculate_best_team(excluded_drivers, excluded_constructors):
    best_team = None
    best_score = 0

    # Filter out the excluded drivers and constructors from the combinations
    available_drivers = [driver for driver in driver_prices.keys() if driver not in excluded_drivers]
    available_constructors = [constructor for constructor in constructor_prices.keys() if constructor not in excluded_constructors]

    # Try all combinations of 5 drivers from the available ones
    for driver_combo in combinations(available_drivers, 5):
        driver_cost = sum(driver_prices[d] for d in driver_combo)
        driver_score = sum(driver_total_points[d] for d in driver_combo)

        # Try all combinations of 2 constructors from the available ones
        for constructor_combo in combinations(available_constructors, 2):
            constructor_cost = sum(constructor_prices[c] for c in constructor_combo)
            constructor_score = sum(constructor_total_points[c] for c in constructor_combo) + sum(constructor_qualifying_bonuses[c] for c in constructor_combo)

            total_cost = driver_cost + constructor_cost
            total_score = driver_score + constructor_score

            if total_cost <= BUDGET and total_score > best_score:
                best_score = total_score
                best_team = (driver_combo, constructor_combo, total_cost, total_score)
    
    return best_team

# Sidebar: Excluded drivers and constructors selection
excluded_drivers = st.sidebar.multiselect(
    "Select drivers you don't want in the optimal team:",
    options=list(driver_prices.keys())
)

excluded_constructors = st.sidebar.multiselect(
    "Select constructors you don't want in the optimal team:",
    options=list(constructor_prices.keys())
)

# Recalculate button
if st.sidebar.button("Recalculate Best Team"):
    best_team = calculate_best_team(excluded_drivers, excluded_constructors)

    # Display the best team
    if best_team:
        st.header(f"Best Team (Under {BUDGET}M Budget)")
        st.write("Drivers: ", best_team[0])
        st.write("Constructors: ", best_team[1])
        st.write("Total Cost: ", best_team[2], "M")
        st.write("Total Score: ", best_team[3])
    else:
        st.write(f"No valid team found under the {BUDGET}M budget.")

# ----------- RIGHT SIDEBAR TO MANUALLY SELECT TEAM AND CALCULATE POINTS -----------

st.sidebar.header("Manually Select Your Team")

# Manual team selection: Select 5 drivers
selected_drivers_manual = []
for i in range(5):
    selected_driver_manual = st.sidebar.selectbox(f"Select Driver {i+1}", list(driver_prices.keys()), key=f"manual_driver_{i}")
    selected_drivers_manual.append(selected_driver_manual)

# Manual constructor selection: Select 2 constructors
selected_constructors_manual = []
for i in range(2):
    selected_constructor_manual = st.sidebar.selectbox(f"Select Constructor {i+1}", list(constructor_prices.keys()), key=f"manual_constructor_{i}")
    selected_constructors_manual.append(selected_constructor_manual)

# Calculate total cost for the selected team
manual_driver_cost = sum(driver_prices[d] for d in selected_drivers_manual)
manual_constructor_cost = sum(constructor_prices[c] for c in selected_constructors_manual)

# Calculate points for the selected manual team
manual_driver_points = sum(driver_total_points[d] for d in selected_drivers_manual)
manual_constructor_points = sum(constructor_total_points[c] for c in selected_constructors_manual) + sum(constructor_qualifying_bonuses[c] for c in selected_constructors_manual)

# Display the selected manual team and calculate the total score and cost
st.write(f"**Your Selected Manual Team:**")
st.write(f"Drivers: {selected_drivers_manual}")
st.write(f"Constructors: {selected_constructors_manual}")
st.write(f"Total Team Cost: {manual_driver_cost + manual_constructor_cost}M")
st.write(f"Total Points: {manual_driver_points + manual_constructor_points}")
