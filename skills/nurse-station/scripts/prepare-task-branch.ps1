param(
  [Parameter(Mandatory = $true)] [string]$TaskId,
  [Parameter(Mandatory = $true)] [string]$RepoKey,
  [string]$Mode = "analysis",
  [string]$YamlPath
)

$ErrorActionPreference = "Stop"

$WorkspaceRoot = $PSScriptRoot
while ($WorkspaceRoot -and -not (Test-Path (Join-Path $WorkspaceRoot "work-system"))) {
    $WorkspaceRoot = Split-Path $WorkspaceRoot -Parent
}
if (-not $WorkspaceRoot) { $WorkspaceRoot = $PWD.Path }

if (-not $YamlPath) {
    $YamlPath = Join-Path $WorkspaceRoot "work-system\config\nurse-station-repo-routing.yaml"
}

if (-not (Test-Path $YamlPath)) {
    Write-Error "YAML not found: $YamlPath"
    exit 1
}

$yamlContent = Get-Content $YamlPath -Raw

if ($yamlContent -notmatch 'status:\s*ready') {
    Write-Error "YAML status is not ready. Aborting."
    exit 1
}

$autoPull = $true
$fetchFirst = $true
$branchPattern = 'feature/{taskId}'

if ($yamlContent -match 'auto_pull:\s*(true|false)')   { $autoPull = $Matches[1] -eq 'true' }
if ($yamlContent -match 'fetch_first:\s*(true|false)') { $fetchFirst = $Matches[1] -eq 'true' }
if ($yamlContent -match 'branch_pattern:\s*"?([^"\n\r]+)"?') {
    $branchPattern = $Matches[1].Trim()
}

$repoBlockPattern = "(?ms)^\s*$RepoKey:\s*`r?`n(?<block>(?:\s{{2,}}.*(?:`r?`n|$))+ )"
$repoPath = $null
$sourceBranch = $null
if ($yamlContent -match $repoBlockPattern) {
    $repoBlock = $Matches['block']
    if ($repoBlock -match 'path:\s*"?([^"\n\r]+)"?') {
        $repoPath = $Matches[1].Trim() -replace '\\\\', '\'
    }
    if ($repoBlock -match 'source_branch:\s*"?([^"\n\r]+)"?') {
        $sourceBranch = $Matches[1].Trim()
    }
}

if (-not $repoPath) {
    Write-Error "Could not find path for repo '$RepoKey' in YAML."
    exit 1
}
if (-not $sourceBranch) {
    Write-Error "Could not find source_branch for repo '$RepoKey' in YAML."
    exit 1
}
if (-not (Test-Path $repoPath)) {
    Write-Error "Repo path does not exist: $repoPath"
    exit 1
}

$branchName = $branchPattern -replace '\{taskId\}', $TaskId

Write-Output "=== nurse-station prepare-workspace ==="
Write-Output "TaskId       : $TaskId"
Write-Output "RepoKey      : $RepoKey"
Write-Output "RepoPath     : $repoPath"
Write-Output "SourceBranch : $sourceBranch"
Write-Output "FeatureBranch: $branchName"
Write-Output "Mode         : $Mode"
Write-Output ""

Push-Location $repoPath
try {
    if ($fetchFirst) {
        Write-Output ">> git fetch..."
        git fetch --all 2>&1 | ForEach-Object { Write-Output "   $_" }
    }

    Write-Output ">> git checkout $sourceBranch ..."
    git checkout $sourceBranch 2>&1 | ForEach-Object { Write-Output "   $_" }

    if ($autoPull) {
        Write-Output ">> git pull..."
        git pull 2>&1 | ForEach-Object { Write-Output "   $_" }
    }

    $baseCommit = (git rev-parse --short HEAD).Trim()
    Write-Output ">> Base commit: $baseCommit"

    $branchExists = $false
    git rev-parse --verify $branchName 1>$null 2>$null
    if ($LASTEXITCODE -eq 0) { $branchExists = $true }

    if ($branchExists) {
        Write-Output ">> git checkout $branchName ..."
        git checkout $branchName 2>&1 | ForEach-Object { Write-Output "   $_" }
    } else {
        Write-Output ">> git checkout -b $branchName ..."
        git checkout -b $branchName 2>&1 | ForEach-Object { Write-Output "   $_" }
    }

    $currentCommit = (git rev-parse --short HEAD).Trim()

    Write-Output ""
    Write-Output "=== Routing Summary ==="
    Write-Output "- TaskId         : $TaskId"
    Write-Output "- RepoKey        : $RepoKey"
    Write-Output "- RepoPath       : $repoPath"
    Write-Output "- SourceBranch   : $sourceBranch"
    Write-Output "- FeatureBranch  : $branchName"
    Write-Output "- BaseCommit     : $baseCommit"
    Write-Output "- CurrentCommit  : $currentCommit"
    Write-Output "- Mode           : $Mode"

} finally {
    Pop-Location
}

