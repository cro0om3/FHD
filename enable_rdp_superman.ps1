# PowerShell script to enable RDP and create a new user automatically
# Run this script as Administrator

# Enable RDP
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 0

# Enable NLA
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'UserAuthentication' -Value 1

# Open port 3389 in the firewall
if (-not (Get-NetFirewallRule -DisplayName 'Remote Desktop - User Mode (TCP-In)' -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName 'Remote Desktop - User Mode (TCP-In)' -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow
}



# Delete user if exists
$Username = 'FHD'
if (Get-LocalUser -Name $Username -ErrorAction SilentlyContinue) {
    net user $Username /delete
}
# Set password
$Password = '123456789'
# Create user with password
net user $Username $Password /add
Add-LocalGroupMember -Group 'Remote Desktop Users' -Member $Username

# Security info
Write-Host 'User FHD was created with password 123456789.'

# Print connection info
Write-Host '--- Connection Info ---'
Write-Host "Username: $Username"
Write-Host "Password: $Password"
Write-Host 'Internal IP:'
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' -and $_.IPAddress -notlike '169.*' }).IPAddress
Write-Host 'External IP:'
try { (Invoke-RestMethod -Uri 'https://api.ipify.org') } catch { Write-Host 'Could not fetch external IP' }
