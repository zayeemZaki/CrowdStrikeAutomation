import pandas as pd

csv_file1 = 'FS.LocalSCCM.csv'
csv_file2 = 'QA.fsSCCM.csv'

df1 = pd.read_csv(csv_file1)
df2 = pd.read_csv(csv_file2)

combined_df = pd.concat([df1, df2], ignore_index=False)
output_file = 'inventory_sccm.xlsx'

combined_df.to_excel(output_file, sheet_name='Sheet1', index=False)

print(f'Data successfully written to {output_file}')
