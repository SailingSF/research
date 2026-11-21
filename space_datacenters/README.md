# Purpose

This repo contains the calculations and assumptions for a blog post about the feasibility of space based datacenters as Elon Musk has described them. I use some clarifications, simplifications, and assumptions based on the conversation Elon had with Dwarkesh Patel, mentioned here: [https://www.dwarkesh.com/p/notes-on-space-gpus](https://www.dwarkesh.com/p/notes-on-space-gpus)

# Space Datacenters Notebook Setup

This project uses Python 3.14 and a local virtual environment.

**Windows (PowerShell):** run `.\scripts\setup_env.ps1`, then `.\.venv\Scripts\Activate.ps1` and `jupyter notebook`. This also installs `pywin32`, which the Part 2 SolidWorks scripts in `cad/` use. On macOS/Linux, use `./scripts/setup_env.sh` or the steps below.

## 1) Create and activate the environment

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

## 2) Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Register a Jupyter kernel for this project

```bash
python -m ipykernel install --user --name space_datacenters_py314 --display-name "Python 3.14 (space_datacenters)"
```

## 4) Launch Jupyter

```bash
jupyter notebook
```

Then open:

- `space_gpu_datacenter_simplified.ipynb`

and select kernel:

- `Python 3.14 (space_datacenters)`

# Radiator panel drawing (SolidWorks)

`cad/radiator/` designs one deployable radiator panel in detail (honeycomb sandwich with a
pumped ammonia loop) and makes a toleranced engineering drawing of it (ASME Y14.5, mm).
With SolidWorks open, from the repo root:

```powershell
.venv\Scripts\python.exe cad\radiator\build_radiator.py   # parts + assembly, prints the mass roll-up
.venv\Scripts\python.exe cad\radiator\make_drawing.py     # radiator_panel.SLDDRW, .pdf, .png, and images/radiator_panel_drawing.jpg (blog)
```

Design parameters are at the top of `build_radiator.py`; the drawing follows them. Every
dimension the script places is checked against the value it should measure.

