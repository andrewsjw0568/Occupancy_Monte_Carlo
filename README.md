# Occupancy Monte Carlo Simulation

This repository contains the simulation code for generating and analysing meeting room occupancy using a Monte Carlo approach. It includes:

- Artificial meeting schedule generation
- Probability mass function (PMF) estimation
  - Type I PMFs: Input probability distributions (ground truth)
  - Type II PMFs: Output from Monte Carlo simulations
  - Type III PMFs: PMFs calculated from simulated occupancy data
  - Type IV PMFs: PMFs calculated from simulated occupied data
- Confidence intervals and cancellation probability analysis


## 🧪 Key Components

- `Occupancy_Simulator.ipynb`: A high-level script to run simulations using `ScheduleManager.py` and output PMFs (Type I–IV) for meeting durations, occupancy levels, and meeting frequency.
- `Meeting_Cancellation_Rate.ipynb`: Jupyter Notebook that uses `ScheduleManager_cancel.py` to generate and analyse meeting cancellation rates under different scheduling configurations.

This tool is designed for academic research on shared space utilisation and stochastic scheduling. It allows users to generate synthetic meeting room schedules for analysis. The visualisation and statistical analysis in the associated study were performed on generated datasets and are not included here.

