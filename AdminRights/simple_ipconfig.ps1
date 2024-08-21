# simple_ipconfig.ps1
Write-Output "IP Configuration:"
Get-NetIPConfiguration | Format-Table -Property InterfaceAlias, IPv4Address, IPv6Address, DefaultGateway
