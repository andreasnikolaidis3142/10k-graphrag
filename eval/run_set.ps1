# Runs a question set: for each question saves eval/<set>/qNN.json + qNN.md (ask_to_file.py) and qNN_context.txt (--no-llm evidence).
# usage: .\eval\run_set.ps1 -Graph eval/aapl_2023.json -Set apple -Questions eval/apple_questions.txt [-Only 1,4] [-Suffix _after]
param([string]$Graph, [string]$Set, [string]$Questions, [int[]]$Only = @(), [string]$Suffix = "")
$py = (Resolve-Path ".\.venv\Scripts\python.exe").Path
$env:PYTHONIOENCODING = "utf-8"
$qs = Get-Content $Questions -Encoding utf8 | Where-Object { $_.Trim() }
$first = $true
for ($i = 0; $i -lt $qs.Count; $i++) {
    $n = $i + 1
    if ($Only.Count -and -not ($Only -contains $n)) { continue }
    $base = "eval/$Set/q{0:D2}$Suffix" -f $n
    if (-not $first) { Start-Sleep -Seconds 20 }
    $first = $false
    & $py -m tenk_graphrag ask $Graph $qs[$i] --no-llm 2>$null | Out-File "$base`_context.txt" -Encoding utf8
    for ($try = 0; $try -le 2; $try++) {
        $out = & $py ask_to_file.py $Graph $qs[$i] $base 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0 -and (Test-Path "$base.json")) { break }
        Write-Output "q$n attempt $try failed: $(($out -split "`n" | Select-Object -Last 2) -join ' ')"
        Start-Sleep -Seconds 20
    }
    Write-Output ("q{0}: {1}" -f $n, (($out -split "`n" | Where-Object { $_ -match "^wrote" }) -join ""))
}
