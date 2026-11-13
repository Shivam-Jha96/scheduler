# scripts/setup_kanban_board.ps1
# Automates GitHub Projects v2 creation, Status configuration, and Backlog population

$owner = "Shivam-Jha96"
$repo = "Shivam-Jha96/scheduler"
$projectTitle = "Omnichannel Message Scheduler Kanban"

Write-Host "Creating GitHub Project v2: '$projectTitle' for owner '$owner'..."
$projectRaw = gh project create --owner $owner --title "$projectTitle" --format json
Write-Host "Raw output: $projectRaw"
$projectJson = $projectRaw | ConvertFrom-Json
$projectNumber = $projectJson.number
$projectId = $projectJson.id

Write-Host "Created Project Number: $projectNumber (ID: $projectId)"

# Link project to repository
Write-Host "Linking project #$projectNumber to repo $repo..."
gh project link $projectNumber --owner $owner --repo $repo

# Retrieve fields to find 'Status' field ID
Write-Host "Inspecting project fields..."
$fieldsRaw = gh project field-list $projectNumber --owner $owner --format json
$fieldsJson = $fieldsRaw | ConvertFrom-Json
$statusField = $fieldsJson.fields | Where-Object { $_.name -eq "Status" }
$statusFieldId = $statusField.id
Write-Host "Found Status Field ID: $statusFieldId"

# Configure 5-stage Kanban Status options via GraphQL mutation
Write-Host "Updating Status single-select options via GraphQL mutation..."
$mutation = @"
mutation {
  updateProjectV2Field(
    input: {
      fieldId: "$statusFieldId"
      singleSelectOptions: [
        { name: "Backlog", color: GRAY, description: "Backlog items awaiting grooming or scheduling" },
        { name: "Ready", color: BLUE, description: "Groomed and ready for development" },
        { name: "In Progress", color: YELLOW, description: "Actively in development" },
        { name: "In Review", color: PURPLE, description: "Under PR/code review" },
        { name: "Done", color: GREEN, description: "Completed and verified" }
      ]
    }
  ) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
        options {
          id
          name
        }
      }
    }
  }
}
"@

$mutationResult = gh api graphql -f query="$mutation"
Write-Host "Mutation Result: $mutationResult"

# Add all 12 Epic issues to Project and set Status to Backlog
$issueNumbers = @(1, 12, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)

Write-Host "Adding 12 Epic issues to Project #$projectNumber and setting Status to 'Backlog'..."
foreach ($num in $issueNumbers) {
    $issueUrl = "https://github.com/$repo/issues/$num"
    Write-Host "Adding issue #$num ($issueUrl)..."
    $itemRaw = gh project item-add $projectNumber --owner $owner --url "$issueUrl" --format json
    Write-Host "  -> Added. Setting Status to 'Backlog'..."
    gh project item-edit $projectNumber --owner $owner --url "$issueUrl" --field "Status" --value "Backlog"
    Write-Host "  -> Done."
}

# Verify items
Write-Host "Verifying all items on Project #$projectNumber..."
$itemsJson = gh project item-list $projectNumber --owner $owner --format json
$itemsJson | Out-File -FilePath "scripts/project_items_verification.json" -Encoding utf8
Write-Host "Board setup and population complete!"
Write-Host "Project URL: https://github.com/users/$owner/projects/$projectNumber"
