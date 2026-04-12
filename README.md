# M-Bedded Enterprise: Supply Chain Financial Simulation

A high-fidelity Monte Carlo financial engine simulating the economic impact of upgrading FMCG packaging lines from traditional Hot Melt Adhesives (HMA) to the M-Bedded blister-seal hardware system.

## 📌 Executive Summary
The Indian FMCG supply chain suffers from a critical mechanical flaw: external straws detach from Tetra Paks during transit due to severe summer heat and humidity. Historically, this was a minor write-off in traditional "Kirana" retail. However, the rapid rise of **Quick Commerce (Modern Trade)**—with automated dark stores and strict Service Level Agreements (SLAs)—has weaponized this physical defect into a massive financial bleed. 

This engine simulates a 90-Million-unit annual production line to prove the break-even timeline and net ROI of a ₹35 Lakh CAPEX hardware upgrade, factoring in thermodynamic failures, automated warehouse rejection logic, and factory floor efficiency gains.

---

## ⚙️ The Business Logic & Mathematical Modules

### 1. Thermodynamic Seasonality (`data_generator.py`)
The simulation does not use a flat failure rate. It applies a continuous sine-wave probability curve across a 365-day logistics calendar:
* **Winter Baseline:** 2% baseline failure.
* **Summer Peak:** Spikes to 12% in May/June when dry-freight truck cargo bays exceed the 55°C softening point of standard EVA hot-melt glue.

### 2. Strict Stream Isolation (`financial_engine.py`)
The engine dynamically splits rejected inventory based on the retailer type, applying different salvage math to each:
* **Traditional (Kirana) Logistics:** Assumes lenient Acceptable Quality Levels (AQL). 60% of units are manually reworked (taped back on) for a minor ₹2.50 labor penalty.
* **Modern Trade (Quick Commerce):** Assumes zero-tolerance automated warehouses. Triggers a `2.0x` Pallet Rejection Multiplier, forces 100% liquidation of rejected collateral, and applies a strict ₹5.00 corporate SLA fine strictly per defective unit.

### 3. Manufacturing Economics (`financial_engine.py`)
To ensure a robust "Hard Mode" financial model, the engine accounts for factory-floor realities:
* **Relative OEE Profit:** Calculates the 1.5% machine uptime gained by eliminating HMA glue nozzle clogs, translating the extra production volume into actual revenue (filtered strictly through a 10% FMCG profit margin).
* **CAPEX Tax Shield:** Deducts 15% machinery depreciation and 25% corporate tax credits from the M-Bedded operational burden to calculate the true recovery timeline.

---

## 🏗️ Codebase Architecture

* `config.py` — The Central Nervous System. Contains all global constants, unit economics, SLA percentages, and file paths.
* `main.py` — The Orchestrator. Triggers the ETL pipeline in a strict, reproducible sequence.
* `src/data_generator.py` — The Monte Carlo engine that builds synthetic shipment telemetry.
* `src/financial_engine.py` — The core ROI calculator that crunches the logistics bleeds and factory credits.
* `src/visualizer.py` — The Matplotlib rendering engine for executive pitch deck charts.

---

## 🚀 Installation & Usage

### Prerequisites
* Python 3.9+
* Recommended: Virtual Environment (`venv`)

### Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/MBedded-Simulation.git](https://github.com/YOUR_USERNAME/MBedded-Simulation.git)
   cd MBedded-Simulation