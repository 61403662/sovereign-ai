# DEV PC (ghjv84) — run in Admin PowerShell when using Ethernet cable to Deploy (10.10.10.x)
$ErrorActionPreference = "Stop"
$alias = "Ethernet"
$myIp = "10.10.10.1"
$prefix = 24

Write-Host "=== Direct link dev setup ===" -ForegroundColor Cyan

$ad = Get-NetAdapter -Name $alias -ErrorAction SilentlyContinue
if (-not $ad -or $ad.Status -ne "Up") {
    Write-Host "Adapter '$alias' not Up. Check cable. Get-NetAdapter for name."
    exit 1
}

Set-NetConnectionProfile -InterfaceAlias $alias -NetworkCategory Private
Enable-NetFirewallRule -DisplayGroup "OpenSSH Server" -ErrorAction SilentlyContinue | Out-Null

$have = Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias $alias -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -eq $myIp }
if (-not $have) {
    Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias $alias -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-NetIPAddress -Confirm:$false -InputObject $_ -ErrorAction SilentlyContinue }
    New-NetIPAddress -InterfaceAlias $alias -IPAddress $myIp -PrefixLength $prefix | Out-Null
    Write-Host "Set $alias to $myIp/$prefix"
} else {
    Write-Host "$alias already $myIp"
}

Write-Host "Profile:" (Get-NetConnectionProfile -InterfaceAlias $alias).NetworkCategory
Write-Host "Test: ping 10.10.10.2"
Write-Host "      ssh deploy-direct hostname"