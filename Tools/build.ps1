# Rebuild the Unity side of the asset library (materials / prefabs / skyboxes / scene).
# Usage:  powershell -ExecutionPolicy Bypass -File Tools\build.ps1 [-Thumbnails]
param(
    [string]$Unity = "C:\Program Files\Unity\Hub\Editor\2022.3.57f1c2\Editor\Unity.exe",
    [switch]$Thumbnails
)
$ErrorActionPreference = "Stop"
$proj = Split-Path -Parent $PSScriptRoot
$project = Join-Path $proj "UnityProject_AssetLibrary"
if (-not (Test-Path $project)) { $project = Split-Path -Parent $proj }
$log = Join-Path $project "build.log"

& $Unity -batchmode -nographics -projectPath $project `
    -executeMethod AssetLibrary.EditorTools.AssetLibraryBuilder.BatchBuild -logFile $log
if ($LASTEXITCODE -ne 0) { throw "Unity build failed, see $log" }

if ($Thumbnails) {
    & $Unity -batchmode -projectPath $project `
        -executeMethod AssetLibrary.EditorTools.AssetLibraryBuilder.BatchThumbnails -logFile $log
}
Write-Host "Done. See $log"
