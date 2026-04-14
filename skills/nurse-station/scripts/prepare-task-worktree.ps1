param(
  [Parameter(Mandatory = $true)] [string]$TaskId,
  [Parameter(Mandatory = $true)] [string]$RepoKey,
  [string]$Mode = "analysis",
  [string]$YamlPath
)

$ErrorActionPreference = "Stop"

# Resolve workspace root (walk up until we find work-system/)
$WorkspaceRoot = $PSScriptRoot
while ($WorkspaceRoot -and -not (Test-Path (Join-Path $WorkspaceRoot "work-system"))) {
    $WorkspaceRoot = Split-Path $WorkspaceRoot -Parent
}
if (-not $WorkspaceRoot) { $WorkspaceRoot = $PWD.Path }

if (-not $YamlPath) {
    $YamlPath = Join-Path $WorkspaceRoot "work-system\config\nurse-station-repo-routing.yaml"
}

# ── 1. Read YAML (lightweight text parsing, no YamlDotNet dependency) ──

if (-not (Test-Path $YamlPath)) {
    Write-Error "YAML not found: $YamlPath"
    exit 1
}

$yamlContent = Get-Content $YamlPath -Raw

# Check status
if ($yamlContent -notmatch 'status:\s*ready') {
    Write-Error "YAML status is not ready. Aborting."
    exit 1
}

# ── 2. Resolve configuration values ──

# Defaults
$autoPull     = $true
$fetchFirst   = $true
$useWorktree  = $true
$worktreeBase = Join-Path $WorkspaceRoot ".nurse-station-worktrees"
$branchPattern = 'feature/{taskId}'

# Override from git_defaults section
if ($yamlContent -match 'auto_pull:\s*(true|false)')        { $autoPull     = $Matches[1] -eq 'true' }
if ($yamlContent -match 'fetch_first:\s*(true|false)')      { $fetchFirst   = $Matches[1] -eq 'true' }
if ($yamlContent -match 'use_worktree:\s*(true|false)')     { $useWorktree  = $Matches[1] -eq 'true' }
if ($yamlContent -match "worktree_base_dir:\s*""?([^""\n\r]+)""?") {
    $worktreeBase = $Matches[1].Trim() -replace '\\\\', '\'
}
if ($yamlContent -match "branch_pattern:\s*""?([^""\n\r]+)""?") {
    $branchPattern = $Matches[1].Trim()
}

# Resolve source_branch for the target repo
$sourceBranch = $null
$repoPattern = "(?s)$RepoKey.*?source_branch:\s*""?([^""\n\r]+)""?"
if ($yamlContent -match $repoPattern) {
    $sourceBranch = $Matches[1].Trim()
}
if (-not $sourceBranch) {
    Write-Error "Could not find source_branch for repo '$RepoKey' in YAML."
    exit 1
}

# Resolve root path for the repo key
$rootPath = $null
$rootPattern = "${RepoKey}:\s*""?([^""\n\r]+)""?"
if ($yamlContent -match $rootPattern) {
    $rootPath = $Matches[1].Trim() -replace '\\\\', '\'
}
if (-not $rootPath) {
    Write-Error "Could not find root path for repo '$RepoKey' in YAML."
    exit 1
}
if (-not (Test-Path $rootPath)) {
    Write-Error "Repo root does not exist: $rootPath"
    exit 1
}

# Resolve branch name from pattern
$branchName = $branchPattern -replace '\{taskId\}', $TaskId

Write-Output "=== nurse-station prepare-task-worktree ==="
Write-Output "TaskId       : $TaskId"
Write-Output "RepoKey      : $RepoKey"
Write-Output "Root         : $rootPath"
Write-Output "SourceBranch : $sourceBranch"
Write-Output "BranchName   : $branchName"
Write-Output "Mode         : $Mode"
Write-Output ""

# ── 3. Sync source branch ──

Push-Location $rootPath
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

    $commit = (git rev-parse --short HEAD).Trim()
    Write-Output ">> Current commit: $commit"

    # ── 4. Worktree ──

    if ($useWorktree) {
        $wtPath = Join-Path $worktreeBase "$TaskId-$RepoKey"

        if (Test-Path $wtPath) {
            Write-Output ">> Worktree already exists: $wtPath"
            Write-Output "   Reusing existing worktree. Delete manually if you want a fresh one."
        } else {
            $null = New-Item -ItemType Directory -Path (Split-Path $wtPath -Parent) -Force -ErrorAction SilentlyContinue
            Write-Output ">> Creating worktree: $wtPath (branch: $branchName)"
            git worktree add $wtPath -b $branchName 2>&1 | ForEach-Object { Write-Output "   $_" }
        }
    } else {
        $wtPath = "(none - use_worktree is false)"
    }

    # ── 5. Output routing summary ──

    Write-Output ""
    Write-Output "=== Routing Summary ==="
    Write-Output "- TaskId        : $TaskId"
    Write-Output "- RepoKey       : $RepoKey"
    Write-Output "- ScanRoot      : $rootPath"
    Write-Output "- SourceBranch  : $sourceBranch"
    Write-Output "- Commit        : $commit"
    Write-Output "- Worktree      : $wtPath"
    Write-Output "- Mode          : $Mode"

} finally {
    Pop-Location
}
