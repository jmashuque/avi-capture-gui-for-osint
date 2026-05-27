param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile,

    [Parameter(Mandatory = $true)]
    [string]$CaseName,

    [Parameter(Mandatory = $false)]
    [string]$CookiesFile,

    [Parameter(Mandatory = $false)]
    [string]$OutputRoot = ".\Investigations",

    [Parameter(Mandatory = $false)]
    [string]$YtDlpPath = ".\yt-dlp.exe",

    [Parameter(Mandatory = $false)]
    [string]$DenoPath,

    [Parameter(Mandatory = $false)]
    [string]$FFmpegFolder,

    [Parameter(Mandatory = $false)]
    [string]$ImpersonateTarget,

    [switch]$PreferMp4,

    [switch]$MetadataOnly,

    [switch]$IncludePlaylist,

    [switch]$WriteInfoJson,

    [switch]$WriteSourceLink,

    [switch]$WriteDescription,

    [switch]$WriteThumbnail,

    [switch]$WriteSubs,

    [switch]$WriteAutoSubs,

    [switch]$WriteComments,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Use", "Ignore", "Force")]
    [string]$ArchiveMode = "Use",

    [Parameter(Mandatory = $false)]
    [string]$DateAfter,

    [Parameter(Mandatory = $false)]
    [string]$DateBefore,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Fast", "Normal", "Cautious")]
    [string]$RateLimit = "Normal",

    [switch]$KeepPartials,

    [Parameter(Mandatory = $false)]
    [ValidateSet("best", "2160", "1440", "1080", "720", "480")]
    [string]$MaxResolution = "best",

    [switch]$SavePlaylistMetadata,

    [switch]$GenerateUrlShortcuts,

    [Parameter(Mandatory = $false)]
    [string]$MatchKeywords,

    [Parameter(Mandatory = $false)]
    [string]$RejectKeywords,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Continue", "Stop")]
    [string]$FailureHandling = "Continue"
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-Host "========== $Text =========="
}

function Resolve-ToolPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PathOrCommand,

        [Parameter(Mandatory = $true)]
        [string]$ToolName
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

function New-SafeCaseName {
    param([string]$Name)
    return ($Name -replace '[\\/:*?"<>|]', '_').Trim()
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

function Get-ThumbnailFileNameForPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $hash = Get-Sha256HashCompat -Path $Path
    return "$hash.png"
}

function Resolve-FFmpegForThumbnail {
    param([string]$Folder)

    if (-not [string]::IsNullOrWhiteSpace($Folder)) {
        $candidate = Join-Path $Folder "ffmpeg.exe"
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    $cmd = Get-Command "ffmpeg.exe" -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $cmd = Get-Command "ffmpeg" -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    return $null
}

function New-VideoThumbnailsForRecentCaptures {
    param(
        [Parameter(Mandatory = $true)]
        [string]$MediaRoot,

        [Parameter(Mandatory = $true)]
        [string]$ThumbnailRoot,

        [Parameter(Mandatory = $true)]
        [datetime]$Since,

        [Parameter(Mandatory = $false)]
        [string]$FFmpegExe
    )

    if ([string]::IsNullOrWhiteSpace($FFmpegExe) -or -not (Test-Path -LiteralPath $FFmpegExe -PathType Leaf)) {
        Write-Warning "FFmpeg was not found. Skipping GUI thumbnail generation."
        Add-Content -Path $RunLog -Value "FFmpeg was not found. Skipping GUI thumbnail generation."
        return
    }

    if (-not (Test-Path -LiteralPath $MediaRoot -PathType Container)) {
        return
    }

    New-Item -ItemType Directory -Path $ThumbnailRoot -Force | Out-Null

    $videoExtensions = @(".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v")

    $recentFiles = Get-ChildItem -LiteralPath $MediaRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $videoExtensions -contains $_.Extension.ToLowerInvariant() -and
            $_.LastWriteTime -ge $Since
        }

    foreach ($file in $recentFiles) {
        try {
            $thumbName = Get-ThumbnailFileNameForPath -Path $file.FullName
            $thumbPath = Join-Path $ThumbnailRoot $thumbName

            if (Test-Path -LiteralPath $thumbPath -PathType Leaf) {
                continue
            }

            Write-Host "Generating GUI thumbnail: $thumbPath"

            $ffmpegArgs = @(
                "-y",
                "-hide_banner",
                "-loglevel", "error",
                "-ss", "00:00:03",
                "-i", $file.FullName,
                "-frames:v", "1",
                "-vf", "scale=320:-1",
                $thumbPath
            )

            & $FFmpegExe @ffmpegArgs 2>&1 |
                ForEach-Object {
                    $line = $_.ToString()
                    if ($line) {
                        Write-Host $line
                        Add-Content -Path $RunLog -Value $line
                    }
                }

            if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $thumbPath -PathType Leaf)) {
                $msg = "FFmpeg could not generate thumbnail for: $($file.FullName)"
                Write-Warning $msg
                Add-Content -Path $RunLog -Value $msg
                if (Test-Path -LiteralPath $thumbPath -PathType Leaf) {
                    Remove-Item -LiteralPath $thumbPath -Force -ErrorAction SilentlyContinue
                }
            }
        }
        catch {
            $msg = "Thumbnail generation failed for $($file.FullName): $($_.Exception.Message)"
            Write-Warning $msg
            Add-Content -Path $RunLog -Value $msg
        }
    }
}



function Resolve-FFprobeForMediaInfo {
    param([string]$Folder)

    if (-not [string]::IsNullOrWhiteSpace($Folder)) {
        $candidate = Join-Path $Folder "ffprobe.exe"
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    $cmd = Get-Command "ffprobe.exe" -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $cmd = Get-Command "ffprobe" -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    return $null
}

function New-MediaInfoForRecentCaptures {
    param(
        [Parameter(Mandatory = $true)]
        [string]$MediaRoot,

        [Parameter(Mandatory = $true)]
        [string]$MetadataRoot,

        [Parameter(Mandatory = $true)]
        [datetime]$Since,

        [Parameter(Mandatory = $false)]
        [string]$FFprobeExe
    )

    if ([string]::IsNullOrWhiteSpace($FFprobeExe) -or -not (Test-Path -LiteralPath $FFprobeExe -PathType Leaf)) {
        Write-Warning "FFprobe was not found. Skipping GUI media information generation."
        Add-Content -Path $RunLog -Value "FFprobe was not found. Skipping GUI media information generation."
        return
    }

    if (-not (Test-Path -LiteralPath $MediaRoot -PathType Container)) {
        return
    }

    New-Item -ItemType Directory -Path $MetadataRoot -Force | Out-Null

    $mediaExtensions = @(".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".mp3", ".m4a", ".opus", ".wav", ".aac", ".flac")

    $recentFiles = Get-ChildItem -LiteralPath $MediaRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $mediaExtensions -contains $_.Extension.ToLowerInvariant() -and
            $_.LastWriteTime -ge $Since
        }

    foreach ($file in $recentFiles) {
        try {
            $metadataName = (Get-ThumbnailFileNameForPath -Path $file.FullName) -replace '\.png$', '.ffprobe.json'
            $metadataPath = Join-Path $MetadataRoot $metadataName

            if (Test-Path -LiteralPath $metadataPath -PathType Leaf) {
                continue
            }

            Write-Host "Generating GUI media info: $metadataPath"

            $ffprobeArgs = @(
                "-v", "error",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                $file.FullName
            )

            $json = & $FFprobeExe @ffprobeArgs 2>&1 | Out-String

            if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($json)) {
                Set-Content -LiteralPath $metadataPath -Value $json -Encoding UTF8
            }
            else {
                $msg = "FFprobe could not generate media info for: $($file.FullName)"
                Write-Warning $msg
                Add-Content -Path $RunLog -Value $msg
            }
        }
        catch {
            $msg = "Media info generation failed for $($file.FullName): $($_.Exception.Message)"
            Write-Warning $msg
            Add-Content -Path $RunLog -Value $msg
        }
    }
}

function Normalize-YtDlpDate {
    param(
        [string]$Value,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $null
    }

    $clean = ($Value.Trim() -replace '-', '')

    if ($clean -notmatch '^\d{8}$') {
        throw "$Name must be in YYYYMMDD or YYYY-MM-DD format."
    }

    try {
        $null = [datetime]::ParseExact($clean, "yyyyMMdd", $null)
    }
    catch {
        throw "$Name is not a valid date: $Value"
    }

    return $clean
}

function Convert-KeywordsToRegex {
    param([string]$Keywords)

    if ([string]::IsNullOrWhiteSpace($Keywords)) {
        return $null
    }

    $items = $Keywords -split '[,\r\n;]' |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }

    if (-not $items -or $items.Count -eq 0) {
        return $null
    }

    $escaped = $items | ForEach-Object { [regex]::Escape($_) }
    return "(?i)(" + ($escaped -join "|") + ")"
}

$YtDlpPath = Resolve-ToolPath -PathOrCommand $YtDlpPath -ToolName "yt-dlp"

if ([string]::IsNullOrWhiteSpace($DenoPath)) {
    $CandidateDeno = Join-Path (Split-Path -Parent $YtDlpPath) "deno.exe"
    if (Test-Path -LiteralPath $CandidateDeno -PathType Leaf) {
        $DenoPath = $CandidateDeno
    }
    else {
        $DenoPath = "deno"
    }
}

$DenoPath = Resolve-ToolPath -PathOrCommand $DenoPath -ToolName "Deno"

if (-not [string]::IsNullOrWhiteSpace($FFmpegFolder)) {
    if (-not (Test-Path -LiteralPath $FFmpegFolder -PathType Container)) {
        throw "FFmpeg folder not found: $FFmpegFolder"
    }

    $ffmpegExe = Join-Path $FFmpegFolder "ffmpeg.exe"
    $ffprobeExe = Join-Path $FFmpegFolder "ffprobe.exe"

    if (-not (Test-Path -LiteralPath $ffmpegExe -PathType Leaf)) {
        throw "ffmpeg.exe was not found in FFmpeg folder: $FFmpegFolder"
    }

    if (-not (Test-Path -LiteralPath $ffprobeExe -PathType Leaf)) {
        throw "ffprobe.exe was not found in FFmpeg folder: $FFmpegFolder"
    }
}

$SafeCaseName = New-SafeCaseName $CaseName
$CaseDir = Join-Path $OutputRoot $SafeCaseName
$MediaDir = Join-Path $CaseDir "media"
$LogDir = Join-Path $CaseDir "logs"
$ManifestDir = Join-Path $CaseDir "manifests"
$GuiCacheDir = Join-Path $CaseDir ".gui-cache"
$GuiThumbnailDir = Join-Path $GuiCacheDir "thumbnails"
$GuiMetadataDir = Join-Path $GuiCacheDir "metadata"

$ArchiveFile = Join-Path $CaseDir "download-archive.txt"
$RunLog = Join-Path $LogDir ("yt-dlp-run_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$HashManifest = Join-Path $ManifestDir ("sha256-manifest_{0}.csv" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

New-Item -ItemType Directory -Path $CaseDir, $MediaDir, $LogDir, $ManifestDir, $GuiThumbnailDir, $GuiMetadataDir -Force | Out-Null

$FFmpegForThumbnails = Resolve-FFmpegForThumbnail -Folder $FFmpegFolder
$FFprobeForMediaInfo = Resolve-FFprobeForMediaInfo -Folder $FFmpegFolder

$DateAfterClean = Normalize-YtDlpDate -Value $DateAfter -Name "DateAfter"
$DateBeforeClean = Normalize-YtDlpDate -Value $DateBefore -Name "DateBefore"

if ($DateAfterClean -and $DateBeforeClean -and $DateAfterClean -gt $DateBeforeClean) {
    throw "DateAfter cannot be later than DateBefore."
}

switch ($RateLimit) {
    "Fast" {
        $SleepBaselineSeconds = 15
        $SleepRequestSeconds = 2
    }
    "Cautious" {
        $SleepBaselineSeconds = 60
        $SleepRequestSeconds = 10
    }
    default {
        $SleepBaselineSeconds = 30
        $SleepRequestSeconds = 5
    }
}

$SleepMaxSeconds = $SleepBaselineSeconds * 2

Write-Section "Preflight checks"

if (-not (Test-Path -LiteralPath $InputFile -PathType Leaf)) {
    throw "Input file not found: $InputFile"
}

if ($CookiesFile -and -not (Test-Path -LiteralPath $CookiesFile -PathType Leaf)) {
    throw "Cookies file not found: $CookiesFile"
}

Write-Host "yt-dlp:        $YtDlpPath"
Write-Host "Deno:          $DenoPath"
Write-Host "FFmpeg folder: $FFmpegFolder"
Write-Host "Case:          $CaseDir"

Write-Section "Version info"

& $YtDlpPath --version 2>&1 | Tee-Object -FilePath $RunLog -Append
& $DenoPath --version 2>&1 | Tee-Object -FilePath $RunLog -Append

if (-not [string]::IsNullOrWhiteSpace($FFmpegFolder)) {
    $ffmpegExe = Join-Path $FFmpegFolder "ffmpeg.exe"
    & $ffmpegExe -version 2>&1 | Select-Object -First 1 | Tee-Object -FilePath $RunLog -Append
}

Write-Section "Capture options"

$OptionLines = @(
    "Prefer MP4:             $PreferMp4",
    "Metadata only:          $MetadataOnly",
    "Include playlist:       $IncludePlaylist",
    "Write metadata JSON:    $WriteInfoJson",
    "Write source link:      $WriteSourceLink",
    "Write description:      $WriteDescription",
    "Write thumbnail:        $WriteThumbnail",
    "Write subtitles:        $WriteSubs",
    "Write auto subtitles:   $WriteAutoSubs",
    "Write comments:         $WriteComments",
    "Archive mode:           $ArchiveMode",
    "Date after:             $DateAfterClean",
    "Date before:            $DateBeforeClean",
    "Rate limit:             $RateLimit ($SleepBaselineSeconds-$SleepMaxSeconds sec)",
    "Keep partials:          $KeepPartials",
    "Max resolution:         $MaxResolution",
    "Save playlist metadata: $SavePlaylistMetadata",
    "Generate URL shortcuts: $GenerateUrlShortcuts",
    "Match keywords:         $MatchKeywords",
    "Reject keywords:        $RejectKeywords",
    "Failure handling:       $FailureHandling",
    "Impersonate target:     $ImpersonateTarget"
)

$OptionLines | Tee-Object -FilePath $RunLog -Append

Write-Section "Loading URLs"

$Urls = @(
    Get-Content -LiteralPath $InputFile |
        ForEach-Object { $_.Trim() } |
        Where-Object {
            $_ -and
            -not $_.StartsWith("#") -and
            ($_ -match '^https?://')
        }
)

if (-not $Urls -or $Urls.Count -eq 0) {
    throw "No valid URLs found in input file. Use one http/https URL per line."
}

Write-Host "Found $($Urls.Count) URL(s)."

Write-Section "Starting capture"

$CommonArgs = @(
    "--continue",
    "--restrict-filenames",
    "--trim-filenames", "180",

    "--js-runtimes", "deno:$DenoPath",

    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "--add-header", "Accept-Language: en-US,en;q=0.9",

    "--no-embed-metadata",
    "--no-embed-thumbnail",
    "--no-embed-subs",

    "--sleep-requests", "$SleepRequestSeconds",
    "--sleep-interval", "$SleepBaselineSeconds",
    "--max-sleep-interval", "$SleepMaxSeconds",

    "--retries", "5",
    "--fragment-retries", "5",
    "--retry-sleep", "exp=10:120",

    "--paths", $MediaDir,

    "--output", "%(extractor)s/%(uploader|unknown)s/%(upload_date|unknown)s_%(id)s_%(title).180B.%(ext)s",

    "--verbose"
)

if ($FailureHandling -eq "Continue") {
    $CommonArgs += "--ignore-errors"
}

switch ($ArchiveMode) {
    "Use" {
        $CommonArgs += @("--download-archive", $ArchiveFile)
        $CommonArgs += "--no-overwrites"
    }
    "Ignore" {
        $CommonArgs += "--no-overwrites"
    }
    "Force" {
        $CommonArgs += "--force-overwrites"
    }
}

if (-not $IncludePlaylist) {
    $CommonArgs += "--no-playlist"
}

if ($MetadataOnly) {
    $CommonArgs += "--skip-download"
}

if ($DateAfterClean) {
    $CommonArgs += @("--dateafter", $DateAfterClean)
}

if ($DateBeforeClean) {
    $CommonArgs += @("--datebefore", $DateBeforeClean)
}

if ($KeepPartials) {
    $CommonArgs += "--keep-fragments"
}

$MatchTitleRegex = Convert-KeywordsToRegex -Keywords $MatchKeywords
if ($MatchTitleRegex) {
    $CommonArgs += @("--match-title", $MatchTitleRegex)
}

$RejectTitleRegex = Convert-KeywordsToRegex -Keywords $RejectKeywords
if ($RejectTitleRegex) {
    $CommonArgs += @("--reject-title", $RejectTitleRegex)
}

if ($WriteInfoJson) {
    $CommonArgs += "--write-info-json"
}

if ($WriteSourceLink) {
    $CommonArgs += "--write-link"
}

if ($WriteDescription) {
    $CommonArgs += "--write-description"
}

if ($WriteThumbnail) {
    $CommonArgs += "--write-thumbnail"
}

if ($WriteSubs) {
    $CommonArgs += "--write-subs"
}

if ($WriteAutoSubs) {
    $CommonArgs += "--write-auto-subs"
}

if ($WriteComments) {
    $CommonArgs += "--write-comments"
}

if ($SavePlaylistMetadata -and $IncludePlaylist) {
    $CommonArgs += "--write-playlist-metafiles"
}

if ($GenerateUrlShortcuts) {
    $CommonArgs += "--write-url-link"
}

if ($MaxResolution -ne "best" -and -not $MetadataOnly) {
    if ($PreferMp4) {
        $FormatSelector = "bv*[ext=mp4][height<=$MaxResolution]+ba[ext=m4a]/b[ext=mp4][height<=$MaxResolution]/bv*[height<=$MaxResolution]+ba/b[height<=$MaxResolution]/best[height<=$MaxResolution]/best"
    }
    else {
        $FormatSelector = "bv*[height<=$MaxResolution]+ba/b[height<=$MaxResolution]/best[height<=$MaxResolution]/best"
    }

    $CommonArgs += @("--format", $FormatSelector)
}
elseif ($PreferMp4 -and -not $MetadataOnly) {
    $CommonArgs += @(
        "--format", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
        "--merge-output-format", "mp4"
    )
}

if ($CookiesFile) {
    $CommonArgs += @("--cookies", $CookiesFile)
}

if ($FFmpegFolder) {
    $CommonArgs += @("--ffmpeg-location", $FFmpegFolder)
}

if ($ImpersonateTarget) {
    $CommonArgs += @("--impersonate", $ImpersonateTarget)
}

for ($i = 0; $i -lt $Urls.Count; $i++) {
    $Url = $Urls[$i]

    Write-Host ""
    Write-Host "Capturing: $Url"

    $CaptureStartTime = Get-Date
    $PreviousErrorActionPreference = $ErrorActionPreference

    try {
        $ErrorActionPreference = "Continue"

        & $YtDlpPath @CommonArgs $Url 2>&1 |
            ForEach-Object {
                $line = $_.ToString()
                Write-Host $line
                Add-Content -Path $RunLog -Value $line
            }

        $YtDlpExitCode = $LASTEXITCODE
    }
    catch {
        $YtDlpExitCode = 1
        $msg = "ERROR capturing URL: $Url`r`n$($_.Exception.Message)"
        Write-Warning $msg
        Add-Content -Path $RunLog -Value $msg
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    New-VideoThumbnailsForRecentCaptures -MediaRoot $MediaDir -ThumbnailRoot $GuiThumbnailDir -Since $CaptureStartTime -FFmpegExe $FFmpegForThumbnails
    New-MediaInfoForRecentCaptures -MediaRoot $MediaDir -MetadataRoot $GuiMetadataDir -Since $CaptureStartTime -FFprobeExe $FFprobeForMediaInfo

    if ($YtDlpExitCode -ne 0) {
        $msg = "yt-dlp exited with code $YtDlpExitCode for URL: $Url"
        Write-Warning $msg
        Add-Content -Path $RunLog -Value $msg

        if ($FailureHandling -eq "Stop") {
            Write-Warning "Stopping capture because FailureHandling is set to Stop."
            break
        }
    }

    if ($i -lt ($Urls.Count - 1)) {
        $PauseSeconds = Get-Random -Minimum $SleepBaselineSeconds -Maximum ($SleepMaxSeconds + 1)
        Write-Host "Pausing $PauseSeconds seconds before next URL..."
        Start-Sleep -Seconds $PauseSeconds
    }
}

Write-Section "Hashing captured files"

$manifestRows = foreach ($file in Get-ChildItem $CaseDir -Recurse -File) {
    if ($file.FullName -eq $HashManifest) {
        continue
    }

    [PSCustomObject]@{
        Algorithm = "SHA256"
        Hash      = Get-Sha256HashCompat -Path $file.FullName
        Path      = $file.FullName
    }
}

$manifestRows | Export-Csv $HashManifest -NoTypeInformation

Write-Host "Hash manifest written to: $HashManifest"

Write-Section "Done"

Write-Host "Case folder:      $CaseDir"
Write-Host "Run log:          $RunLog"
Write-Host "Download archive: $ArchiveFile"
Write-Host "SHA256 manifest:  $HashManifest"
