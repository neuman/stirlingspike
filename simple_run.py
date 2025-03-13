from OMPython import OMCSessionZMQ
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Create output directory if it doesn't exist
if not os.path.exists("omcoutput"):
    os.makedirs("omcoutput")

# Start an OpenModelica session
omc = OMCSessionZMQ()

# Load the .mo file with the SimpleSystem model
omc.sendExpression('loadFile("SimpleSystem.mo")')

# Check if the model is loaded successfully
loaded = omc.sendExpression('getClassNames()')
print(f"Loaded models: {loaded}")

# Set working directory for simulation output
omc.sendExpression('cd("omcoutput")')


# Copy the weather data to the working directory
import shutil
shutil.copy("weatherData.csv", "omcoutput/weatherData.csv")


# Set simulation parameters to match CSV time range (0-86400 seconds, 24 hours)
sim_start = 0
sim_stop = 86400  # 24 hours in seconds
sim_interval = 3600  # 1 hour in seconds for output

# Simulate the SimpleSystem model with specified parameters
sim_options = f'''
simulate(
    SimpleSystem, 
    startTime={sim_start}, 
    stopTime={sim_stop}, 
    numberOfIntervals={int(sim_stop/sim_interval)},
    outputFormat="csv", 
    variableFilter=".*"
)
'''

omc.sendExpression("setCommandLineOptions(\"-d=initialization\")")
result = omc.sendExpression(sim_options)

# Check the results
print(f"Simulation result: {result}")

# Check for errors
error_message = omc.sendExpression("getErrorString()")
print("******************************")
print("Error Message:", error_message)
print("******************************")


# Load the CSV file into a DataFrame
data_file = "omcoutput/SimpleSystem_res.csv"
if os.path.exists(data_file):
    data = pd.read_csv(data_file)
    
    # Create a reference dataframe for the original CSV data
    try:
        # First attempt with standard CSV parsing
        weather_df = pd.read_csv("weatherData.csv", 
                             comment="#",  # Handle comment lines
                             index_col=0)  # First column is index
    except:
        # Fallback for the specific format with # and fixed width
        weather_df = pd.read_csv("weatherData.csv", 
                              skiprows=2,  # Skip the first two rows with # markers
                              delim_whitespace=False,  # Use commas
                              names=["index", "time", "ambient_temp", "solar_irradiance"])
    
    print("Weather data sample:")
    print(weather_df.head())
    
    # Inspect the columns in the simulation results file
    print("Available columns in simulation results:", data.columns)
    
    # Create time labels for x-axis (hour of day)
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    time_labels = [start_time + timedelta(hours=int(h)) for h in data['time'] / 3600]
    
    # Convert temperatures from Kelvin to Celsius for plotting
    if "panelTemperature" in data.columns and "mixtureTemperature" in data.columns and "cylinderMixtureTemperature" in data.columns:
        data["panelTemperature_C"] = data["panelTemperature"] - 273.15
        data["mixtureTemperature_C"] = data["mixtureTemperature"] - 273.15
        data["cylinderMixtureTemperature_C"] = data["cylinderMixtureTemperature"] - 273.15
        data["ambientTemperature_C"] = data["ambientTemperature"] - 273.15
        data["groundTemperature_C"] = 12.78  # 55F converted to Celsius (constant)
        
        # Create a single figure with all plots stacked vertically
        fig = plt.figure(figsize=(14, 20))  # Reduced height since we have one less plot
        
        # Create subplots with specific heights (now 5 plots)
        gs = fig.add_gridspec(5, 1, height_ratios=[2, 1, 1, 1, 1])
        ax1 = fig.add_subplot(gs[0])  # Temperature plot
        ax2 = fig.add_subplot(gs[1])  # Solar irradiance
        ax3 = fig.add_subplot(gs[2])  # Power flows
        ax4 = fig.add_subplot(gs[3])  # Cylinder heat flows
        ax5 = fig.add_subplot(gs[4])  # Temperature gradients
        
        # Set x-axis formatting for all subplots
        for ax in [ax1, ax2, ax3, ax4, ax5]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            ax.set_xlim(time_labels[0], time_labels[-1])
            ax.grid(True, alpha=0.3)
        
        # Plot temperatures
        ax1.plot(time_labels, data["panelTemperature_C"], 'r-', linewidth=2.5, label="Solar Panel")
        ax1.plot(time_labels, data["mixtureTemperature_C"], 'b-', linewidth=2.5, label="Upper Vessel")
        ax1.plot(time_labels, data["cylinderMixtureTemperature_C"], 'c-', linewidth=2.5, label="Cylinder")
        ax1.plot(time_labels, data["ambientTemperature_C"], 'g--', linewidth=1.5, label="Ambient Temp")
        
        ax1.set_title("Temperature Evolution over 24 Hours", fontsize=16)
        ax1.set_ylabel("Temperature (°C)", fontsize=12)
        ax1.legend(fontsize=12, loc='upper left')
        
        # Plot solar irradiance
        ax2.bar(time_labels, data["solarIrradiance"], color='orange', alpha=0.7, width=0.4, label="Solar Irradiance")
        ax2.set_ylabel("Solar Irradiance (W/m²)", fontsize=12)
        ax2.legend(fontsize=12)
        
        # Plot power flows
        ax3.plot(time_labels, data["electricalPowerOutput"], 'g-', linewidth=2, label="Electrical Output")
        ax3.plot(time_labels, data["heatTransferPanelToVessel"], 'm-', linewidth=2, label="Panel→Vessel Transfer")
        ax3.set_title("Power Flow Analysis over 24 Hours", fontsize=16)
        ax3.set_ylabel("Power (W)", fontsize=12)
        ax3.legend(fontsize=12)
        
        # Plot cylinder heat flows
        ax4.plot(time_labels, data["thermalPowerAbsorbed"], 'r-', linewidth=2, label="Thermal Absorption")
        ax4.plot(time_labels, data["heatTransferCylinderToGround"], 'b--', linewidth=2, label="Cylinder→Ground Transfer")
        ax4.plot(time_labels, data["heatLossCylinderInsulated"], 'g--', linewidth=2, label="Cylinder Insulated Loss")
        ax4.plot(time_labels, data["heatLossCylinderExposed"], 'y--', linewidth=2, label="Cylinder Exposed Loss")
        ax4.set_title("Heat Flow Analysis - Cylinder System", fontsize=16)
        ax4.set_ylabel("Heat Flow (W)", fontsize=12)
        ax4.legend(fontsize=12)
        
        # Plot temperature gradients
        ax5.plot(time_labels, data["panelTemperature_C"] - data["mixtureTemperature_C"], 'r-', linewidth=2, label="Panel→Vessel Gradient")
        ax5.plot(time_labels, data["mixtureTemperature_C"] - data["cylinderMixtureTemperature_C"], 'b-', linewidth=2, label="Vessel→Cylinder Gradient")
        ax5.plot(time_labels, data["cylinderMixtureTemperature_C"] - data["groundTemperature_C"], 'g-', linewidth=2, label="Cylinder→Ground Gradient")
        ax5.plot(time_labels, data["cylinderMixtureTemperature_C"] - data["ambientTemperature_C"], 'c--', linewidth=2, label="Cylinder→Ambient Gradient")
        ax5.set_title("Temperature Gradients in the System", fontsize=16)
        ax5.set_ylabel("Temperature Difference (°C)", fontsize=12)
        ax5.legend(fontsize=12)
        
        # Set x-axis label only for the bottom plot
        ax5.set_xlabel("Time", fontsize=12)
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig("omcoutput/combined_analysis_24h.png", dpi=300, bbox_inches='tight')
        
        # Generate a summary of the results including cylinder data
        max_panel_temp = data["panelTemperature_C"].max()
        max_vessel_temp = data["mixtureTemperature_C"].max()
        max_cylinder_temp = data["cylinderMixtureTemperature_C"].max()
        total_electrical_energy = np.trapezoid(data["electricalPowerOutput"], data["time"]) / 3600  # Wh
        total_thermal_energy = np.trapezoid(data["thermalPowerAbsorbed"], data["time"]) / 3600  # Wh
        total_cylinder_ground_energy = np.trapezoid(data["heatTransferCylinderToGround"], data["time"]) / 3600  # Wh
        
        print("\n===== SIMULATION SUMMARY =====")
        print(f"Maximum Solar Panel Temperature: {max_panel_temp:.2f}°C")
        print(f"Maximum Upper Vessel Temperature: {max_vessel_temp:.2f}°C")
        print(f"Maximum Cylinder Temperature: {max_cylinder_temp:.2f}°C")
        print(f"Total Electrical Energy Production: {total_electrical_energy:.2f} Wh")
        print(f"Total Thermal Energy Absorbed: {total_thermal_energy:.2f} Wh")
        print(f"Total Energy Lost to Ground: {total_cylinder_ground_energy:.2f} Wh")
        print(f"Upper Vessel Temperature Rise: {data['mixtureTemperature_C'].iloc[-1] - data['mixtureTemperature_C'].iloc[0]:.2f}°C")
        print(f"Cylinder Temperature Rise: {data['cylinderMixtureTemperature_C'].iloc[-1] - data['cylinderMixtureTemperature_C'].iloc[0]:.2f}°C")
        
        # Create a comprehensive energy flow diagram (Sankey-like visualization)
        fig6, ax7 = plt.subplots(figsize=(14, 10))
        
        # Calculate energy values for the diagram
        total_solar_energy = np.trapezoid(data["totalSolarPower"], data["time"]) / 3600  # Wh
        total_electrical_energy = np.trapezoid(data["electricalPowerOutput"], data["time"]) / 3600  # Wh
        total_thermal_energy = np.trapezoid(data["thermalPowerAbsorbed"], data["time"]) / 3600  # Wh
        panel_to_vessel = np.trapezoid(data["heatTransferPanelToVessel"], data["time"]) / 3600  # Wh
        vessel_to_ambient = np.trapz(data["heatLossVessel"], data["time"]) / 3600  # Wh
        cylinder_to_ground = np.trapz(data["heatTransferCylinderToGround"], data["time"]) / 3600  # Wh
        cylinder_insulated_loss = np.trapz(data["heatLossCylinderInsulated"], data["time"]) / 3600  # Wh
        cylinder_exposed_loss = np.trapz(data["heatLossCylinderExposed"], data["time"]) / 3600  # Wh
        
        # Create a simple bar chart to visualize energy flows
        energy_types = [
            'Solar Input', 'Electrical Output', 'Thermal Energy', 
            'Panel→Vessel', 'Vessel→Ambient',
            'Vessel→Cylinder', 'Cylinder→Ground', 
            'Cylinder Insulated Loss', 'Cylinder Exposed Loss'
        ]
        
        energy_values = [
            total_solar_energy, total_electrical_energy, total_thermal_energy,
            panel_to_vessel, vessel_to_ambient, cylinder_to_ground,
            cylinder_insulated_loss, cylinder_exposed_loss
        ]
        
        plt.tight_layout()
        plt.savefig("omcoutput/energy_flow_summary_24h.png", dpi=300, bbox_inches='tight')
        
        #plt.show()
        
    else:
        print("Error: Required temperature columns not found in simulation results")
        print("Available columns:", data.columns)
else:
    print(f"Error: Simulation result file not found at {data_file}")