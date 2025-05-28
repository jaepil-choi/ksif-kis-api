# ---------------------------------------------------------------------------
# PowerShell script that updates or reads a value from a JSON file.
# By default, it targets C:\Users\[username]\AppData\Local\Programs\Cursor\resources\app\product.json,
# but you can override that via -File parameter.
#
# Usage examples:
#   .\fix-product-json.ps1
#   .\fix-product-json.ps1 -DryRun
#   .\fix-product-json.ps1 -JsonPath '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion'
#   .\fix-product-json.ps1 -JsonPath '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion' -NewValue '0.399.0'
# ---------------------------------------------------------------------------

param (
    [string]$File = "$env:LOCALAPPDATA\Programs\Cursor\resources\app\product.json",
    [switch]$DryRun,
    [string]$JsonPath,
    [string]$NewValue,
    [switch]$Help,
    [Parameter(Position = 0)]
    [string]$Command,
    [Parameter(Position = 1)]
    [string]$CommandArg
)

# Store script name for usage
$SCRIPT_NAME = $MyInvocation.MyCommand.Name

# Helper function for consistent logging
function Log-Message {
    param (
        [string]$status,
        [string]$message
    )
    Write-Host "[$status] $message"
}

function Show-Usage {
    $usage = @"
Usage: $SCRIPT_NAME [options] [command or json_path [args...]]

Options:
  -File <path>          Override the default JSON file location
                        (default: $env:LOCALAPPDATA\Programs\Cursor\resources\app\product.json)
  -DryRun               Show what would be changed, but do not actually write
  -Help                 Show this help message
  -JsonPath <path>      Specify JSON path to read or modify
  -NewValue <value>     New value to set at JsonPath

Commands:
  update_gallery [target_file]     Apply only the extensionsGallery updates.
                                   If target_file is provided, it overrides -File.

JSON Operations:
  -JsonPath <path>                  Get the value at the JSON path
  -JsonPath <path> -NewValue <val>  Update the value at the JSON path

If no arguments given, the script applies a predefined set of changes
to the default file (Cursor\resources\app\product.json).
These include gallery and extension version updates.

Examples:
  # Perform the default updates (gallery, extensions) on the standard file
  $SCRIPT_NAME

  # Dry-run only (no changes written)
  $SCRIPT_NAME -DryRun

  # Apply only gallery updates to the default file
  $SCRIPT_NAME update_gallery

  # Apply only gallery updates to a specific file
  $SCRIPT_NAME update_gallery "C:\Custom\Path\product.json"

  # Print the current value from the default file
  $SCRIPT_NAME -JsonPath '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion'

  # Update that same key in the default file
  $SCRIPT_NAME -JsonPath '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion' -NewValue '0.399.0'
"@
    Write-Host $usage
}

# Ensures the path starts with a leading dot if it doesn't already
function Ensure-LeadingDot {
    param ([string]$path)
    
    if ([string]::IsNullOrEmpty($path)) {
        return $path
    }
    elseif ($path.StartsWith(".")) {
        return $path
    }
    else {
        return ".$path"
    }
}

# Splits a JSON path into parts, respecting quoted property names
function Split-JsonPath {
    param (
        [string]$path
    )
    
    $path = $path.TrimStart('.')
    $result = New-Object System.Collections.ArrayList
    $currentPart = ""
    $inQuotes = $false
    
    for ($i = 0; $i -lt $path.Length; $i++) {
        $char = $path[$i]
        
        if ($char -eq '"' -and ($i -eq 0 -or $path[$i-1] -ne '\')) {
            $inQuotes = -not $inQuotes
            $currentPart += $char
        }
        elseif ($char -eq '.' -and -not $inQuotes) {
            if ($currentPart) {
                [void]$result.Add($currentPart)
                $currentPart = ""
            }
        }
        else {
            $currentPart += $char
        }
    }
    
    if ($currentPart) {
        [void]$result.Add($currentPart)
    }
    
    return $result.ToArray()
}

# Gets a value from a nested JSON object using a path like '.property.subproperty'
function Get-JsonValue {
    param (
        [object]$jsonObj,
        [string]$path
    )
    
    $pathParts = Split-JsonPath -path $path
    $current = $jsonObj
    
    foreach ($part in $pathParts) {
        # Handle quoted property names with dots or special characters
        if ($part -match '^"(.*)"$') {
            $part = $Matches[1]
        }
        
        if ($null -eq $current.$part) {
            return $null
        }
        $current = $current.$part
    }
    
    return $current
}

# Sets a value in a nested JSON object using a path like '.property.subproperty'
function Set-JsonValue {
    param (
        [object]$jsonObj,
        [string]$path,
        [string]$value
    )
    
    $pathParts = Split-JsonPath -path $path
    $current = $jsonObj
    $lastIndex = $pathParts.Count - 1
    
    for ($i = 0; $i -lt $lastIndex; $i++) {
        $part = $pathParts[$i]
        
        # Handle quoted property names with dots or special characters
        if ($part -match '^"(.*)"$') {
            $part = $Matches[1]
        }
        
        # Create intermediate objects if they don't exist
        if ($null -eq $current.$part) {
            $current | Add-Member -NotePropertyName $part -NotePropertyValue ([PSCustomObject]@{})
        }
        
        $current = $current.$part
    }
    
    $lastPart = $pathParts[$lastIndex]
    # Handle quoted property names with dots or special characters
    if ($lastPart -match '^"(.*)"$') {
        $lastPart = $Matches[1]
    }
    
    # Try to convert string value to appropriate type
    $typedValue = $value
    
    # Try to convert to number if possible
    if ($value -match '^\d+$') {
        $typedValue = [int]$value
    }
    elseif ($value -match '^\d+\.\d+$') {
        $typedValue = [double]$value
    }
    
    # Add or update the property
    if ($null -eq $current.$lastPart) {
        $current | Add-Member -NotePropertyName $lastPart -NotePropertyValue $typedValue
    }
    else {
        $current.$lastPart = $typedValue
    }
}

# Reads a JSON value from a file
function Read-JsonValue {
    param (
        [string]$file,
        [string]$rawPath
    )
    
    $pathToUse = Ensure-LeadingDot $rawPath
    
    try {
        $jsonContent = Get-Content -Path $file -Raw | ConvertFrom-Json
        $value = Get-JsonValue -jsonObj $jsonContent -path $pathToUse
        
        if ($null -eq $value) {
            Log-Message "NO_KEY" "${pathToUse}: key does not exist or cannot be retrieved."
            return
        }
        
        Log-Message "READ" "${pathToUse} => $value"
    }
    catch {
        Log-Message "ERROR" "Failed to read JSON value: $_"
    }
}

# Updates a JSON value in a file
function Update-JsonValue {
    param (
        [string]$file,
        [string]$rawPath,
        [string]$newValue
    )
    
    $pathToUse = Ensure-LeadingDot $rawPath
    
    try {
        $jsonContent = Get-Content -Path $file -Raw | ConvertFrom-Json
        $currentValue = Get-JsonValue -jsonObj $jsonContent -path $pathToUse
        $keyMissing = $null -eq $currentValue
        
        if ($currentValue -eq $newValue) {
            Log-Message "NO_CHANGE" "${pathToUse}: Already => $newValue"
            return
        }
        
        if ($DryRun) {
            if ($keyMissing) {
                Log-Message "WILL_CREATE" "${pathToUse}: Would create key and set to => $newValue"
            }
            else {
                Log-Message "WILL_UPDATE" "${pathToUse}: Would change from => $currentValue to => $newValue"
            }
            return
        }
        
        Set-JsonValue -jsonObj $jsonContent -path $pathToUse -value $newValue
        
        # Write the updated JSON back to the file
        $jsonContent | ConvertTo-Json -Depth 32 | Set-Content -Path $file
        
        if ($keyMissing) {
            Log-Message "CREATED" "${pathToUse}: Set to => $newValue"
        }
        else {
            Log-Message "UPDATED" "${pathToUse}: Changed from => $currentValue to => $newValue"
        }
    }
    catch {
        Log-Message "ERROR" "Failed to update JSON value: $_"
    }
}

# Apply updates related to extensionsGallery
function Apply-GalleryUpdates {
    param ([string]$targetFile)
    
    Log-Message "INFO" "Applying extensionsGallery updates to => $targetFile"
    
    # Switchover to MS VSCode Marketplace endpoints
    Update-JsonValue "$targetFile" ".extensionsGallery.serviceUrl" "https://marketplace.visualstudio.com/_apis/public/gallery"
    Update-JsonValue "$targetFile" ".extensionsGallery.itemUrl" "https://marketplace.visualstudio.com/items"
    Update-JsonValue "$targetFile" ".extensionsGallery.resourceUrlTemplate" "https://{publisher}.vscode-unpkg.net/{publisher}/{name}/{version}/{path}"
    Update-JsonValue "$targetFile" ".extensionsGallery.controlUrl" "https://main.vscode-cdn.net/extensions/marketplace.json"
    Update-JsonValue "$targetFile" ".extensionsGallery.nlsBaseUrl" "https://www.vscode-unpkg.net/_lp/"
    Update-JsonValue "$targetFile" ".extensionsGallery.publisherUrl" "https://marketplace.visualstudio.com/publishers"
}

# Apply updates related to extensionMaxVersions
function Apply-ExtensionVersionUpdates {
    param ([string]$targetFile)
    
    Log-Message "INFO" "Applying extensionMaxVersions updates to => $targetFile"
    
    # ms-python.python
    Update-JsonValue "$targetFile" '.extensionMaxVersions."ms-python.python".maxVersion' "2025.5.2025041801"
    
    # ms-python.debugpy
    Update-JsonValue "$targetFile" '.extensionMaxVersions."ms-python.debugpy".maxVersion' "2025.6.0"
    
    # ms-python.vscode-pylance
    Update-JsonValue "$targetFile" '.extensionMaxVersions."ms-python.vscode-pylance".maxVersion' "2025.4.100"
    
    # ms-vscode-remote.remote-containers
    Update-JsonValue "$targetFile" '.extensionMaxVersions."ms-vscode-remote.remote-containers".maxVersion' "0.399.0"
    
    # ms-toolsai.jupyter
    Update-JsonValue "$targetFile" '.extensionMaxVersions."ms-toolsai.jupyter".maxVersion' "2025.4.0"
    
    # anysphere.pyright
    Update-JsonValue "$targetFile" '.extensionMaxVersions."anysphere.pyright".maxVersion' "0.0.0-0"
    
    # codeium.windsurfPyright
    Update-JsonValue "$targetFile" '.extensionMaxVersions."codeium.windsurfPyright".maxVersion' "0.0.0-0"
}

# Apply all predefined updates (default behavior)
function Apply-PredefinedUpdates {
    Log-Message "INFO" "Using file => $File"
    Log-Message "INFO" "Applying all predefined updates..."
    
    Apply-GalleryUpdates $File
    Apply-ExtensionVersionUpdates $File
    
    Log-Message "INFO" "Successfully completed all updates."
}

# Main execution logic
if ($Help) {
    Show-Usage
    exit 0
}

# Check if the file exists
if (-not (Test-Path $File) -and -not $DryRun) {
    Log-Message "ERROR" "Target file does not exist: $File"
    exit 1
}

# Process command if specified
if ($Command) {
    switch ($Command) {
        "update_gallery" {
            $targetFile = if ($CommandArg) { $CommandArg } else { $File }
            Apply-GalleryUpdates $targetFile
            exit 0
        }
        default {
            # If not a known command, treat first positional arg as JsonPath
            $JsonPath = $Command
            if ($CommandArg) {
                $NewValue = $CommandArg
            }
        }
    }
}

# Handle JSON operations
if ($JsonPath) {
    if ($NewValue) {
        Update-JsonValue $File $JsonPath $NewValue
    }
    else {
        Read-JsonValue $File $JsonPath
    }
    exit 0
}

# If no specific command or JSON operation was requested, apply all predefined updates
Apply-PredefinedUpdates
exit 0