# Run on Deploy (Admin). Avoid pre-auth hang / slow DNS on direct-link 10.10.10.x clients.
$ErrorActionPreference = "Stop"
$cfg = "C:\ProgramData\ssh\sshd_config"
if (-not (Test-Path $cfg)) { throw "Missing $cfg" }

$lines = Get-Content $cfg
$insert = @(
  "",
  "# --- sovereign-ai direct cable (global, must be above any Match block) ---",
  "UseDNS no",
  "GSSAPIAuthentication no"
)

# Append only if not already set globally (simple check)
$text = $lines -join "`n"
$matchIndex = [regex]::Match($text, "(?m)^Match\s").Index
if ($matchIndex -lt 0) { $matchIndex = $text.Length }

$globalPart = $text.Substring(0, $matchIndex)
if ($globalPart -notmatch "(?m)^UseDNS\s") { $text = $globalPart.TrimEnd() + "`n" + ($insert -join "`n") + "`n" + $text.Substring($matchIndex) }
elseif ($globalPart -notmatch "(?m)^GSSAPIAuthentication\s") {
  $text = $globalPart.TrimEnd() + "`nGSSAPIAuthentication no`n" + $text.Substring($matchIndex)
}

Set-Content -Path $cfg -Value $text -Encoding utf8
& C:\Windows\System32\OpenSSH\sshd.exe -t
Restart-Service sshd
Write-Host "sshd tuned. From dev: ssh deploy-direct hostname"