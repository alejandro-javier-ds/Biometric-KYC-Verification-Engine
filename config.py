import os
from urllib.parse import quote_plus

class Config:
    DB_SERVER = os.environ.get("DB_SERVER", r"(localdb)\MSSQLLocalDB")
    DB_NAME = os.environ.get("DB_NAME", "VisionSecurityDB")
    DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")

def get_pyodbc_string() -> str:
    return (
        f"DRIVER={{{Config.DB_DRIVER}}};"
        f"SERVER={Config.DB_SERVER};"
        f"DATABASE={Config.DB_NAME};"
        "Trusted_Connection=yes;"
    )

def get_sqlalchemy_string() -> str:
    raw_conn_str = get_pyodbc_string()
    encoded_params = quote_plus(raw_conn_str)
    return f"mssql+pyodbc:///?odbc_connect={encoded_params}"