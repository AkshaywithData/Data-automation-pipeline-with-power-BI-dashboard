# Chemical Production Data Automation & Power BI Dashboard

##  Project Overview

This project demonstrates an end-to-end data engineering and automation pipeline for chemical production data.

The pipeline takes raw CSV production files, cleans and transforms the data using Python, creates fact and dimension tables, loads the data into MySQL with primary and foreign key relationships, performs SQL analysis, and presents the results through an interactive Power BI dashboard using DAX measures.

The project is designed to demonstrate practical skills in:

- Python
- Pandas
- Data Cleaning
- Data Transformation
- Dimensional Data Modelling
- MySQL
- SQL
- Primary & Foreign Keys
- SQLAlchemy
- Power BI
- DAX
- Data Visualization
- ETL Automation
- Logging

## End to End data pipeline
```
                         RAW DATA
                            │
                            ▼
                    CSV Production Files
                            │
                            ▼
                    Python ETL Pipeline
                            │
             ┌───────────────────────────┐
             ▼                           ▼
          Cleaning                 Transformation
             │                           │
             └───────────────────────────┘
                            │
                            ▼
                  Fact & Dimension Tables
                            │
                            ▼
                         MySQL
                            │
                    ┌───────┴───────┐
                    │               │
                    │               ▼
                    ▼            PK / FK         
               SQL Analysis     Relationships       
                    │               │
                Analysis csvs       │
                                    ▼
                                Power BI
                                    │
                                    ▼
                            Interactive Dashboard
             
```

## How to Run

1. 
 ```bash
         pip install -r requirements.txt
   ```

2.   Create a '.env' file in the project root:

   - DB_USER=your_mysql_username
   - DB_PASSWORD=your_mysql_password
   - DB_HOST=localhost
   - DB_NAME=chemical_production

      The pipeline uses environment variables for the database connection. Your code loads these values using load_dotenv().


3.  Place your production CSV files inside:
```
   Raw/
   ├── production_june.csv
   ├── production_july.csv
   └── production_august.csv
```
4. Run the pipeline
```
    python etl_modelling_pipeline.py  
```

5. View the results

   After execution:

   output/
      Dimension CSV files

   Analysis/
      SQL analysis results

   logs/
      pipeline.log

6. Power BI Setup

   The project includes a Power BI `.pbix` dashboard containing the
   completed visualizations, slicers, and DAX measures.

   1. Open the `.pbix` file in Power BI Desktop.
   2. If using a different MySQL environment, update the MySQL Server
      and Database connection.
   3. Enter the required MySQL credentials if prompted.
   4. Click **Refresh** to load the latest data from MySQL.

##  Project Architecture

```
Chemical Production Data Automation
│
├── Raw/
│   ├── production_june.csv
│   ├── production_july.csv
│   └── production_august.csv
│
├── output/
│   ├── dim_plant.csv
│   ├── dim_machine.csv
│   ├── dim_shift.csv
│   ├── dim_operator.csv
│   ├── dim_product.csv
│   └── dim_date.csv
│
├── Analysis/
│   ├── plant_production.csv
│   ├── good_vs_rejected_prod.csv
│   ├── machine_prod.csv
│   ├── production_by_product.csv
│   └── operator_production.csv
│
├── logs/
│   └── pipeline.log
│
├── PowerBI/
│   └── Chemical_Production_Dashboard.pbix
│
├── Screenshots/
│   └── Dashboard.png
│
├── .env.example
├── LICENSE
├── etl_modelling_pipeline.py
├── README.md
├── requirements.txt
└── .gitignore
```


## Dataset

The project uses chemical production data containing information such as:

- Production ID
- Production Date
- Plant
- Machine
- Shift
- Operator
- Product
- Product Category
- Production Quantity
- Good Quantity
- Rejected Quantity
- Downtime Hours
- Energy Consumption

Multiple CSV files can be placed inside the Raw/ folder.

The Python pipeline automatically reads all CSV files from this folder.

## MySQL Database

The pipeline automatically creates the:

chemical_production database.

The following tables are loaded:

- dim_date
- dim_plant
- dim_machine
- dim_shift
- dim_operator
- dim_product
- fact_production


## Database Relationships
```
fact_production
      │
      ├── DateID ───────► dim_date
      │
      ├── PlantID ──────► dim_plant
      │
      ├── MachineID ────► dim_machine
      │
      ├── ShiftID ──────► dim_shift
      │
      ├── OperatorID ───► dim_operator
      │
      └── ProductID ────► dim_product
```

This creates a basic star-schema structure for analytical reporting.

## SQL Analysis

- Analysis 1 — Production by Plant

- Analysis 2 — Good vs Rejected Production

- Analysis 3 — Production by Machine

- Analysis 4 — Production by Product  

- Analysis 5 — Production by Operator


## Power BI Dashboard

KPI Cards

- Total Production
- Total Good Production
- Total Rejected Quantity
- Rejection Rate %
- Total Downtime

Slicers

- Plant
- Product
- Production Date

Visualizations
- Production Trend by Day
- Production by Plant
- Good vs Rejected Production by Plant

DAX Measures
- Total Production
- Total Good Production
- Total Rejected Quantity
- Rejection Rate %
- Total Downtime

## Logging

The pipeline uses Python's built-in logging module.

Logs are stored in:

logs/pipeline.log


## Technologies Used


 Technology  Purpose                              
 
 Python      ETL automation                        
 Pandas      Data cleaning and transformation     
 SQLAlchemy  Python–MySQL connection              
 PyMySQL     MySQL database driver                 
 MySQL       Data storage and relational modelling 
 SQL         Data analysis                         
 Power BI    Dashboard and visualization           
 DAX         Dynamic KPI calculations              
 Logging     Pipeline monitoring                   


## Outcomes

This project demonstrates the ability to:

- Build a Python ETL pipeline
- Process multiple CSV files automatically
- Clean and transform raw production data
- Create dimensional models
- Build fact and dimension tables
- Load data into MySQL
- Create primary and foreign key relationships
- Perform SQL-based analysis
- Build DAX measures
- Create interactive Power BI dashboards
- Implement pipeline logging
- Structure Python code using reusable functions

## Future Improvements

Possible future enhancements include:

- Error notification
- Windows Task Scheduler automation 
- Power BI Service scheduled refresh
- Incremental data loading


##  Project Objective
```
The main objective of this project is to demonstrate an end-to-end data engineering and automation workflow:

Raw Data
   ↓
Python ETL
   ↓
Data Cleaning
   ↓
Data Transformation
   ↓
Dimensional Modelling
   ↓
MySQL
   ↓
PK / FK Relationships
   ↓
SQL Analysis
   ↓
Power BI
   ↓
DAX
   ↓
Interactive Dashboard

```

## Loading Strategy

This version of the pipeline uses a Full Refresh loading strategy.

During each pipeline execution, the existing MySQL tables are removed
and the transformed data is loaded again from the source CSV files.

Future versions may implement incremental loading and other advanced
ETL techniques.

## Author

**Akshay Gawand**


