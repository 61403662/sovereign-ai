# DEV PC only (ghjv84). Creates C:\Users\<you>\.ssh\config + key if missing.
$ErrorActionPreference = "Stop"
$ssh = Join-Path $env:USERPROFILE ".ssh"
$key = Join-Path $ssh "id_ed25519_deploy"
$cfg = Join-Path $ssh "config"
$deployIp = "192.168.2.45"
$deployUser = "bryan"

New-Item -ItemType Directory -Force -Path $ssh | Out-Null

if (-not (Test-Path $key)) {
    ssh-keygen -t ed25519 -f $key -N '""' -C "ghjv84-to-deploy"
}

$block = @"

Host deploy
  HostName $deployIp
  User $deployUser
  IdentityFile $key
  IdentitiesOnly yes
  KexAlgorithms curve25519-sha256,ecdh-sha2-nistp256,ecdh-sha2-nistp384,diffie-hellman-group14-sha256
  HostKeyAlgorithms ecdsa-sha2-nistp256,ssh-ed25519
"@

if (Test-Path $cfg) {
    $text = Get-Content $cfg -Raw
    if ($text -notmatch "(?m)^Host deploy\s*$") {
        Add-Content -Path $cfg -Value $block
    }
} else {
    Set-Content -Path $cfg -Value $block.TrimStart()
}

Write-Host "DEV SSH ready."
Write-Host "Pubkey (paste on Deploy authorized_keys):"
Get-Content "$key.pub"
Write-Host ""
Write-Host "Run: powershell -File .\scripts\dev-test-deploy-connection.ps1"