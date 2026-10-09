param([string]$Message = '更新九域守界网站')
$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    python scripts/build.py
    if ($LASTEXITCODE -ne 0) { throw '网站生成失败，未上传。' }
    git add .
    if ($LASTEXITCODE -ne 0) { throw 'Git 添加文件失败。' }
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host '没有需要提交的内容。'
    } elseif ($LASTEXITCODE -eq 1) {
        git commit -m $Message
        if ($LASTEXITCODE -ne 0) { throw 'Git 提交失败。' }
    } else { throw 'Git 检查失败。' }
    git push
    if ($LASTEXITCODE -ne 0) { throw '上传失败，请检查 GitHub 登录和网络。' }
    Write-Host '已上传。GitHub Pages 完成发布后即可看到更新。'
} finally {
    Pop-Location
}
