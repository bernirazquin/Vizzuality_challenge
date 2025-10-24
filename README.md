# Total Carbon Pipeline

This repository provides a reproducible workflow for downloading, processing, and analyzing carbon data across U.S. counties.  
The pipeline integrates geospatial data (raster and vector), executes analytical steps in Jupyter notebooks, and stores results in a local SQLite database.

---

## 1. Environment Setup (Conda)

To ensure reproducibility and avoid dependency conflicts, it is recommended to run this project inside a **Conda environment**.

# Create the environment from the .yml file
conda env create -f environment.yml

# Activate the environment
conda activate vizz_env

### Activate the environment
    conda activate vizz_env

## 2. Data Download

You can obtain the dataset for this projects in two ways: 

## Option A. Run download.py 
 In your terminal, execute 

 ```bash
    python download.py
 ```
 - This will create the data/raw directory if it doesn't exists already.
 - Download dataset

## Option B. Run through the notebook (Recomended) 
 The notebook total_carbon_pipeline.ipynb includes a cell that performs the same download procedure as part of the data preparation pipeline.

# 3. Running SQL Queries in SQLite

Processed data is stored in a local SQGLite dataset (total_carbon.db)
You can query it either inside the notebook or using an external SQLite client. 
 
 #Query format 
    
    SELECT column_name
    FROM table_name
    WHERE condition;
 ## Example 
    SELECT county_name, total_carbon
    FROM carbon_summary
    WHERE total_carbon > 1000;
