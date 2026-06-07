# 一键推送到 GitHub 并打开 Streamlit 部署页（最小权限 public_repo）
# 用法：.\scripts\push_and_deploy.ps1

$ErrorActionPreference = "Stop"
$RepoOwner = "hukisgod-sheng"
$RepoName = "LotteryApp"
$Branch = "main"
$MainFile = "app.py"

Set-Location $PSScriptRoot\..

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  双色球沙盘 - 云端部署助手" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. GitHub CLI 登录（仅 public_repo，无法访问私有飞控仓库）
try {
    gh auth status 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "not logged in" }
} catch {
    Write-Host "[1/3] GitHub CLI 登录（权限: public_repo，仅公开仓库）..." -ForegroundColor Yellow
    gh auth login --hostname github.com --git-protocol https --web --scopes public_repo
    if ($LASTEXITCODE -ne 0) { throw "GitHub 登录失败" }
}
Write-Host "[OK] GitHub CLI 已就绪" -ForegroundColor Green

# 2. 创建独立公开仓库并推送（与飞控仓库无关）
$fullRepo = "$RepoOwner/$RepoName"
$repoExists = $false
try {
    gh repo view $fullRepo 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $repoExists = $true }
} catch {}

if (-not $repoExists) {
    Write-Host "[2/3] 创建公开仓库 $fullRepo 并推送..." -ForegroundColor Yellow
    gh repo create $RepoName --public --source=. --remote=origin --push `
        --description "炸裂双色球数据沙盘 - 娱乐学习用 Streamlit 应用"
    if ($LASTEXITCODE -ne 0) { throw "创建或推送失败" }
} else {
    Write-Host "[2/3] 推送到已有仓库 $fullRepo ..." -ForegroundColor Yellow
    $remote = git remote get-url origin 2>$null
    if (-not $remote) {
        git remote add origin "https://github.com/$fullRepo.git"
    }
    git push -u origin $Branch
    if ($LASTEXITCODE -ne 0) { throw "推送失败" }
}
Write-Host "[OK] 代码已在 GitHub" -ForegroundColor Green

# 3. 打开 Streamlit 预填部署页（你已授权 Streamlit，点 Deploy 即可）
$deployUrl = "https://share.streamlit.io/deploy?repository=$fullRepo&branch=$Branch&mainModule=$MainFile&subdomain=lottery-app"
Write-Host "[3/3] 打开 Streamlit 部署页..." -ForegroundColor Yellow
Write-Host "  $deployUrl" -ForegroundColor Gray
Start-Process $deployUrl

Write-Host ""
Write-Host "请在浏览器点击 Deploy 完成部署。" -ForegroundColor Green
Write-Host "Streamlit 授权建议：仅选定仓库 → $RepoName，勿开放全部私有仓库。" -ForegroundColor Yellow
