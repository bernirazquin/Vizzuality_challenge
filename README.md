# Total Carbon Pipeline

This repository provides a reproducible workflow for downloading, processing, and analyzing carbon data across U.S. counties.  
The pipeline integrates geospatial data (raster and vector), executes analytical steps in Jupyter notebooks, and stores results in a local SQLite database.

---

## 1. Environment Setup (Conda)

To ensure reproducibility and avoid dependency conflicts, I recommend to run this project inside a **Conda environment**.

### Create the environment from the .yml file
    conda env create -f environment.yml

### Activate the environment
    conda activate vizz_env

## **Optional**
  If you prefer to run the entire pipeline all at once, you can run: 
  ```bash 
  main.py
  ```
  However, for a clearer understanding of the workflow, including pre-visualization, post-visualization, and database query steps,
  I recommend to follow the process interactively through the Jupyter notebook  ```total_carbon_pipeline.ipynb ```.
  
##  2. Data Download

  You can obtain the dataset for this project in two ways: 

- Option A. Run through the notebook (Recommended)
   
  The notebook  ```total_carbon_pipeline.ipynb``` includes a cell that performs the same download procedure as part of the data preparation pipeline.
 
- Option B. Run ```download.py```
   
  In your terminal, execute 

 ```bash
  python download.py
 ```
  This will create the data/raw directory if it doesn't exists already.

## 3. Running SQL Queries in SQLite

  Processed data is stored in a local SQLite dataset ```total_carbon.db```

  You can query it either inside the notebook or using an external SQLite client. 
 
### Query format 
    
    SELECT column_name
    FROM table_name
    WHERE condition;
### Example 
    SELECT county_name, total_carbon
    FROM carbon_summary
    WHERE total_carbon > 1000;
