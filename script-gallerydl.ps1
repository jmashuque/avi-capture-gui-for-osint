param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile,

    [Parameter(Mandatory = $true)]
    [string]$CaseName,

    [Parameter(Mandatory = $false)]
    [string]$OutputTemplate,

    [Parameter(Mandatory = $false)]
    [string]$CookiesFile,

    [Parameter(Mandatory = $false)]
    [string]$OutputRoot = ".\Investigations",

    [Parameter(Mandatory = $false)]
    [string]$GalleryDlPath = ".\gallery-dl.exe",

    [switch]$MetadataOnly,

    [switch]$WriteMetadata,

    [switch]$WriteInfoJson,

    [switch]$WriteTags,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Use", "Ignore", "Force")]
    [string]$ArchiveMode = "Use",

    [Parameter(Mandatory = $false)]
    [ValidateSet("Fast", "Normal", "Cautious")]
    [string]$RateLimit = "Normal",

    [Parameter(Mandatory = $false)]
    [ValidateRange(0, 1000000)]
    [int]$MaxItems = 0,

    [Parameter(Mandatory = $false)]
    [string]$ItemRange,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 100)]
    [int]$Retries = 4,

    [Parameter(Mandatory = $false)]
    [ValidateRange(10, 900)]
    [int]$Timeout = 30,

    [Parameter(Mandatory = $false)]
    [string]$ProxyUrl,

    [Parameter(Mandatory = $false)]
    [string]$UniversalArchiveFile
)

$ErrorActionPreference = "Stop"

if ($PSScriptRoot) {
    $ScriptRoot = $PSScriptRoot
}
else {
    $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$AppTempFolder = Join-Path $ScriptRoot "gui-temp"

function New-AppTempFile {
    param(
        [Parameter(Mandatory = $true)][string]$Prefix,
        [Parameter(Mandatory = $false)][string]$Suffix = ".tmp"
    )

    if (-not (Test-Path -LiteralPath $AppTempFolder -PathType Container)) {
        New-Item -ItemType Directory -Path $AppTempFolder -Force | Out-Null
    }

    $safePrefix = ($Prefix -replace '[^A-Za-z0-9_.-]', '-')
    $safeSuffix = if ([string]::IsNullOrWhiteSpace($Suffix)) { ".tmp" } else { $Suffix }

    for ($i = 0; $i -lt 50; $i++) {
        $candidate = Join-Path $AppTempFolder ("{0}{1}{2}" -f $safePrefix, ([guid]::NewGuid().ToString("N")), $safeSuffix)
        if (-not (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
    }

    throw "Could not create a unique app temp file name."
}

function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-Host "========== $Text =========="
}

function Resolve-ToolPath {
    param(
        [Parameter(Mandatory = $true)][string]$PathOrCommand,
        [Parameter(Mandatory = $true)][string]$ToolName
    )

    if ([string]::IsNullOrWhiteSpace($PathOrCommand)) {
        throw "$ToolName path is blank."
    }

    if (Test-Path -LiteralPath $PathOrCommand -PathType Leaf) {
        return (Resolve-Path -LiteralPath $PathOrCommand).Path
    }

    $cmd = Get-Command $PathOrCommand -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    throw "$ToolName was not found: $PathOrCommand"
}

function ConvertTo-NativeArgument {
    param([AllowNull()][string]$Argument)

    if ($null -eq $Argument) {
        return '""'
    }

    if ($Argument.Length -eq 0) {
        return '""'
    }

    if ($Argument -notmatch '[\s"]') {
        return $Argument
    }

    $Result = '"'
    $Backslashes = 0

    foreach ($Char in $Argument.ToCharArray()) {
        if ($Char -eq '\') {
            $Backslashes++
            continue
        }

        if ($Char -eq '"') {
            if ($Backslashes -gt 0) {
                $Result += ('\' * ($Backslashes * 2))
                $Backslashes = 0
            }
            $Result += '\"'
            continue
        }

        if ($Backslashes -gt 0) {
            $Result += ('\' * $Backslashes)
            $Backslashes = 0
        }
        $Result += $Char
    }

    if ($Backslashes -gt 0) {
        $Result += ('\' * ($Backslashes * 2))
    }

    $Result += '"'
    return $Result
}

function Join-NativeArguments {
    param([string[]]$Arguments)

    return (($Arguments | ForEach-Object { ConvertTo-NativeArgument $_ }) -join ' ')
}

function Invoke-GalleryDlSafely {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$RunLog
    )

    $StdOutFile = New-AppTempFile -Prefix "avi-gallerydl-stdout-" -Suffix ".log"
    $StdErrFile = New-AppTempFile -Prefix "avi-gallerydl-stderr-" -Suffix ".log"

    try {
        $Process = Start-Process -FilePath $FilePath -ArgumentList (Join-NativeArguments $Arguments) -RedirectStandardOutput $StdOutFile -RedirectStandardError $StdErrFile -NoNewWindow -Wait -PassThru

        foreach ($OutputFile in @($StdOutFile, $StdErrFile)) {
            if (Test-Path -LiteralPath $OutputFile -PathType Leaf) {
                Get-Content -LiteralPath $OutputFile -ErrorAction SilentlyContinue | ForEach-Object {
                    $Line = $_.ToString()
                    if ($Line.Length -gt 0) {
                        Write-Host $Line
                        Write-RunLogLineOnly $Line
                    }
                }
            }
        }

        if ($null -eq $Process.ExitCode) {
            return 1
        }

        return [int]$Process.ExitCode
    }
    finally {
        Remove-Item -LiteralPath $StdOutFile, $StdErrFile -Force -ErrorAction SilentlyContinue
    }
}

function New-SafeCaseName {
    param([string]$Name)
    return ($Name -replace '[\\/:*?"<>|]', '_').Trim()
}

function Test-RelativeOutputTemplate {
    param([Parameter(Mandatory = $true)][string]$Template)

    $clean = $Template.Trim().Replace('\', '/')

    if ([string]::IsNullOrWhiteSpace($clean)) {
        throw "OutputTemplate cannot be blank."
    }

    # Do not use [System.IO.Path]::IsPathRooted() here. yt-dlp/gallery-dl
    # output templates can contain native placeholder syntax such as
    # %(uploader|unknown)s, and .NET path validation treats the pipe as an
    # illegal literal path character before the capture tool has a chance to
    # resolve it. Only block clear absolute-path forms after normalizing
    # backslashes to forward slashes.
    if ($clean -match '^[A-Za-z]:' -or $clean.StartsWith('/')) {
        throw "OutputTemplate must be relative to the case media folder, not an absolute path."
    }

    if ($clean -notmatch '\{extension\}' -and $clean -notmatch '%extension%' -and $clean -notmatch '%ext%') {
        $clean = "$clean.{extension}"
    }

    foreach ($part in ($clean -split '/')) {
        if ([string]::IsNullOrWhiteSpace($part)) {
            throw "OutputTemplate cannot contain empty path segments."
        }
        if ($part -eq '..') {
            throw "OutputTemplate cannot contain '..' path traversal."
        }
    }

    return $clean
}

function Get-Sha256HashCompat {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (Get-Command Get-FileHash -ErrorAction SilentlyContinue) {
        return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    }

    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha.ComputeHash($stream)
            return ([BitConverter]::ToString($hashBytes) -replace '-', '').ToUpperInvariant()
        }
        finally {
            $sha.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

function New-DirectoryIfMissing {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

if (-not (Test-Path -LiteralPath $InputFile -PathType Leaf)) {
    throw "InputFile was not found: $InputFile"
}

$GalleryDlPath = Resolve-ToolPath -PathOrCommand $GalleryDlPath -ToolName "gallery-dl"
$SafeCaseName = New-SafeCaseName -Name $CaseName
if ([string]::IsNullOrWhiteSpace($SafeCaseName)) {
    throw "CaseName is blank after sanitizing."
}

if ([string]::IsNullOrWhiteSpace($OutputTemplate)) {
    $OutputTemplate = "{category}/{subcategory}/{id}_{filename}.{extension}"
}
$OutputTemplate = Test-RelativeOutputTemplate -Template $OutputTemplate

$OutputRootFull = [System.IO.Path]::GetFullPath($OutputRoot)
$CaseFolder = Join-Path $OutputRootFull $SafeCaseName
$MediaFolder = Join-Path $CaseFolder "media"
$LogsFolder = Join-Path $CaseFolder "logs"
$ManifestsFolder = Join-Path $CaseFolder "manifests"

New-DirectoryIfMissing -Path $OutputRootFull
New-DirectoryIfMissing -Path $CaseFolder
New-DirectoryIfMissing -Path $MediaFolder
New-DirectoryIfMissing -Path $LogsFolder
New-DirectoryIfMissing -Path $ManifestsFolder

$RunStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunLog = Join-Path $LogsFolder "gallery-dl-run_$RunStamp.log"
$ArchiveFile = Join-Path $ManifestsFolder "gallery-dl-archive.sqlite3"
$ArchiveFileUsed = $ArchiveFile
if ($ArchiveMode -eq "Use" -and -not [string]::IsNullOrWhiteSpace($UniversalArchiveFile)) {
    $UniversalArchiveParent = Split-Path -Parent $UniversalArchiveFile
    if (-not [string]::IsNullOrWhiteSpace($UniversalArchiveParent)) {
        New-DirectoryIfMissing -Path $UniversalArchiveParent
    }
    $ArchiveFileUsed = [System.IO.Path]::GetFullPath($UniversalArchiveFile)
}
$UnsupportedFile = Join-Path $LogsFolder "gallery-dl-unsupported_$RunStamp.txt"
$ManifestFile = Join-Path $ManifestsFolder "gallery-dl-sha256-manifest_$RunStamp.csv"
$CapturedUrlsFile = Join-Path $OutputRootFull "gui-captured-urls.txt"
$FailedUrlsFile = Join-Path $OutputRootFull "gui-failed-urls.txt"
$script:RunLogWriter = $null

function Initialize-RunLogWriter {
    if ($null -ne $script:RunLogWriter) {
        return
    }

    $encoding = New-Object System.Text.UTF8Encoding($false)
    $script:RunLogWriter = New-Object System.IO.StreamWriter($RunLog, $true, $encoding)
}

function Write-RunLogLineOnly {
    param([AllowNull()][string]$Message)

    if ($null -eq $script:RunLogWriter) {
        Initialize-RunLogWriter
    }

    if ($null -ne $script:RunLogWriter) {
        $script:RunLogWriter.WriteLine([string]$Message)
    }
    else {
        Add-Content -LiteralPath $RunLog -Value $Message -Encoding UTF8
    }
}

function Close-RunLogWriter {
    if ($null -ne $script:RunLogWriter) {
        try {
            $script:RunLogWriter.Flush()
        }
        finally {
            $script:RunLogWriter.Dispose()
            $script:RunLogWriter = $null
        }
    }
}

Initialize-RunLogWriter

function Write-RunLog {
    param([string]$Message)
    Write-Host $Message
    Write-RunLogLineOnly $Message
}

$UrlList = New-Object System.Collections.Generic.List[string]
foreach ($line in Get-Content -LiteralPath $InputFile -Encoding UTF8) {
    $trimmed = $line.Trim()
    if ($trimmed -and -not $trimmed.StartsWith('#')) {
        [void]$UrlList.Add($trimmed)
    }
}
$Urls = $UrlList.ToArray()

if (-not $Urls.Count) {
    throw "No URLs were found in InputFile."
}

Write-Section "Image Capture Setup"
Write-RunLog "gallery-dl path: $GalleryDlPath"
Write-RunLog "Input file: $InputFile"
Write-RunLog "Case folder: $CaseFolder"
Write-RunLog "Media folder: $MediaFolder"
Write-RunLog "Output template: $OutputTemplate"
Write-RunLog "Archive mode: $ArchiveMode"
Write-RunLog "Archive file: $ArchiveFileUsed"
Write-RunLog "Rate limit: $RateLimit"
Write-RunLog "URL count: $($Urls.Count)"

$BaseArgs = @(
    "--destination", $MediaFolder,
    "--filename", $OutputTemplate,
    "--write-unsupported", $UnsupportedFile,
    "--retries", [string]$Retries,
    "--http-timeout", [string]$Timeout,
    "--windows-filenames"
)

if ($WriteMetadata) { $BaseArgs += "--write-metadata" }
if ($WriteInfoJson) { $BaseArgs += "--write-info-json" }
if ($WriteTags) { $BaseArgs += "--write-tags" }

if ($ArchiveMode -eq "Use") {
    $BaseArgs += @("--download-archive", $ArchiveFileUsed)
}
elseif ($ArchiveMode -eq "Force") {
    $BaseArgs += "--no-skip"
}

if (-not [string]::IsNullOrWhiteSpace($CookiesFile)) {
    if (-not (Test-Path -LiteralPath $CookiesFile -PathType Leaf)) {
        throw "CookiesFile was not found: $CookiesFile"
    }
    $BaseArgs += @("--cookies", $CookiesFile)
}

if (-not [string]::IsNullOrWhiteSpace($ProxyUrl)) {
    $BaseArgs += @("--proxy", $ProxyUrl)
}

switch ($RateLimit) {
    "Fast" { }
    "Normal" { $BaseArgs += @("--sleep", "1.0-3.0", "--sleep-request", "0.5-1.5", "--sleep-429", "60") }
    "Cautious" { $BaseArgs += @("--sleep", "3.0-8.0", "--sleep-request", "1.0-3.0", "--sleep-429", "120") }
}

if (-not [string]::IsNullOrWhiteSpace($ItemRange)) {
    $BaseArgs += @("--range", $ItemRange.Trim())
}
elseif ($MaxItems -gt 0) {
    $BaseArgs += @("--range", "1-$MaxItems")
}

if ($MetadataOnly) {
    $BaseArgs += @("--simulate", "--dump-json")
}

function Write-GuiUrlResult {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("captured", "failed")][string]$Status,
        [Parameter(Mandatory = $true)][int]$Index,
        [Parameter(Mandatory = $true)][int]$Total,
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $false)][string]$Detail = "gallery-dl"
    )

    if ($Status -eq "captured") {
        $record = "{0}`tcaptured`t{1}`t{2}`t{3}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $SafeCaseName, $Url, $Detail
        Add-BufferedGuiUrlRecord -Status "captured" -Line $record
        $marker = "GUI_QUEUE_URL_COMPLETE`t{0}`t{1}`t{2}" -f $Index, $Total, $Url
    }
    else {
        $record = "{0}`tfailed`t{1}`t{2}`t{3}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $SafeCaseName, $Url, $Detail
        Add-BufferedGuiUrlRecord -Status "failed" -Line $record
        $marker = "GUI_QUEUE_URL_INCOMPLETE`t{0}`t{1}`t{2}" -f $Index, $Total, $Url
    }

    Write-Host $marker
    Write-RunLogLineOnly $marker
}

function Write-Utf8NoBomLines {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Lines
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($Path, $Lines, $encoding)
}

function Read-UrlSetFromFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    $set = @{}
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $set
    }

    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8 -ErrorAction SilentlyContinue) {
        $trimmed = $line.Trim()
        if ($trimmed -and -not $trimmed.StartsWith('#')) {
            $set[$trimmed] = $true
        }
    }

    return $set
}

$Completed = 0
$Failed = 0
$script:CapturedUrlRecords = New-Object System.Collections.Generic.List[string]
$script:FailedUrlRecords = New-Object System.Collections.Generic.List[string]

function Add-BufferedGuiUrlRecord {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("captured", "failed")][string]$Status,
        [Parameter(Mandatory = $true)][string]$Line
    )

    if ($Status -eq "captured") {
        [void]$script:CapturedUrlRecords.Add($Line)
    }
    else {
        [void]$script:FailedUrlRecords.Add($Line)
    }
}

function Write-BufferedLinesUtf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Lines,
        [Parameter(Mandatory = $false)][bool]$Append = $true
    )

    if (-not $Lines -or $Lines.Count -eq 0) {
        return
    }

    $parent = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($parent) -and -not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-DirectoryIfMissing -Path $parent
    }

    $encoding = New-Object System.Text.UTF8Encoding($false)
    $writer = New-Object System.IO.StreamWriter($Path, $Append, $encoding)
    try {
        foreach ($Line in $Lines) {
            $writer.WriteLine($Line)
        }
    }
    finally {
        $writer.Dispose()
    }
}

function Flush-GuiUrlRecords {
    Write-BufferedLinesUtf8NoBom -Path $CapturedUrlsFile -Lines $script:CapturedUrlRecords.ToArray() -Append $true
    Write-BufferedLinesUtf8NoBom -Path $FailedUrlsFile -Lines $script:FailedUrlRecords.ToArray() -Append $true
    $script:CapturedUrlRecords.Clear()
    $script:FailedUrlRecords.Clear()
}

if ($Urls.Count -gt 1) {
    Write-Section "Image URL batch"
    Write-RunLog "Using gallery-dl native input-file mode for $($Urls.Count) URLs."

    $BatchInputFile = New-AppTempFile -Prefix "avi-gallerydl-input-" -Suffix ".txt"
    $BatchErrorFile = Join-Path $LogsFolder "gallery-dl-errors_$RunStamp.txt"

    Remove-Item -LiteralPath $BatchErrorFile -Force -ErrorAction SilentlyContinue

    try {
        Write-Utf8NoBomLines -Path $BatchInputFile -Lines $Urls

        $GalleryDlArgs = @($BaseArgs + @("--input-file", $BatchInputFile, "--error-file", $BatchErrorFile))
        Write-RunLog ("Command: " + $GalleryDlPath + " " + ($GalleryDlArgs -join " "))
        Write-RunLog "Temporary input file: $BatchInputFile"
        Write-RunLog "gallery-dl error file: $BatchErrorFile"

        $ExitCode = Invoke-GalleryDlSafely -FilePath $GalleryDlPath -Arguments $GalleryDlArgs -RunLog $RunLog
        $FailedUrlSet = Read-UrlSetFromFile -Path $BatchErrorFile

        # gallery-dl writes failed URLs to --error-file. If gallery-dl returns non-zero but does not
        # provide an error file, treat the batch status as unknown and mark each submitted URL incomplete
        # instead of assuming success.
        $TreatAllAsFailed = (($ExitCode -ne 0) -and ($FailedUrlSet.Count -eq 0))

        $Index = 0
        foreach ($Url in $Urls) {
            $Index++
            if ($TreatAllAsFailed -or $FailedUrlSet.ContainsKey($Url)) {
                $Failed++
                Write-GuiUrlResult -Status "failed" -Index $Index -Total $Urls.Count -Url $Url -Detail ("gallery-dl batch exit code {0}" -f $ExitCode)
            }
            else {
                $Completed++
                Write-GuiUrlResult -Status "captured" -Index $Index -Total $Urls.Count -Url $Url -Detail "gallery-dl input-file"
            }
        }

        if ($ExitCode -ne 0) {
            Write-RunLog "gallery-dl batch finished with exit code $ExitCode"
        }
    }
    catch {
        $Failed = $Urls.Count
        $Completed = 0
        $msg = "ERROR capturing image URL batch:`r`n$($_.Exception.Message)"
        Write-Warning $msg
        Write-RunLogLineOnly $msg

        $Index = 0
        foreach ($Url in $Urls) {
            $Index++
            Write-GuiUrlResult -Status "failed" -Index $Index -Total $Urls.Count -Url $Url -Detail "gallery-dl batch script error"
        }
    }
    finally {
        Remove-Item -LiteralPath $BatchInputFile -Force -ErrorAction SilentlyContinue
    }
}
else {
    $Index = 0
    foreach ($Url in $Urls) {
        $Index++
        Write-Section "Image URL $Index of $($Urls.Count)"
        Write-RunLog "URL: $Url"

        $GalleryDlArgs = @($BaseArgs + $Url)
        Write-RunLog ("Command: " + $GalleryDlPath + " " + ($GalleryDlArgs -join " "))

        $ExitCode = 1

        try {
            # gallery-dl commonly writes normal extractor status messages to stderr, such as API-key/token
            # discovery notices. Do not use PowerShell native stderr redirection here: in Windows PowerShell
            # it turns those stderr lines into NativeCommandError records and can make otherwise successful
            # captures fail at the script layer.
            $ExitCode = Invoke-GalleryDlSafely -FilePath $GalleryDlPath -Arguments $GalleryDlArgs -RunLog $RunLog
        }
        catch {
            $ExitCode = 1
            $msg = "ERROR capturing image URL $Index`: $Url`r`n$($_.Exception.Message)"
            Write-Warning $msg
            Write-RunLogLineOnly $msg
        }

        if ($ExitCode -eq 0) {
            $Completed++
            Write-GuiUrlResult -Status "captured" -Index $Index -Total $Urls.Count -Url $Url -Detail "gallery-dl"
        }
        else {
            $Failed++
            Write-RunLog "gallery-dl failed for URL $Index of $($Urls.Count) with exit code $ExitCode"
            Write-GuiUrlResult -Status "failed" -Index $Index -Total $Urls.Count -Url $Url -Detail ("gallery-dl exit code {0}" -f $ExitCode)
        }
    }
}

Flush-GuiUrlRecords

Write-Section "Image Capture Manifest"
$CaseFiles = Get-ChildItem -LiteralPath $CaseFolder -File -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notlike "*\.gui-cache\*" -and $_.FullName -notlike "*\manifests\*"
}

$ManifestEncoding = New-Object System.Text.UTF8Encoding($false)
$ManifestWriter = New-Object System.IO.StreamWriter($ManifestFile, $false, $ManifestEncoding)
try {
    $ManifestWriter.WriteLine("SHA256,SizeBytes,RelativePath")
    foreach ($File in $CaseFiles) {
        try {
            $Hash = Get-Sha256HashCompat -Path $File.FullName
            $Relative = $File.FullName.Substring($CaseFolder.Length).TrimStart('\', '/')
            $ManifestWriter.WriteLine(('"{0}",{1},"{2}"' -f $Hash, $File.Length, ($Relative -replace '"', '""')))
        }
        catch {
            Write-RunLog "WARNING: Could not hash file: $($File.FullName) - $($_.Exception.Message)"
        }
    }
}
finally {
    $ManifestWriter.Dispose()
}

Write-Section "Image Capture Summary"
Write-RunLog "Submitted URLs: $($Urls.Count)"
Write-RunLog "Completed URLs: $Completed"
Write-RunLog "Failed URLs: $Failed"
Write-RunLog "Case folder: $CaseFolder"
Write-RunLog "Manifest: $ManifestFile"
Close-RunLogWriter

if ($Failed -gt 0) {
    exit 1
}

exit 0
