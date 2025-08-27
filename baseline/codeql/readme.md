# CodeQL Analysis

This repository provides CodeQL analysis for two datasets: **seccodePLT** and **Juliet**.

## Prerequisites

- Install **mingw-64**.
```bash
sudo apt install mingw-w64
```

## Usage

Run the analysis script from the root directory (`VulnScan-r0`) using one of the following commands:

- For seccodePLT:
```bash
./scripts/run_codeql.sh seccodeplt
```

- For Juliet:
```bash
./scripts/run_codeql.sh juliet
```

## Directory Structure
- **baseline/codeql/codel_analyze_data/**
  - **c/**  
    Contains data for the Juliet dataset and CodeQL results.
  - **python/**  
    Contains data for the seccodePLT dataset and CodeQL results.
