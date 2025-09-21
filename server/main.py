import pymssql
from fastapi import FastAPI
import time
import random

app = FastAPI()


# === פרטי החיבור שלך ===
# conn = pymssql.connect(
#     server="SmartMarket.mssql.somee.com",
#     user="yossijosko_SQLLogin_2",
#     password="zy4y1j8day",
#     database="SmartMarket",
#     as_dict=True  
# )

# cursor = conn.cursor()

def get_conn():
    return pymssql.connect(
        server="SmartMarket.mssql.somee.com",
        user="yossijosko_SQLLogin_2",
        password="zy4y1j8day",
        database="SmartMarket",
        as_dict=True
    )

@app.get("/")
def list_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT ProductID, ProductName, Price FROM ProductsSimple ORDER BY ProductID DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"count ksknsksksksksn" : len(rows), "products": rows}

@app.get("/touch")
def touch():
    conn = get_conn()
    cur = conn.cursor()
    name = f"Product_{int(time.time())}"
    price = round(random.uniform(1.0, 50.0), 2)
    cur.execute("INSERT INTO ProductsSimple (ProductName, Price) VALUES (%s, %s)", (name, price))
    conn.commit()
    cur.execute("SELECT ProductID, ProductName, Price FROM ProductsSimple WHERE ProductName=%s", (name,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return {"inserted": row}




# cursor.execute("DELETE FROM ProductsSimple WHERE ProductName LIKE 'Product_%'")
# conn.commit()
# # === CREATE (הוספה) ===

# cursor.execute(
#     "INSERT INTO ProductsSimple (ProductName, Price) VALUES (%s, %s)",
#     ("Apple", 3.5)
# )
# cursor.execute(
#     "INSERT INTO ProductsSimple (ProductName, Price) VALUES (%s, %s)",
#     ("Banana", 2.0)
# )

# conn.commit() 
# print("✅ Added Apple & Banana")

# # === READ (שליפה) ===
# print("\n== All Products ==")
# cursor.execute("SELECT ProductID, ProductName, Price FROM ProductsSimple")
# for row in cursor.fetchall():
#     print(row)

# # === UPDATE (עדכון) ===
# cursor.execute(
#     "UPDATE TOP (1) ProductsSimple SET Price=%s WHERE ProductName=%s",
#     (30.0, "Apple")
# )
# conn.commit()
# print("\n✅ Updated Apple price")

# # בדיקה
# cursor.execute("SELECT * FROM ProductsSimple WHERE ProductName=%s", ("Apple",))
# print(cursor.fetchone())

# # === DELETE (מחיקה) ===
# cursor.execute("DELETE FROM ProductsSimple WHERE ProductName=%s", ("Banana",))
# conn.commit()
# print("\n✅ Deleted Banana")

# # בדיקה
# cursor.execute("SELECT * FROM ProductsSimple")
# print("\n== After Delete ==")
# for row in cursor.fetchall():
#     print(row)

# # סגירה
# cursor.close()
# conn.close()
