# Run on DEV PC (ghjv84) in PowerShell: tests TCP banner and ssh to deploy.
param(
    [string]$HostName = "192.168.2.45",
    [int]$Port = 22
)

Write-Host "=== Dev -> Deploy connectivity ===" -ForegroundColor Cyan
Write-Host "Target: ${HostName}:${Port}"

$tnc = Test-NetConnection -ComputerName $HostName -Port $Port -WarningAction SilentlyContinue
Write-Host "TcpTestSucceeded:" $tnc.TcpTestSucceeded

Write-Host "`n--- Raw TCP read (SSH banner) ---"
try {
    $tcp = New-Object System.Net.Sockets.TcpClient($HostName, $Port)
    $tcp.ReceiveTimeout = 8000
    $stream = $tcp.GetStream()
    $buf = New-Object byte[] 512
    $n = $stream.Read($buf, 0, 512)
    $banner = [Text.Encoding]::ASCII.GetString($buf, 0, [Math]::Max(0, $n))
    if ($banner) {
        Write-Host "Banner:" $banner.Trim()
    } else {
        Write-Host "Banner: (empty - server closed before sending SSH line)"
    }
    $tcp.Close()
} catch {
    Write-Host "Banner read failed:" $_.Exception.Message -ForegroundColor Red
}

Write-Host "`n--- ssh deploy (verbose tail) ---"
Write-Host "Config: $env:USERPROFILE\.ssh\config"
Write-Host "Key:    $env:USERPROFILE\.ssh\id_ed25519_deploy"
if (Test-Path "$env:USERPROFILE\.ssh\id_ed25519_deploy.pub") {
    Write-Host "Pubkey:" (Get-Content "$env:USERPROFILE\.ssh\id_ed25519_deploy.pub" -Raw).Trim()
}

ssh -v -o ConnectTimeout=10 deploy 2>&1 | Select-Object -Last 20