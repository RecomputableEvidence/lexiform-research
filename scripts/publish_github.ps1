# GitHub repository already exists. Use the verified no-force publisher for that repository.
param(
    [switch]$ConfirmPublic,
    [switch]$RightsReviewed
)
$ErrorActionPreference = 'Stop'
if (-not ($ConfirmPublic -and $RightsReviewed)) {
    throw 'Publication requires -ConfirmPublic -RightsReviewed. Inspect the release gates first.'
}
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $root
& py -3 .\tools\publish_existing_repo.py --publish --confirmed-rights
if ($LASTEXITCODE -ne 0) { throw 'Publisher stopped. Examine its error; do not claim publication.' }
