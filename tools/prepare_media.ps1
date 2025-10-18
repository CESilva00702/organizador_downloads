param(
    [Parameter(Mandatory=$true)] [string]$AutounattendPath,
    [Parameter(Mandatory=$true)] [string]$EncryptedPasswordFile
)

if (-not (Test-Path $AutounattendPath)) {
    Write-Error "Autounattend file not found: $AutounattendPath"
    exit 1
}
if (-not (Test-Path $EncryptedPasswordFile)) {
    Write-Error "Encrypted password file not found: $EncryptedPasswordFile"
    exit 2
}

Write-Host "Backing up $AutounattendPath to $AutounattendPath.bak"
Copy-Item -Path $AutounattendPath -Destination ($AutounattendPath + '.bak') -Force

$b64 = Get-Content -Path $EncryptedPasswordFile -Raw
try {
    $bytes = [Convert]::FromBase64String($b64)
    $plain = [System.Security.Cryptography.ProtectedData]::Unprotect($bytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
    $password = [System.Text.Encoding]::UTF8.GetString($plain)
} catch {
    Write-Error "Failed to decrypt password blob: $_"
    exit 3
}

Write-Host "Injecting password into $AutounattendPath (local machine only)"
$xml = [xml](Get-Content $AutounattendPath)

# Find first Password/Value element and set inner text
$node = $xml.SelectSingleNode('//Password/Value')
if ($null -eq $node) {
    Write-Error 'Could not find //Password/Value node in Autounattend file.'
    exit 4
}
$node.InnerText = $password

$xml.Save($AutounattendPath)
Write-Host "Password injected successfully. Backup at $AutounattendPath.bak"
