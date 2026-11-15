# DEV PC (ghjv84) — run in Admin PowerShell when using Ethernet cable to Deploy (10.10.10.x)
$ErrorActionPreference = "Stop"
# Firewall rules need Admin; link + IP work without elevation.
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

$deployIp = "10.10.10.2"
$sshExe = "$env:Windir\System32\OpenSSH\ssh.exe"
try {
    foreach ($port in 22, 2223) {
        $name = "SSH-Dev-To-Deploy-$port"
        if (-not (Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -Name $name -DisplayName "SSH dev to Deploy TCP $port" `
                -Enabled True -Direction Outbound -Action Allow -Protocol TCP `
                -RemoteAddress $deployIp -RemotePort $port -Profile Private | Out-Null
        }
    }
    if (-not (Get-NetFirewallRule -Name "SSH-Dev-OpenSSH-exe" -ErrorAction SilentlyContinue)) {
        New-NetFirewallRule -Name "SSH-Dev-OpenSSH-exe" -DisplayName "OpenSSH ssh.exe outbound" `
            -Enabled True -Direction Outbound -Action Allow -Program $sshExe -Profile Private | Out-Null
    }
    if (-not (Get-NetFirewallRule -Name "SSH-Deploy-Inbound-Ethernet" -ErrorAction SilentlyContinue)) {
        New-NetFirewallRule -Name "SSH-Deploy-Inbound-Ethernet" -DisplayName "Deploy 10.10.10.2 inbound" `
            -Enabled True -Direction Inbound -Action Allow -Protocol TCP `
            -RemoteAddress $deployIp -Profile Private | Out-Null
    }
    Write-Host "Firewall rules OK."
} catch {
    Write-Host "Firewall rules skipped (run this script as Administrator):" $_.Exception.Message -ForegroundColor Yellow
}

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