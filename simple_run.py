from OMPython import OMCSessionZMQ
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

# Create output directory if it doesn't exist
if not os.path.exists("omcoutput"):
    os.makedirs("omcoutput")

# Start an OpenModelica session
omc = OMCSessionZMQ()

# Load the .mo file with the SolarPanelGlycolSystem model
omc.sendExpression('loadFile("simple.mo")')

# Check if the model is loaded successfully
loaded = omc.sendExpression('getClassNames()')
print(f"Loaded models: {loaded}")

# Set working directory for simulation output
omc.sendExpression('cd("omcoutput")')

# Simulate the SolarPanelGlycolSystem model
result = omc.sendExpression('simulate(SolarPanelGlycolSystem, outputFormat="csv")')

# Check the results
print(f"Simulation result: {result}")

# Load the CSV file into a DataFrame
data = pd.read_csv("omcoutput/SolarPanelGlycolSystem_res.csv")

# Inspect the columns in the file
print("Available columns:", data.columns)

# Convert temperatures from Kelvin to Celsius for plotting
if "panelTemperature" in data.columns and "mixtureTemperature" in data.columns:
    data["panelTemperature_C"] = data["panelTemperature"] - 273.15
    data["mixtureTemperature_C"] = data["mixtureTemperature"] - 273.15
    
    # Plot both temperatures over time
    plt.figure(figsize=(14, 8))
    
    # Convert time from seconds to hours for better readability
    hours = data["time"] / 3600
    
    # Create the plot
    plt.plot(hours, data["panelTemperature_C"], 'r-', linewidth=2, label="Solar Panel")
    plt.plot(hours, data["mixtureTemperature_C"], 'b-', linewidth=2, label="Glycol Vessel")
    
    plt.title("Temperature Evolution of Solar Panel and Glycol Vessel Over 24 Hours", fontsize=14)
    plt.xlabel("Time (hours)", fontsize=12)
    plt.ylabel("Temperature (°C)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    
    # Add horizontal grid lines
    max_temp = max(data["panelTemperature_C"].max(), data["mixtureTemperature_C"].max())
    plt.yticks(np.arange(0, max_temp + 10, 10))
    
    # Add vertical grid lines at 2-hour intervals
    plt.xticks(range(0, 25, 2))
    
    # Add annotations for initial and final temperatures
    # Panel temperatures
    panel_initial = data["panelTemperature_C"].iloc[0]
    panel_final = data["panelTemperature_C"].iloc[-1]
    plt.annotate(f"Panel initial: {panel_initial:.1f}°C", 
                 xy=(0.5, panel_initial), 
                 xytext=(2, panel_initial+5),
                 arrowprops=dict(arrowstyle="->", color='r'), color='r')
    plt.annotate(f"Panel final: {panel_final:.1f}°C", 
                 xy=(23.5, panel_final), 
                 xytext=(21, panel_final+5),
                 arrowprops=dict(arrowstyle="->", color='r'), color='r')
    
    # Glycol temperatures
    glycol_initial = data["mixtureTemperature_C"].iloc[0]
    glycol_final = data["mixtureTemperature_C"].iloc[-1]
    plt.annotate(f"Glycol initial: {glycol_initial:.1f}°C", 
                 xy=(0.5, glycol_initial), 
                 xytext=(2, glycol_initial-10),
                 arrowprops=dict(arrowstyle="->", color='b'), color='b')
    plt.annotate(f"Glycol final: {glycol_final:.1f}°C", 
                 xy=(23.5, glycol_final), 
                 xytext=(21, glycol_final-10),
                 arrowprops=dict(arrowstyle="->", color='b'), color='b')
    
    # Add heat flow analysis
    plt.figure(figsize=(14, 8))
    
    # Plot heat flows
    plt.plot(hours, data["heatInputToPanel"], 'r-', label="Heat Input to Panel")
    plt.plot(hours, data["heatTransferPanelToVessel"], 'g-', label="Heat Transfer Panel→Vessel")
    plt.plot(hours, data["heatLossPanel"], 'r--', label="Heat Loss from Panel")
    plt.plot(hours, data["heatLossVessel"], 'b--', label="Heat Loss from Vessel")
    
    plt.title("Heat Flow Analysis Over 24 Hours", fontsize=14)
    plt.xlabel("Time (hours)", fontsize=12)
    plt.ylabel("Heat Flow (Watts)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    plt.xticks(range(0, 25, 2))
    
    # Save the figures
    plt.figure(1)
    plt.savefig("omcoutput/temperature_evolution.png", dpi=300, bbox_inches='tight')
    plt.figure(2)
    plt.savefig("omcoutput/heat_flow_analysis.png", dpi=300, bbox_inches='tight')
    
    plt.show()
    
else:
    print("Error: Required temperature columns not found in simulation results")
    print("Available columns:", data.columns)