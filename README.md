# CFST Ultimate Load Prediction GUI

This repository contains a Python-based graphical user interface (GUI)
for predicting the ultimate load-carrying capacity of
concrete-filled steel tubular (CFST) columns considering corrosion.

## Description

The developed GUI provides ultimate load predictions for circular and
rectangular CFST columns using machine-learning models.

For circular CFST columns, a CatBoost regression model is used.

For rectangular CFST columns, a Gaussian Process Regression (GPR) model
is used.

The models are provided as pre-trained Joblib files and can be used
directly through the graphical user interface.

## Input Parameters

The GUI requires geometric, material, and corrosion-related parameters
of the CFST columns, including:

- Section dimensions
- Steel tube thickness
- Column length
- Concrete compressive strength
- Concrete elastic modulus
- Steel yield strength
- Steel ultimate strength
- Steel elastic modulus
- Corrosion level

Additional derived parameters are automatically calculated by the
program where required.

## Prediction Models

| Section Type | Model | Model File |
|---|---|---|
| Circular | CatBoost Regression | `CatBoost_CFST.joblib` |
| Rectangular | Gaussian Process Regression (GPR) | `GPR_CFST.joblib` |

## Requirements

The program was developed using Python 3.12.

The required packages and their versions are provided in
`requirements.txt`.

Install the required packages using:

```bash
pip install -r requirements.txt
