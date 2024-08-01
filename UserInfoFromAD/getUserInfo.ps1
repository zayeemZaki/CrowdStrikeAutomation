# need to install :
# Install-Module -Name ImportExcel -Scope CurrentUser


Import-Module ActiveDirectory
Import-Module ImportExcel

# Function to get the manager's display name
function Get-ManagerName {
   param (
       [string]$ManagerDN
   )
   if ($ManagerDN) {
       $manager = Get-ADUser -Identity $ManagerDN -Properties DisplayName
       return $manager.DisplayName
   }
   return ""
}

# Read the list of users from the existing Excel sheet
$excelFilePath = "C:\Users\FS142999\Documents\LocalAdmins.xlsx"
$sheetName = "DomainAccounts"
$userList = Import-Excel -Path $excelFilePath -WorksheetName $sheetName

$properties = @("DisplayName", "Title", "Department", "Manager")

$userDetails = @()

foreach ($user in $userList) {
   $username = $user.'AccountName' 
   $adUser = Get-ADUser -Identity $username -Properties $properties
   if ($adUser) {
       $managerName = Get-ManagerName -ManagerDN $adUser.Manager
       $userDetails += [PSCustomObject]@{
           'DeviceName' = $user.DeviceName
           'AccountDomain' = $user.'AccountDomain'
           'AccountName' = $user.'AccountName'
           'LogonCount' = $user.'LogonCount'
           DisplayName = $adUser.DisplayName
           Title       = $adUser.Title
           Department  = $adUser.Department
           Manager     = $managerName
       }
   } 
   else {
       $userDetails += [PSCustomObject]@{
           'DeviceName' = $user.DeviceName
           'AccountDomain' = $user.'AccountDomain'
           'AccountName' = $user.'AccountName'
           'LogonCount' = $user.'LogonCount'
           DisplayName = ""
           Title       = ""
           Department  = ""
           Manager     = ""
       }
   }
}

$newExcelPath = "C:\Users\FS142999\Documents\LocalAdmins - Copy.xlsx" # new Excel file path
$userDetails | Export-Excel -Path $newExcelPath -WorksheetName $sheetName -ClearSheet

# Display the results
$userDetails