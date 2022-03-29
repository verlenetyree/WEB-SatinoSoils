import pyodbc
import os
import sys
import win32com.client
import logging
from pathlib import Path
import numpy as np
import pandas as pd
# from string import Template
# import sqlalchemy
from pyproj import Proj
# from pyproj import _datadir, datadir
from datetime import datetime
import time

from progress.bar import ChargingBar

from config import PG_UID, PG_PWD

start_time = datetime.now()

#logging.basicConfig(
#    format='%(levelname)s: %(message)s',
#    level=logging.INFO)


print("Python version: " + sys.version.replace("\n", ""))
print(os.path.dirname(sys.executable))

myDataSources = pyodbc.dataSources()

print(myDataSources)

conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\grita\Documents\important\MSU\SOIL_SATINO\soil_database.mdb;')
filepath = r'C:\Users\grita\Documents\important\MSU\SOIL_SATINO\soil_database.mdb'

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

a = win32com.client.Dispatch("Access.Application")
a.OpenCurrentDatabase(filepath)

# # # # # #
# EDITING TABLE
# # # # # #

try:
	cursor.execute('ALTER TABLE dat_Profiles ADD Lon number, Lat number')
except:
	logging.warning("Colunms 'Lon' and 'Lat' are already exist.\n")

conn.commit()

#---------
#sql = "select ProfileId, ProfileY, ProfileX from dat_Profiles where (ProfileId < 343) and (ProfileId > 343)"
#cursor.execute(sql)
#data = cursor.fetchall()
#print(data)
#df = pd.DataFrame(data)
#print(df)
#---------

#df = pd.read_sql('dat_Profiles', conn)
df1 = pd.read_sql('select ProfileId, ProfileY, ProfileX from dat_Profiles where ProfileId < 343', conn)
df2 = pd.read_sql('select ProfileId, ProfileY, ProfileX from dat_Profiles', conn)
df = pd.concat([df1, df2])
print(df.head(20))

# affine parametrs
an = [6.067276e+06, 9.996311e-01, 6.214654e-04]
bn = [2.980103e+05, -7.045716e-04, 1.000017e+00]

x = an[0] + an[1] * df["ProfileY"] + an[2] * df["ProfileX"]
y = bn[0] + bn[1] * df["ProfileY"] + bn[2] * df["ProfileX"]

# UTM 37N -> WGS-84
ReProj = Proj("+proj=utm +zone=37N, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
lon, lat = ReProj(y.values, x.values, inverse=True)
dfWGS = pd.DataFrame(np.c_[lon, lat], columns=["Lon", "Lat"])
dfWGS.replace(np.inf, np.NaN, inplace=True)

print(dfWGS.head(20))

# Update columns values
for index, row in dfWGS.iterrows():
	with conn.cursor() as crsr:
		if pd.isna(row["Lon"]):
			continue
		crsr.execute("UPDATE dat_Profiles SET Lon = ?, Lat = ? WHERE ProfileId = ?", round(row["Lon"], 7), round(row["Lat"], 7), index + 1)

conn.commit()

# # # # # #
# EXPORT ALL TABLES TO POSTGRESQL
# # # # # #


postgres_conn_str = ("DRIVER={PostgreSQL Unicode};""DATABASE=soil_database;"f"UID={PG_UID};"f"PWD={PG_PWD};""SERVER=localhost;""PORT=5432;")
postgres_conn = pyodbc.connect(postgres_conn_str)
postgres_cursor = postgres_conn.cursor()

table_list = []

for table_info in cursor.tables(tableType='TABLE'):
	table_list.append(table_info.table_name)

acExport = 1
acTable = 0
db_name = Path(filepath).stem.lower()

bar = ChargingBar('Exporting tables', max=len(table_list))
for table in table_list:
	logging.info(f"Exporting: {table}")
	postgres_cursor.execute(f'DROP TABLE IF EXISTS public."{table}"')
	postgres_conn.commit()
	a.DoCmd.TransferDatabase(acExport, "ODBC Database", "ODBC;DRIVER={PostgreSQL Unicode};"f"DATABASE=soil_database;"f"UID=postgres;"f"PWD=Magrit;""SERVER=localhost;"f"PORT=5432;", acTable, f"{table}", f"{table}")
	logging.info(f"Finished Export of Table: {table}")
	bar.next()
bar.finish()
print(datetime.now() - start_time)

