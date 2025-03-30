import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

def respiratory_experiment_simulation():
    """Simulate the lung volumes and capacities experiment"""
    st.subheader("Experiment: Effect of Exercise on Lung Volumes")
    
    st.write("""
    This simulation demonstrates how lung volumes change with exercise.
    Adjust the parameters to see the effects.
    """)
    
    # User inputs
    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.radio("Select gender:", ["Male", "Female"])
        age = st.slider("Age (years):", 18, 80, 25)
        height = st.slider("Height (cm):", 150, 210, 170)
        
    with col2:
        exercise_intensity = st.slider("Exercise intensity:", 0, 100, 50)
        fitness_level = st.slider("Fitness level:", 1, 10, 5)
    
    # Calculate baseline values
    if gender == "Male":
        baseline_tidal = 500  # mL
        baseline_vital_capacity = 4800  # mL
        baseline_expiratory_reserve = 1200  # mL
    else:
        baseline_tidal = 400  # mL
        baseline_vital_capacity = 3600  # mL
        baseline_expiratory_reserve = 900  # mL
        
    # Adjust for height
    height_factor = height / 170
    baseline_tidal *= height_factor
    baseline_vital_capacity *= height_factor
    baseline_expiratory_reserve *= height_factor
    
    # Adjust for age
    age_factor = 1.0 - ((age - 25) * 0.005)  # Decrease by 0.5% per year above 25
    baseline_vital_capacity *= max(0.7, age_factor)
    baseline_expiratory_reserve *= max(0.7, age_factor)
    
    # Calculate exercise effects
    exercise_factor = 1.0 + (exercise_intensity * 0.015)  # Increase by up to 150%
    fitness_bonus = fitness_level * 0.03  # Up to 30% bonus for fit individuals
    
    tidal_at_rest = baseline_tidal
    tidal_during_exercise = baseline_tidal * exercise_factor * (1 + fitness_bonus)
    
    expiratory_at_rest = baseline_expiratory_reserve
    expiratory_during_exercise = baseline_expiratory_reserve * 0.85  # Typically decreases
    
    vital_at_rest = baseline_vital_capacity
    vital_during_exercise = baseline_vital_capacity * 0.95  # Slightly decreases
    
    # Display results
    st.subheader("Results:")
    
    data = {
        "Measurement": ["Tidal Volume (mL)", "Expiratory Reserve Volume (mL)", "Vital Capacity (mL)"],
        "At Rest": [round(tidal_at_rest), round(expiratory_at_rest), round(vital_at_rest)],
        "During Exercise": [round(tidal_during_exercise), round(expiratory_during_exercise), round(vital_during_exercise)]
    }
    
    df = pd.DataFrame(data)
    st.table(df)
    
    # Create visualization
    chart_data = pd.DataFrame({
        "State": ["At Rest", "During Exercise", "At Rest", "During Exercise", "At Rest", "During Exercise"],
        "Volume Type": ["Tidal", "Tidal", "Expiratory Reserve", "Expiratory Reserve", "Vital Capacity", "Vital Capacity"],
        "Volume (mL)": [
            tidal_at_rest, tidal_during_exercise, 
            expiratory_at_rest, expiratory_during_exercise,
            vital_at_rest, vital_during_exercise
        ]
    })
    
    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('State:N'),
        y=alt.Y('Volume (mL):Q'),
        color=alt.Color('State:N'),
        column=alt.Column('Volume Type:N')
    ).properties(
        width=150
    )
    
    st.altair_chart(chart)
    
    st.write("""
    **Analysis:**
    - Tidal volume increases significantly during exercise
    - Expiratory reserve volume typically decreases during exercise
    - Vital capacity slightly decreases during exercise
    
    These changes allow for more efficient oxygen delivery during physical activity.
    """)

def co2_reaction_simulation():
    """Simulate the CO2 reaction experiment from the digestive system lab"""
    st.subheader("Experiment: CO₂ Production in Digestive Processes")
    
    st.write("""
    This simulation demonstrates CO₂ production during different digestive reactions.
    Adjust the parameters to see how different conditions affect CO₂ production.
    """)
    
    # User inputs
    col1, col2 = st.columns(2)
    
    with col1:
        substrate = st.selectbox(
            "Select substrate:", 
            ["Glucose", "Starch", "Protein", "Lipid"]
        )
        
        enzyme_concentration = st.slider(
            "Enzyme concentration (mg/mL):", 
            0.1, 10.0, 5.0, 0.1
        )
        
    with col2:
        temperature = st.slider(
            "Temperature (°C):", 
            20, 45, 37
        )
        
        ph_level = st.slider(
            "pH level:", 
            1.0, 10.0, 7.0, 0.1
        )
    
    # Calculate CO2 production rates based on inputs
    # Base rates for different substrates (arbitrary units)
    base_rates = {
        "Glucose": 10,
        "Starch": 7, 
        "Protein": 5,
        "Lipid": 3
    }
    
    # Temperature effects (optimal at 37°C)
    temp_factor = 1.0 - (abs(temperature - 37) * 0.05)
    
    # pH effects (different optima for different substrates)
    ph_optima = {
        "Glucose": 7.0,
        "Starch": 7.0,
        "Protein": 2.0,  # Pepsin works in acidic environment
        "Lipid": 8.0     # Lipase works in alkaline environment
    }
    ph_factor = 1.0 - (abs(ph_level - ph_optima[substrate]) * 0.15)
    
    # Enzyme concentration effect (diminishing returns)
    enzyme_factor = 0.2 + (0.8 * (enzyme_concentration / (enzyme_concentration + 2)))
    
    # Calculate final CO2 production rate
    co2_rate = base_rates[substrate] * max(0.1, temp_factor) * max(0.1, ph_factor) * enzyme_factor
    
    # Generate time-series data
    time_points = np.arange(0, 31, 1)  # 0 to 30 minutes
    
    if substrate == "Glucose":
        # Fast initial reaction
        co2_values = [co2_rate * (1 - np.exp(-0.15 * t)) for t in time_points]
    elif substrate == "Starch":
        # Gradual increase
        co2_values = [co2_rate * (1 - np.exp(-0.1 * t)) for t in time_points]
    elif substrate == "Protein":
        # Delayed then rapid increase
        co2_values = [co2_rate * (1 - np.exp(-0.08 * max(0, t-5))) for t in time_points]
    else:  # Lipid
        # Very gradual increase
        co2_values = [co2_rate * (1 - np.exp(-0.05 * t)) for t in time_points]
    
    # Display results
    st.subheader("Results:")
    
    # Show summary data
    st.write(f"**Maximum CO₂ Production Rate:** {co2_rate:.2f} mL/min")
    
    # Display optimal conditions
    st.write(f"**Optimal pH for {substrate} digestion:** {ph_optima[substrate]}")
    st.write(f"**Current efficiency:** {max(0.1, temp_factor * ph_factor * enzyme_factor):.1%}")
    
    # Create and display the plot
    fig, ax = plt.figure(figsize=(10, 6)), plt.axes()
    ax.plot(time_points, co2_values, 'b-', linewidth=2)
    ax.set_xlabel('Time (minutes)')
    ax.set_ylabel('CO₂ Production (mL)')
    ax.set_title(f'CO₂ Production Over Time: {substrate} Digestion')
    ax.grid(True)
    
    # Add annotations about optimal conditions
    if ph_factor < 0.5:
        plt.annotate(
            f"Suboptimal pH\nOptimal pH: {ph_optima[substrate]}",
            xy=(20, co2_values[20]),
            xytext=(15, max(co2_values) * 0.7),
            arrowprops=dict(facecolor='red', shrink=0.05),
        )
    
    if temp_factor < 0.5:
        plt.annotate(
            "Suboptimal temperature\nOptimal: 37°C",
            xy=(10, co2_values[10]),
            xytext=(5, max(co2_values) * 0.6),
            arrowprops=dict(facecolor='red', shrink=0.05),
        )
    
    st.pyplot(fig)
    
    # Educational explanation
    st.write("""
    **Analysis:**
    
    - **Substrate matters**: Different nutrients produce CO₂ at different rates during digestion
    - **pH sensitivity**: Each digestive enzyme has an optimal pH range
      - Pepsin (protein digestion): Acidic (pH 1.5-2.5)
      - Amylase (starch digestion): Neutral (pH 6.7-7.0)
      - Lipase (fat digestion): Slightly alkaline (pH 7.5-8.5)
    - **Temperature dependence**: Enzyme activity is highest near body temperature (37°C)
    - **Enzyme concentration**: Higher concentration increases reaction rate up to a point
    
    This experiment demonstrates how the digestive system optimizes conditions for different nutrients.
    """)

def simulations_page():
    """Page containing all simulations"""
    st.title("Experimental Simulations")
    
    st.write("""
    Interactive simulations based on laboratory exercises. Adjust different parameters to see their effects
    on physiological and chemical processes.
    """)
    
    sim_type = st.radio(
        "Select Simulation Type:", 
        ["Respiratory Experiment", "Digestive CO₂ Production"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if sim_type == "Respiratory Experiment":
        respiratory_experiment_simulation()
    else:
        co2_reaction_simulation()
