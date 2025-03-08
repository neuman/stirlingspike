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
shutil.copy("weatherData.txt", "omcoutput/weatherData.txt")

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
    if "panelTemperature" in data.columns and "mixtureTemperature" in data.columns:
        data["panelTemperature_C"] = data["panelTemperature"] - 273.15
        data["mixtureTemperature_C"] = data["mixtureTemperature"] - 273.15
        data["ambientTemperature_C"] = data["ambientTemperature"] - 273.15
        
        # Create a figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [2, 1]})
        
        # Convert time from seconds to hours for better readability
        hours = data["time"] / 3600
        
        # Plot temperatures
        ax1.plot(hours, data["panelTemperature_C"], 'r-', linewidth=2.5, label="Solar Panel")
        ax1.plot(hours, data["mixtureTemperature_C"], 'b-', linewidth=2.5, label="Glycol Vessel")
        ax1.plot(hours, data["ambientTemperature_C"], 'g--', linewidth=1.5, label="Ambient Temp")
        
        ax1.set_title("Temperature Evolution over 24 Hours", fontsize=16)
        ax1.set_xlabel("Time (hours)", fontsize=12)
        ax1.set_ylabel("Temperature (°C)", fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=12, loc='upper left')
        
        # Set x-axis limits
        ax1.set_xlim(0, 24)
        
        # Add vertical grid lines at 2-hour intervals
        ax1.set_xticks(range(0, 25, 2))
        
        # Plot solar irradiance on second subplot
        ax2.bar(hours, data["solarIrradiance"], color='orange', alpha=0.7, width=0.4, label="Solar Irradiance")
        ax2.set_xlabel("Time (hours)", fontsize=12)
        ax2.set_ylabel("Solar Irradiance (W/m²)", fontsize=12)
        ax2.set_xlim(0, 24)
        ax2.set_xticks(range(0, 25, 2))
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=12)
        
        plt.tight_layout()
        plt.savefig("omcoutput/solar_glycol_system_24h.png", dpi=300, bbox_inches='tight')
        
        # Create a second figure to analyze power flows
        fig2, ax3 = plt.subplots(figsize=(14, 8))
        
        # Plot power flows
        ax3.plot(hours, data["totalSolarPower"], 'y-', linewidth=2, label="Total Solar Power")
        ax3.plot(hours, data["electricalPowerOutput"], 'g-', linewidth=2, label="Electrical Output")
        ax3.plot(hours, data["thermalPowerAbsorbed"], 'r-', linewidth=2, label="Thermal Absorption")
        ax3.plot(hours, data["heatTransferPanelToVessel"], 'm-', linewidth=2, label="Panel→Vessel Transfer")
        
        ax3.set_title("Power Flow Analysis over 24 Hours", fontsize=16)
        ax3.set_xlabel("Time (hours)", fontsize=12)
        ax3.set_ylabel("Power (W)", fontsize=12)
        ax3.grid(True, alpha=0.3)
        ax3.legend(fontsize=12)
        ax3.set_xlim(0, 24)
        ax3.set_xticks(range(0, 25, 2))
        
        plt.tight_layout()
        plt.savefig("omcoutput/power_flow_analysis_24h.png", dpi=300, bbox_inches='tight')
        
        # Generate a summary of the results
        max_panel_temp = data["panelTemperature_C"].max()
        max_glycol_temp = data["mixtureTemperature_C"].max()
        total_electrical_energy = np.trapezoid(data["electricalPowerOutput"], data["time"]) / 3600  # Wh
        total_thermal_energy = np.trapezoid(data["thermalPowerAbsorbed"], data["time"]) / 3600  # Wh
        
        print("\n===== SIMULATION SUMMARY =====")
        print(f"Maximum Solar Panel Temperature: {max_panel_temp:.2f}°C")
        print(f"Maximum Glycol Vessel Temperature: {max_glycol_temp:.2f}°C")
        print(f"Total Electrical Energy Production: {total_electrical_energy:.2f} Wh")
        print(f"Total Thermal Energy Absorbed: {total_thermal_energy:.2f} Wh")
        print(f"Glycol Temperature Rise: {data['mixtureTemperature_C'].iloc[-1] - data['mixtureTemperature_C'].iloc[0]:.2f}°C")
        
        # Create a third figure showing all the heat flows
        fig3, ax4 = plt.subplots(figsize=(14, 8))
        
        # Plot all heat flows
        ax4.plot(hours, data["thermalPowerAbsorbed"], 'r-', linewidth=2, label="Thermal Absorption")
        ax4.plot(hours, data["radiativeLossPanel"], 'c-', linewidth=2, label="Radiative Loss")
        ax4.plot(hours, data["convectiveLossPanel"], 'b-', linewidth=2, label="Convective Loss (Panel)")
        ax4.plot(hours, data["heatTransferPanelToVessel"], 'm-', linewidth=2, label="Panel→Vessel Transfer")
        ax4.plot(hours, data["heatLossVessel"], 'k-', linewidth=2, label="Vessel Heat Loss")
        
        ax4.set_title("Heat Flow Analysis over 24 Hours", fontsize=16)
        ax4.set_xlabel("Time (hours)", fontsize=12)
        ax4.set_ylabel("Heat Flow (W)", fontsize=12)
        ax4.grid(True, alpha=0.3)
        ax4.legend(fontsize=12)
        ax4.set_xlim(0, 24)
        ax4.set_xticks(range(0, 25, 2))
        
        plt.tight_layout()
        plt.savefig("omcoutput/heat_flow_analysis_24h.png", dpi=300, bbox_inches='tight')
        
        plt.show()
        
    else:
        print("Error: Required temperature columns not found in simulation results")
        print("Available columns:", data.columns)
else:
    print(f"Error: Simulation result file not found at {data_file}")
