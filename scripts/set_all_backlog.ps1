# scripts/set_all_backlog.ps1
$issueNumbers = @(1, 12, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
$projectNumber = 2
$owner = "Shivam-Jha96"
$repo = "Shivam-Jha96/scheduler"

foreach ($num in $issueNumbers) {
    $url = "https://github.com/$repo/issues/$num"
    Write-Host "Setting Status to 'Backlog' for #$num ($url)..."
    gh project item-edit $projectNumber --owner $owner --url "$url" --field "Status" --value "Backlog"
}

Write-Host "All items set to Backlog!"
