"""
DB bootstrap: creates a single pyodbc connection factory.
We derive a pyodbc-friendly string from the provided Somee connection info.
"""
import pyodbc

# Original (as provided):
SOMEE_CONN = (
    "workstation id=SmartMarket.mssql.somee.com;packet size=4096;"
    "user id=yossijosko_SQLLogin_2;pwd=zy4y1j8day;data source=SmartMarket.mssql.somee.com;"
    "persist security info=False;initial catalog=SmartMarket;TrustServerCertificate=True"
)

# PyODBC-style DSN-less string (same credentials):
PYODBC_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SmartMarket.mssql.somee.com;"
    "DATABASE=SmartMarket;"
    "UID=yossijosko_SQLLogin_2;"
    "PWD=zy4y1j8day;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

def get_conn():
    """Open a new DB connection. Caller should close it (context manager recommended)."""
    return pyodbc.connect(PYODBC_CONN)
