import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

DRIVER_OPTIONS = [
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server", 
    "ODBC Driver 13 for SQL Server",
    "ODBC Driver 11 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server Native Client 10.0",
    "SQL Server"
]

def get_working_driver():
    import pyodbc
    available_drivers = pyodbc.drivers()
    for driver in DRIVER_OPTIONS:
        if driver in available_drivers:
            return driver
    return "ODBC Driver 18 for SQL Server"

PYODBC_CONN = (
    f"DRIVER={{{get_working_driver()}}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASS')};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

def get_conn():
    """Open a new DB connection. Caller should close it (context manager recommended)."""
    return pyodbc.connect(PYODBC_CONN)
