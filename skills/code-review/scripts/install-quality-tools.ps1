# Installs crapper and dryer (optionally mutator) for the quality gates in
# references/quality-gates.md. Windows PowerShell 5.1+ / PowerShell 7.
# Usage: powershell -File install-quality-tools.ps1 [-WithMutator] [-Latest] [-Dir DIR]
# Default DIR: ~\.claude\tools\ub-mode. Do not move DIR after install (pip -e points to it).
# By default clones are pinned to the commits this skill was written against.
param([switch]$WithMutator, [switch]$Latest, [string]$Dir = (Join-Path $HOME ".claude\tools\ub-mode"))
$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git not found" }
# 'python3' on Windows is often the Microsoft Store stub; prefer 'python', then the 'py' launcher.
$py = $null
foreach ($c in @("python", "py")) {
  $cmd = Get-Command $c -ErrorAction SilentlyContinue
  if ($cmd -and $cmd.Source -notmatch "WindowsApps") { $py = $c; break }
}
if (-not $py) { throw "python 3.11+ not found (the WindowsApps stub does not count)" }
& $py -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"
if ($LASTEXITCODE -ne 0) { throw "$py is older than 3.11" }

function Install-One($name, $commit) {
  $path = Join-Path $Dir $name
  if (-not (Test-Path (Join-Path $path ".git"))) { git clone "https://github.com/unclebob/$name" $path; if ($LASTEXITCODE) { throw "clone $name failed" } }
  if (-not $Latest) { git -C $path fetch --quiet origin; git -C $path checkout --quiet $commit; if ($LASTEXITCODE) { throw "checkout $name failed" } }
  & $py -m pip install -e $path
  if ($LASTEXITCODE) { throw "pip install $name failed" }
}

New-Item -ItemType Directory -Force $Dir | Out-Null
Install-One "crapper" "c757ec79a6c15dc815238bbd9c2f4601eb54d3cc"
Install-One "dryer" "66ff6d21a42c04afcad89c78a80066176d1294b0"
# mutator reads function names from ..\crapper, so it must sit next to it (it does).
if ($WithMutator) { Install-One "mutator" "830ec7e9c39664d753f8699015bc796df67727b9" }

# crapper --help prints U+2212, which crashes a cp1252 console; force UTF-8 for the check.
$env:PYTHONUTF8 = "1"
& $py -m crapper --help | Out-Null; if ($LASTEXITCODE) { throw "crapper check failed" }
& $py -m dryer --help | Out-Null; if ($LASTEXITCODE) { throw "dryer check failed" }
Write-Host "OK: crapper and dryer installed for $py (clones in $Dir)"
Write-Host "Note: the first analysis downloads tree-sitter grammars from GitHub releases."
