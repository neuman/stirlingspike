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

print("Starting OpenModelica session...")

# Load the .mo file with the SimpleSystem model
print("Loading model file...")
result = omc.sendExpression('loadFile("SimpleSystem.mo")')
print(f"Load result: {result}")

# Check if the model is loaded successfully
loaded = omc.sendExpression('getClassNames()')
print(f"Loaded models: {loaded}")

# Set working directory for simulation output
print("Setting working directory...")
omc.sendExpression('cd("omcoutput")')

# Set simulation parameters to match CSV time range (0-86400 seconds, 24 hours)
sim_start = 0
sim_stop = 86400  # 24 hours in seconds
sim_interval = 3600  # 1 hour in seconds for output

# Set solver options for better stability
print("Setting solver options...")
omc.sendExpression('setCommandLineOptions("-d=initialization,solver,steps")')

# Check model before simulation
print("Checking model...")
check_result = omc.sendExpression('checkModel(SimpleSystem)')
print(f"Model check result: {check_result}")

# Get error string after check
error_string = omc.sendExpression('getErrorString()')
print(f"Error string after check: {error_string}")

# Build the model
print("Building model...")
build_result = omc.sendExpression('buildModel(SimpleSystem)')
print(f"Build result: {build_result}")

# Simulate with progress output
print("Starting simulation...")
sim_options = f'''
simulate(
    SimpleSystem, 
    startTime={sim_start}, 
    stopTime={sim_stop}, 
    numberOfIntervals={int(sim_stop/sim_interval)},
    outputFormat="csv", 
    variableFilter=".*",
    simflags="-lv=LOG_STATS,LOG_INIT"
)
'''

result = omc.sendExpression(sim_options)
print(f"Simulation result: {result}")

# Check for errors
error_message = omc.sendExpression("getErrorString()")
print("******************************")
print("Error Message:", error_message)
print("******************************")

# Get simulation statistics
stats = omc.sendExpression("getSimulationStatistics()")
print("\nSimulation Statistics:")
print(stats)

# Load and plot results if simulation was successful
data_file = "omcoutput/SimpleSystem_res.csv"
if os.path.exists(data_file):
    print("\nLoading simulation results...")
    data = pd.read_csv(data_file)
    
    # Create time labels for x-axis
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    time_labels = [start_time + timedelta(hours=int(h)) for h in data['time'] / 3600]
    
    print("Creating plots...")
    
    # Convert temperatures from Kelvin to Celsius for plotting
    if "panelTemperature" in data.columns and "mixtureTemperature" in data.columns and "cylinderMixtureTemperature" in data.columns:
        data["panelTemperature_C"] = data["panelTemperature"] - 273.15
        data["mixtureTemperature_C"] = data["mixtureTemperature"] - 273.15
        data["cylinderMixtureTemperature_C"] = data["cylinderMixtureTemperature"] - 273.15
        data["ambientTemperature_C"] = data["ambientTemperature"] - 273.15
        data["groundTemperature_C"] = 12.78  # 55F converted to Celsius (constant)
        
        # Create a single figure with all plots stacked vertically
        fig = plt.figure(figsize=(14, 20))
        
        # Create subplots with specific heights
        gs = fig.add_gridspec(5, 1, height_ratios=[2, 1, 1, 1, 1])
        ax1 = fig.add_subplot(gs[0])  # Temperature plot
        ax2 = fig.add_subplot(gs[1])  # Solar irradiance
        ax3 = fig.add_subplot(gs[2])  # Power flows
        ax4 = fig.add_subplot(gs[3])  # Heat flows
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
        ax1.plot(time_labels, data["ambientTemperature_C"], 'g--', linewidth=1.5, label="Ambient")
        ax1.axhline(y=data["groundTemperature_C"].iloc[0], color='k', linestyle=':', label="Ground")
        
        ax1.set_title("Temperature Evolution", fontsize=16)
        ax1.set_ylabel("Temperature (°C)", fontsize=12)
        ax1.legend(fontsize=12)
        
        # Plot solar irradiance
        ax2.plot(time_labels, data["solarIrradiance"], 'orange', linewidth=2, label="Solar Irradiance")
        ax2.set_title("Solar Irradiance", fontsize=16)
        ax2.set_ylabel("W/m²", fontsize=12)
        ax2.legend(fontsize=12)
        
        # Plot power flows
        ax3.plot(time_labels, data["electricalPowerOutput"], 'g-', linewidth=2, label="Solar Panel Output")
        ax3.plot(time_labels, data["stirlingPowerOutput"], 'r-', linewidth=2, label="Stirling Output")
        ax3.plot(time_labels, data["stirlingTotalPowerOutput"], 'b--', linewidth=2, label="Total Output")
        ax3.set_title("Power Output", fontsize=16)
        ax3.set_ylabel("Power (W)", fontsize=12)
        ax3.legend(fontsize=12)
        
        # Plot heat flows
        ax4.plot(time_labels, data["heatTransferPanelToVessel"], 'r-', linewidth=2, label="Panel→Vessel")
        ax4.plot(time_labels, data["stirlingHeatFlowHot"], 'g-', linewidth=2, label="Stirling Hot Side")
        ax4.plot(time_labels, data["stirlingHeatFlowCold"], 'b-', linewidth=2, label="Stirling Cold Side")
        ax4.set_title("Heat Flows", fontsize=16)
        ax4.set_ylabel("Heat Flow (W)", fontsize=12)
        ax4.legend(fontsize=12)
        
        # Plot temperature gradients
        ax5.plot(time_labels, data["mixtureTemperature_C"] - data["cylinderMixtureTemperature_C"], 'r-', linewidth=2, label="Vessel-Cylinder ΔT")
        ax5.plot(time_labels, data["cylinderMixtureTemperature_C"] - data["groundTemperature_C"], 'b-', linewidth=2, label="Cylinder-Ground ΔT")
        ax5.set_title("Temperature Gradients", fontsize=16)
        ax5.set_ylabel("ΔT (°C)", fontsize=12)
        ax5.set_xlabel("Time", fontsize=12)
        ax5.legend(fontsize=12)
        
        plt.tight_layout()
        print("Saving plots...")
        plt.savefig("omcoutput/system_analysis.png", dpi=300, bbox_inches='tight')
        
        # Calculate and print summary statistics
        print("\n===== SIMULATION SUMMARY =====")
        print(f"Maximum Panel Temperature: {data['panelTemperature_C'].max():.1f}°C")
        print(f"Maximum Vessel Temperature: {data['mixtureTemperature_C'].max():.1f}°C")
        print(f"Maximum Cylinder Temperature: {data['cylinderMixtureTemperature_C'].max():.1f}°C")
        print(f"Maximum Solar Power Output: {data['electricalPowerOutput'].max():.1f}W")
        print(f"Maximum Stirling Power Output: {data['stirlingPowerOutput'].max():.1f}W")
        print(f"Maximum Total Power Output: {data['stirlingTotalPowerOutput'].max():.1f}W")
        
        # Calculate total energy production
        total_solar_energy = np.trapz(data['electricalPowerOutput'], data['time']) / 3600  # Wh
        total_stirling_energy = np.trapz(data['stirlingPowerOutput'], data['time']) / 3600  # Wh
        print(f"\nTotal Solar Energy Production: {total_solar_energy:.1f} Wh")
        print(f"Total Stirling Energy Production: {total_stirling_energy:.1f} Wh")
        print(f"Total Combined Energy Production: {total_solar_energy + total_stirling_energy:.1f} Wh")
        
    else:
        print("Error: Required temperature columns not found in simulation results")
        print("Available columns:", data.columns)
else:
    print(f"Error: Simulation result file not found at {data_file}")