import pandas as pd
import glob
from sqlalchemy import text,create_engine
import os
import logging
from dotenv import load_dotenv


os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
                           
def load_data():

    logger.info("Pipeline started")
    dfs = []

    files = glob.glob("Raw/*.csv")

    logger.info(f"Raw CSV files found: {len(files)}")

    for file in files:

        logger.info(f"Reading file: {file}")

        df = pd.read_csv(file)

        df["ProductionDate"] = pd.to_datetime(
            df["ProductionDate"],
            format="%d-%m-%Y",
            errors="coerce"
        )
        dfs.append(df)

        logger.info("All raw files loaded successfully")

    return dfs

def clean_data(dfs):

    logger.info("Data cleaning started")

    raw_df = pd.concat(dfs, ignore_index=True)

    logger.info(f"Total rows loaded: {len(raw_df)}")

    raw_df["ProductionDate"] = pd.to_datetime(raw_df["ProductionDate"], errors = "coerce")

    raw_df["Plant"] = raw_df["Plant"].str.strip()
    raw_df["Machine"] = raw_df["Machine"].str.strip()
    raw_df["Operator"] = raw_df["Operator"].str.strip()
    raw_df["Product"] = raw_df["Product"].str.strip()

    logger.info("Data cleaning completed")

    return raw_df

def create_dimensions(raw_df):

    logger.info("Creating dimension tables")

    dim_plant = raw_df[["Plant"]].drop_duplicates().reset_index(drop=True)
    dim_plant["PlantID"] = dim_plant.index + 1
    dim_plant = dim_plant[["PlantID", "Plant"]]

    dim_machine = raw_df[["Machine"]].drop_duplicates().reset_index(drop=True)
    dim_machine["MachineID"] = dim_machine.index + 1
    dim_machine = dim_machine[["MachineID", "Machine"]]


    dim_shift = raw_df[["Shift"]].drop_duplicates().reset_index(drop=True)
    dim_shift["ShiftID"] = dim_shift.index + 1  
    dim_shift = dim_shift[["ShiftID", "Shift"]]

    dim_operator = raw_df[["Operator"]].drop_duplicates().reset_index(drop=True)
    dim_operator["OperatorID"] = dim_operator.index + 1
    dim_operator = dim_operator[["OperatorID", "Operator"]]


    dim_product = raw_df[
        ["Product", "ProductCategory"]
    ].drop_duplicates().reset_index(drop=True)
    dim_product["ProductID"] = dim_product.index + 1
    dim_product = dim_product[["ProductID", "Product", "ProductCategory"]]

    dim_date = raw_df[["ProductionDate"]].drop_duplicates().reset_index(drop = True)
    dim_date["DateID"] = dim_date.index + 1
    dim_date = dim_date[["DateID", "ProductionDate"]]

    dim_date["Month"] = dim_date["ProductionDate"].dt.month
    dim_date["Year"] = dim_date["ProductionDate"].dt.year

    dimensions = {
        "dim_plant": dim_plant,
        "dim_machine": dim_machine,
        "dim_shift": dim_shift,
        "dim_operator": dim_operator,
        "dim_product": dim_product,
        "dim_date": dim_date
    }

    logger.info("Dimension tables created successfully")

    return dimensions

def create_fact_table(raw_df, dimensions):

    logger.info("Creating fact table")

    fact_production = raw_df[
        [
            "ProductionID",
            "ProductionDate",
            "Plant",
            "Machine",
            "Shift",
            "Operator",
            "Product",
            "ProductCategory",
            "ProductionQty",
            "GoodQty",
            "RejectedQty",
            "DowntimeHours",
            "EnergyKwh"
        ]
    ].copy()


    fact_production = fact_production.merge(dimensions["dim_plant"][["PlantID", "Plant"]], 
                                            on = "Plant", 
                                            how = "left")

    fact_production = fact_production.merge(dimensions["dim_machine"][["MachineID", "Machine"]],
                                            on  = "Machine",
                                            how = "left")

    fact_production = fact_production.merge(dimensions["dim_shift"][["ShiftID", "Shift"]],
                                            on = "Shift",
                                            how = "left")
    fact_production = fact_production.merge(dimensions["dim_operator"][["OperatorID", "Operator"]],
                                            on = "Operator",
                                            how = "left")
    fact_production = fact_production.merge(dimensions["dim_product"][["ProductID", "Product", "ProductCategory"]],
                                            on = ["Product", "ProductCategory"], 
                                            how = "left")
    fact_production = fact_production.merge(dimensions["dim_date"][["DateID", "ProductionDate", "Month", "Year"]],
                                            on = "ProductionDate",
                                            how = "left")

    fact_production = fact_production[["ProductionID", 
                                    "DateID",
                                    "PlantID", 
                                    "MachineID", 
                                    "ShiftID", 
                                    "OperatorID",
                                    "ProductID",
                                    "ProductionQty",
                                    "GoodQty",
                                    "RejectedQty",
                                    "DowntimeHours",
                                    "EnergyKwh"]]
    logger.info(
        f"Fact table created successfully: "
        f"{len(fact_production)} rows"
    )

    return fact_production

def save_dimensions(dimensions):

    os.makedirs("output", exist_ok = True)

    for name, df in dimensions.items():
        df.to_csv(f"output/{name}.csv", index = False)

def create_database():

    logger.info(
        "Creating/checking MySQL database"
    )

    load_dotenv()

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")

    engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}"
    )

    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS chemical_production"))


    engine = create_engine((
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        ))
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fact_production"))
        conn.execute(text("DROP TABLE IF EXISTS dim_date"))
        conn.execute(text("DROP TABLE IF EXISTS dim_plant"))
        conn.execute(text("DROP TABLE IF EXISTS dim_machine"))
        conn.execute(text("DROP TABLE IF EXISTS dim_shift"))
        conn.execute(text("DROP TABLE IF EXISTS dim_operator"))
        conn.execute(text("DROP TABLE IF EXISTS dim_product"))

    logger.info(
        "Database ready and old tables removed"
    )

    return engine

def load_to_mysql(dimensions, fact_production, engine):

    logger.info(
        "Loading dimension tables into MySQL"
    )
    for name, df in dimensions.items():

        df.to_sql(
            name,
            con=engine,
            if_exists="replace",
            index=False
        )

    fact_production.to_sql(
        "fact_production",
        con=engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        "All tables loaded into MySQL successfully"
    )


def create_relationships(engine):

    logger.info(
        "Creating primary and foreign keys"
    )

    with engine.begin() as conn:
        #primary keys

        conn.execute(text("""
            Alter table dim_date 
            add primary key (DateID)
        """))

        conn.execute(text("""
            Alter table dim_machine
            add primary key (MachineID)
        """))

        conn.execute(text("""
            Alter table dim_operator
            add primary key(OperatorID)
        """))

        conn.execute(text("""
            Alter table dim_plant
            add primary key(PlantID)
        """))

        conn.execute(text("""
            Alter table dim_product
            add primary key(ProductID)
        """))

        conn.execute(text("""
            Alter table dim_shift
            add primary key(ShiftID)
        """))

        conn.execute(text("""
            Alter table fact_production
            add primary key(ProductionID)
        """))


        #foreign keys 

        conn.execute(text("""
            Alter table fact_production
            add constraint fk_date
            foreign key(DateID)
            references dim_date(DateID)
        """))

        conn.execute(text("""
            Alter table fact_production
            add constraint fk_plant
            foreign key(PlantID)
            references dim_plant(PlantID)
        """))

        conn.execute(text("""
            Alter table fact_production
            add constraint fk_machine
            foreign key(MachineID)
            references dim_machine(MachineID)
            """))

        conn.execute(text("""
            Alter table fact_production
            add constraint fk_shift
            foreign key(ShiftID)
            references dim_shift(ShiftID)
        """))

        conn.execute(text("""
                Alter table fact_production
                add constraint fk_operator
                foreign key(OperatorID)
                references dim_Operator(OperatorID)
            """))


        conn.execute(text("""
                Alter table fact_production
                add constraint fk_product
                foreign key(ProductID)
                references dim_Product(ProductID)
            """))
        
    logger.info(
        "Primary keys and foreign keys created successfully"
    )

def run_analysis(engine):

    logger.info(
        "Running SQL analysis queries"
    )
    
    os.makedirs("Analysis", exist_ok=True)
    #total production by plant

    query1 = """SELECT
        p.Plant,
        SUM(f.ProductionQty) AS TotalProduction
    FROM fact_production f
    JOIN dim_plant p
        ON f.PlantID = p.PlantID
    GROUP BY p.Plant
    ORDER BY TotalProduction DESC;"""

    analysis_df = pd.read_sql(query1, engine)

    analysis_df.to_csv(
        "Analysis/plant_production.csv",
        index=False)

    # good vs rejected prodction

    query2 = """SELECT
        SUM(f.ProductionQty) AS TotalProduction,
        SUM(f.GoodQty) AS GoodProduction,
        SUM(f.RejectedQty) AS RejectedProduction
    FROM fact_production f;"""   

    analysis_df = pd.read_sql(query2, engine)

    analysis_df.to_csv(
        "Analysis/good_vs_rejected_prod.csv",
        index=False)

    #production by machine
    query3 = """SELECT
        m.Machine,
        SUM(f.ProductionQty) AS TotalProduction
    FROM fact_production f
    JOIN dim_machine m
        ON f.MachineID = m.MachineID
    GROUP BY m.Machine
    ORDER BY TotalProduction DESC;"""

    analysis_df = pd.read_sql(query3, engine)
    analysis_df.to_csv(
        "Analysis/machine_prod.csv",
        index=False)

    #production by product 

    query4 = """SELECT
        p.Product,
        SUM(f.ProductionQty) AS TotalProduction
    FROM fact_production f
    JOIN dim_product p
        ON f.ProductID = p.ProductID
    GROUP BY p.Product
    ORDER BY TotalProduction DESC"""
    analysis_df = pd.read_sql(query4, engine)
    analysis_df.to_csv(
        "Analysis/production_by_prod.csv",
        index=False)


    #production by operator

    query5 = """SELECT
        o.Operator,
        SUM(f.ProductionQty) AS TotalProduction
    FROM fact_production f
    JOIN dim_operator o
        ON f.OperatorID = o.OperatorID
    GROUP BY o.Operator
    ORDER BY TotalProduction DESC;""" 

    analysis_df = pd.read_sql(query5, engine)
    analysis_df.to_csv(
        "Analysis/operator_production.csv",
        index=False)

    logger.info(
        "All SQL analysis queries completed"
    )

def main():
    dfs = load_data()

    if not dfs:
            logger.error(
                "Pipeline stopped: no input files found"
            )
            return

    raw_df = clean_data(dfs)

    dimensions = create_dimensions(raw_df)

    fact_production = create_fact_table(raw_df, dimensions)

    save_dimensions(dimensions)

    engine = create_database()

    load_to_mysql(dimensions, fact_production, engine)

    create_relationships(engine)

    run_analysis(engine)

    logger.info(
            "PIPELINE COMPLETED SUCCESSFULLY"
        )

    print("Pipeline completed successfully!")


if __name__ == "__main__":
    main()





