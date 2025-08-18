import os
import subprocess
import sys

# --- List of all simulation scripts to run in order ---
# I have used the filenames from your screenshot.
# Make sure your final, perfected scripts have these exact names.
simulation_scripts = [
    # --- Stage 1: Baseline (Corrected Profits) ---
    "simulation_food_truck.py",
    "simulation_ghost_kitchen.py",
    "simulation_no_kitchen.py",

    # --- Stage 2: Price War (Corrected Profits) ---
    "simulation_food_truck_price_war.py",
    "simulation_ghost_kitchen_price_war.py",
    "simulation_no_kitchen_price_war.py",

    # --- Stage 3: Power of Choice (Unique Emoji Disk Viz) ---
    "piechart.py", # This is the Emoji Disk Chart

    # --- Stage 4: Power of Choice (2-Year Line Charts) ---
    "simulation_food_truck_choice_war.py",
    "simulation_ghost_kitchen_choice_war.py",
    "simulation_no_kitchen_choice_war.py",
    
    # --- Stage 5: External Factors (Final Simulations) ---
    "simulation_food_truck_final.py",
    "simulation_ghost_kitchen_final.py",
    "simulation_no_kitchen_final.py"
]

# --- Directory to store the final videos ---
output_directory = "media"

def main():
    # --- Create the output directory if it doesn't exist ---
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: ./{output_directory}/")

    # --- Find the python executable in the current venv ---
    # This ensures it uses the same Python with the same libraries (pygame, opencv)
    python_executable = sys.executable
    print(f"Using Python executable: {python_executable}")

    # --- Loop through and run each script ---
    for i, script_name in enumerate(simulation_scripts):
        print("\n" + "="*50)
        print(f"--- RUNNING SCRIPT {i+1}/{len(simulation_scripts)}: {script_name} ---")
        print("="*50)
        
        if not os.path.exists(script_name):
            print(f"!!! WARNING: Script '{script_name}' not found. Skipping. !!!")
            continue

        try:
            # subprocess.run will execute the command and wait for it to complete
            process = subprocess.run(
                [python_executable, script_name],
                check=True, # This will raise an error if the script fails
                capture_output=True, # Capture stdout and stderr
                text=True # Decode stdout/stderr as text
            )
            print(f"--- SUCCESS: Finished running {script_name} ---")
            # Optional: print the script's output if you want to see the progress bars
            # print(process.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"!!! ERROR: The script '{script_name}' failed to execute. !!!")
            print("--- Error Output ---")
            print(e.stderr)
            print("--- Halting render process. Please fix the script above and try again. ---")
            # Stop the whole process if one script fails
            sys.exit(1)
        except FileNotFoundError:
             print(f"!!! ERROR: Could not find Python executable '{python_executable}'. Make sure you are in your virtual environment. !!!")
             sys.exit(1)


    print("\n" + "="*50)
    print("--- ALL SIMULATIONS RENDERED SUCCESSFULLY! ---")
    print(f"--- Your videos are in the ./{output_directory}/ folder. ---")
    print("="*50)

if __name__ == "__main__":
    main()