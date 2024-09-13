import pyodbc
import pandas as pd

print("Available ODBC Drivers:", pyodbc.drivers())

connection_string = (
    "Driver={SQL Server};"
    "Server=edr1sql01s530;"
    "Database=CM_FS3;"
    "Trusted_Connection=yes;"
)

query = """
SELECT
    ISNULL(LOWER(sys.AD_Site_Name0),'NA') AS site,
    ISNULL(sys.Active0,'0') AS active,
    ISNULL(sys.BuildExt,'NA') AS build,
    ISNULL(sys.Client0,'0') AS client,
    ISNULL(sys.Client_Version0,'NA') AS client_version,
    ISNULL(sys.Creation_Date0,'1971-01-01 00:00:00') AS creation_date,
    ISNULL(LOWER(sys.Full_Domain_Name0),'NA') AS domain,
    ISNULL(sys.Last_Logon_Timestamp0,'1971-01-01 00:00:00') AS last_logon,
    ISNULL(LOWER(sys.Name0),'NA') AS name,
    ISNULL(LOWER(sys.Netbios_Name0),'NA') AS netbios_name,
    ISNULL(sys.Obsolete0,'0') AS obsolete,
    ISNULL(LOWER(sys.Distinguished_Name0),'NA') AS dn,
    ISNULL(LOWER(os.caption0),'NA') AS operating_system,
    ISNULL(LOWER(csys.model0),'NA') AS model,
    ISNULL(LOWER(csys.Manufacturer0),'NA') AS manufacturer
FROM CM_FS3.dbo.v_R_System sys
LEFT JOIN CM_FS3.dbo.v_GS_OPERATING_SYSTEM os ON sys.resourceid = os.resourceid
LEFT JOIN CM_FS3.dbo.v_GS_COMPUTER_SYSTEM csys ON sys.resourceid = csys.resourceid
"""

conn = pyodbc.connect(connection_string)
df = pd.read_sql(query, conn)
output_path = 'FS.LocalSCCM.csv'
df.to_csv(output_path, index=False)
conn.close()
print(f"Data exported to {output_path}")
