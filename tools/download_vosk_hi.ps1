param(
    [string]$ModelDir = "models/vosk-hi",
    [string]$ModelName = "vosk-model-small-hi-0.22"
)

$ErrorActionPreference = "Stop"

$zipUrl = "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip"

$root = Resolve-Path -Path .
$targetDir = Join-Path $root $ModelDir
$zipPath = Join-Path $targetDir "$ModelName.zip"

if (!(Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir | Out-Null
}

Write-Host "Downloading $zipUrl"
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath

Write-Host "Extracting to $targetDir"
Expand-Archive -Path $zipPath -DestinationPath $targetDir -Force

# Normalize folder name to match config expectation
$extracted = Join-Path $targetDir $ModelName
if (!(Test-Path $extracted)) {
    $candidate = Get-ChildItem -Path $targetDir -Directory | Where-Object { $_.Name -like "$ModelName*" } | Select-Object -First 1
    if ($candidate) {
        Rename-Item -Path $candidate.FullName -NewName $ModelName
    }
}

Write-Host "Done. Model path: $ModelDir/$ModelName"
