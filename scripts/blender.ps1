# Windows entry point: use Blender's bundled Python, no pip install required.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$blenderPath = $env:BLENDER_EXECUTABLE
if (-not $blenderPath -and (Test-Path -LiteralPath (Join-Path $projectRoot 'blender.local.json'))) {
    $blenderPath = (Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $projectRoot 'blender.local.json') | ConvertFrom-Json).blender_executable
}
if (-not $blenderPath) {
    $blenderCommand = Get-Command blender -ErrorAction SilentlyContinue
    if ($blenderCommand) { $blenderPath = $blenderCommand.Source }
}
if (-not $blenderPath) {
    $installRoots = @(
        (Join-Path $env:ProgramFiles 'Blender Foundation'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Blender Foundation')
    )
    $candidates = foreach ($installRoot in $installRoots) {
        if (Test-Path -LiteralPath $installRoot) {
            Get-ChildItem -LiteralPath $installRoot -Directory -Filter 'Blender*' | ForEach-Object {
                $candidate = Join-Path $_.FullName 'blender.exe'
                if (Test-Path -LiteralPath $candidate) { Get-Item -LiteralPath $candidate }
            }
        }
    }
    $latest = $candidates | Sort-Object { $_.VersionInfo.FileVersionRaw } -Descending | Select-Object -First 1
    if ($latest) { $blenderPath = $latest.FullName }
}
if (-not $blenderPath -or -not (Test-Path -LiteralPath $blenderPath -PathType Leaf)) {
    throw 'Blender not found. Set BLENDER_EXECUTABLE or blender.local.json (see README.md).'
}
$blenderPath = (Resolve-Path -LiteralPath $blenderPath).Path
$pythonCandidate = Get-ChildItem -LiteralPath (Split-Path -Parent $blenderPath) -Directory |
    ForEach-Object { Join-Path $_.FullName 'python\bin\python.exe' } |
    Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if (-not $pythonCandidate) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $pythonCandidate = $pythonCommand.Source }
}
if (-not $pythonCandidate) { throw 'Python 3.11+ is required; bundled Blender Python was not found.' }
$env:BLENDER_EXECUTABLE = $blenderPath
$env:PYTHONUTF8 = '1'
& $pythonCandidate (Join-Path $projectRoot 'bridge\client.py') @args
exit $LASTEXITCODE
