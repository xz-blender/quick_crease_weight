$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root = $PSScriptRoot
$files = @('__init__.py', 'hud.py', 'keymaps.py', 'mesh_data.py', 'operators.py', 'preferences.py', 'translation.py', 'blender_manifest.toml', 'LICENSE')
$manifest = Get-Content -LiteralPath (Join-Path $root 'blender_manifest.toml') -Raw
if ($manifest -notmatch '(?m)^version = "(\d+\.\d+\.\d+)"\s*$') { throw 'Invalid manifest version' }
$version = $Matches[1]
$init = Get-Content -LiteralPath (Join-Path $root '__init__.py') -Raw
if ($init -notmatch '"version":\s*\((\d+),\s*(\d+),\s*(\d+)\)') { throw 'Invalid bl_info version' }
if ("$($Matches[1]).$($Matches[2]).$($Matches[3])" -ne $version) { throw 'Version mismatch' }
foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $file) -PathType Leaf)) { throw "Missing package file: $file" }
}
$dist = Join-Path $root 'dist'
$downloads = Join-Path $root 'downloads'
New-Item -ItemType Directory -Path $dist, $downloads -Force | Out-Null
$name = "quick_crease_weight-$version.zip"
$target = Join-Path $dist $name
$temporary = Join-Path $dist ([guid]::NewGuid().ToString() + '.zip')
try {
    $zip = [System.IO.Compression.ZipFile]::Open($temporary, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($file in $files) {
            $entry = $zip.CreateEntry($file, [System.IO.Compression.CompressionLevel]::Optimal)
            $entry.LastWriteTime = [DateTimeOffset]::new(2020, 1, 1, 0, 0, 0, [TimeSpan]::Zero)
            $source = [System.IO.File]::OpenRead((Join-Path $root $file))
            try {
                $output = $entry.Open()
                try { $source.CopyTo($output) } finally { $output.Dispose() }
            } finally { $source.Dispose() }
        }
    } finally { $zip.Dispose() }
    Move-Item -LiteralPath $temporary -Destination $target -Force
    Copy-Item -LiteralPath $target -Destination (Join-Path $downloads $name) -Force
    Write-Host "Built $target ($($files.Count) files)"
    Write-Host "Published local copy: $(Join-Path $downloads $name)"
} finally {
    if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
}
