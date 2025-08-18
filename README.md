# Food Business Financial Simulations

This repository contains all the Python scripts used to generate the data visualizations for the YouTube video: **"The Most Profitable Food Business Makes No Food. I Simulated It."**

## About The Project

This project uses Python, Pygame, and OpenCV to simulate and compare the financial viability of three different food business models over a two-year period:

*   **The Food Truck:** A classic mobile vendor.
*   **The Ghost Kitchen:** A modern, delivery-only kitchen.
*   **The "No-Kitchen" Restaurant:** A novel arbitrage model based on a curated dining experience.

The simulations are designed to be data-rich, incorporating multi-stage scenarios that account for variables like pricing, menu variety, and external factors like weather and local events.

### Watch The Video

**https://youtu.be/YZbaAaOWk7g**

## Getting Started

These scripts are designed to render video files directly and do not require a live display.

### Prerequisites

You will need Python 3 and the following libraries installed. You can install them using pip:

bash
pip install pygame opencv-python numpy

Running the Simulations
You can run any individual simulation script to generate its corresponding .mp4 video file. For example:

Bash
python simulation_food_truck_final.py

To render all video files for the entire project in sequence, you can use the master script:

Bash
python render_all.py


The Simulation Stages
The project is broken down into several simulation stages, each building upon the last:
Baseline: Establishes the initial financial projections with a level playing field.
Price War: Shows how customer flow changes based on realistic pricing.
Power of Choice: Introduces menu variety as a key differentiator.
External Factors: Simulates the impact of real-world events like weather and festivals.

License
This project is open-source. Feel free to use and adapt the code for your own projects.
