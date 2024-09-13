import pyodbc
import pandas as pd

connection_string = (
    "Driver={SQL Server};"
    "Server=pbg1sql02s324.qa.fs;"
    "Database=CM_QA3;"
    "Trusted_Connection=yes;"
)

query = """
SELECT
      ISNULL(lower(sys.AD_Site_Name0),'NA') AS site
      ,ISNULL(sys.Active0,'0') AS active
      ,ISNULL(sys.BuildExt,'NA') AS build
      ,ISNULL(sys.Client0,'0') AS client
      ,ISNULL(sys.Client_Version0,'NA') AS client_version
      ,ISNULL(sys.Creation_Date0,'1971-01-01 00:00:00') AS creation_date
      ,ISNULL(lower(sys.Full_Domain_Name0),'NA') AS domain
      ,ISNULL(sys.Last_Logon_Timestamp0,'1971-01-01 00:00:00') AS last_logon
      ,ISNULL(lower(sys.Name0),'NA') AS name
      ,ISNULL(lower(sys.Netbios_Name0),'NA') AS netbios_name
      ,ISNULL(sys.Obsolete0,'0') AS obsolete
      ,ISNULL(lower(sys.Distinguished_Name0),'NA') AS dn
        ,ISNULL(lower(os.caption0),'NA') AS operating_system
        ,ISNULL(lower(csys.model0),'NA') AS model
        ,ISNULL(lower(csys.Manufacturer0),'NA') AS manufacturer
  FROM "CM_QA3"."dbo"."v_R_System" sys
  LEFT JOIN "CM_QA3"."dbo"."v_GS_OPERATING_SYSTEM" os ON sys.resourceid = os.resourceid
  LEFT JOIN "CM_QA3"."dbo"."v_GS_COMPUTER_SYSTEM" csys ON sys.resourceid = csys.resourceid
"""

with pyodbc.connect(connection_string) as conn:
    df = pd.read_sql_query(query, conn)

# Export to CSV
df.to_csv('QA.fsSCCM.csv', index=False)
print("Data exported to sccm_inventory.csv")