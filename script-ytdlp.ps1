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
    [string]$YtDlpPath = ".\yt-dlp.exe",

    [Parameter(Mandatory = $false)]
    [string]$DenoPath,

    [Parameter(Mandatory = $false)]
    [string]$FFmpegFolder,

    [Parameter(Mandatory = $false)]
    [string]$ImpersonateTarget,

    [switch]$PreferMp4,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Best", "PreferMp4", "StrictMp4", "AudioOnly", "LowBandwidth")]
    [string]$FormatStrategy = "Best",

    [switch]$MetadataOnly,

    [switch]$MediaOnly,

    [switch]$IncludePlaylist,

    [Parameter(Mandatory = $false)]
    [string]$PlaylistItems,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Normal", "Reverse", "Random")]
    [string]$PlaylistOrder = "Normal",

    [Parameter(Mandatory = $false)]
    [ValidateRange(0, 1000000)]
    [int]$MaxPlaylistItems = 0,

    [switch]$BreakOnExisting,

    [Parameter(Mandatory = $false)]
    [ValidateRange(0, 1000000)]
    [int]$SkipPlaylistAfterErrors = 0,

    [switch]$WriteInfoJson,

    [switch]$WriteSourceLink,

    [switch]$WriteDescription,

    [switch]$WriteThumbnail,

    [switch]$WriteSubs,

    [switch]$WriteAutoSubs,

    [switch]$WriteComments,

    [switch]$EmbedMetadata,

    [switch]$EmbedThumbnail,

    [switch]$EmbedSubs,

    [switch]$EmbedChapters,

    [switch]$EmbedInfoJson,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Use", "Ignore", "Force")]
    [string]$ArchiveMode = "Use",

    [Parameter(Mandatory = $false)]
    [string]$UniversalArchiveFile,

    [Parameter(Mandatory = $false)]
    [string]$DateAfter,

    [Parameter(Mandatory = $false)]
    [string]$DateBefore,

    [Parameter(Mandatory = $false)]
    [ValidateSet("None", "Fast", "Normal", "Cautious")]
    [string]$RateLimit = "Normal",

    [Parameter(Mandatory = $false)]
    [string]$DownloadSpeedLimit = "Disabled",

    [Parameter(Mandatory = $false)]
    [ValidateSet("Light", "Normal", "Aggressive")]
    [string]$RetryBehavior = "Normal",

    [Parameter(Mandatory = $false)]
    [string]$ThrottledRate = "Disabled",

    [Parameter(Mandatory = $false)]
    [string]$HttpChunkSize = "Disabled",

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 8)]
    [int]$ConcurrentFragments = 1,

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
    [string]$FailureHandling = "Continue",

    [Parameter(Mandatory = $false)]
    [string]$ProxyUrl,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Off", "AfterEachUrl", "AfterRun")]
    [string]$GuiCacheMode = "AfterRun",

    [Parameter(Mandatory = $false)]
    [ValidateSet("Full", "RunOnly")]
    [string]$ManifestMode = "Full"
)

$ErrorActionPreference = "Stop"

if ($MetadataOnly -and $MediaOnly) {
    throw "MetadataOnly and MediaOnly cannot both be enabled."
}

$EmbedRequested = $EmbedMetadata -or $EmbedThumbnail -or $EmbedSubs -or $EmbedChapters -or $EmbedInfoJson

if ($EmbedRequested -and ($MetadataOnly -or $MediaOnly)) {
    throw "Embed options require a media capture mode. They cannot be used with MetadataOnly or MediaOnly."
}

$PlaylistItemsClean = ""
if (-not [string]::IsNullOrWhiteSpace($PlaylistItems)) {
    $PlaylistItemsClean = ($PlaylistItems -replace '\s+', '')

    if ($PlaylistItemsClean -notmatch '^[0-9,:\-]+$') {
        throw "PlaylistItems is invalid. Use indexes or ranges such as 1:10,30,35:40."
    }
}

$PlaylistOptionsRequested = (
    -not [string]::IsNullOrWhiteSpace($PlaylistItemsClean) -or
    $PlaylistOrder -ne "Normal" -or
    $MaxPlaylistItems -gt 0 -or
    $BreakOnExisting -or
    $SkipPlaylistAfterErrors -gt 0
)

if ($PlaylistOptionsRequested -and -not $IncludePlaylist) {
    throw "Playlist options require IncludePlaylist."
}

if ($MetadataOnly -and $FormatStrategy -eq "AudioOnly") {
    throw "AudioOnly format cannot be used with MetadataOnly."
}

if ($SavePlaylistMetadata -and -not $IncludePlaylist) {
    throw "SavePlaylistMetadata requires IncludePlaylist."
}

if (-not [string]::IsNullOrWhiteSpace($ProxyUrl)) {
    if ($ProxyUrl -notmatch '^(https?|socks4|socks5)://') {
        throw "ProxyUrl must start with http://, https://, socks4://, or socks5://."
    }

    try {
        $null = [System.Uri]$ProxyUrl
    }
    catch {
        throw "ProxyUrl is not a valid URL."
    }
}

$script:RunLog = ""
$script:RunLogWriter = $null

function Initialize-RunLogWriter {
    if ([string]::IsNullOrWhiteSpace($script:RunLog)) {
        return
    }

    if ($null -ne $script:RunLogWriter) {
        return
    }

    $parent = Split-Path -Parent $script:RunLog
    if (-not [string]::IsNullOrWhiteSpace($parent) -and -not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $encoding = New-Object System.Text.UTF8Encoding($false)
    $script:RunLogWriter = New-Object System.IO.StreamWriter($script:RunLog, $true, $encoding)
}

function Add-RunLogLine {
    param([AllowNull()][string]$Message)

    if ([string]::IsNullOrWhiteSpace($script:RunLog)) {
        return
    }

    if ($null -eq $script:RunLogWriter) {
        Initialize-RunLogWriter
    }

    if ($null -ne $script:RunLogWriter) {
        $script:RunLogWriter.WriteLine([string]$Message)
    }
    else {
        Add-Content -LiteralPath $script:RunLog -Value $Message -Encoding UTF8
    }
}

function Flush-RunLogWriter {
    if ($null -ne $script:RunLogWriter) {
        $script:RunLogWriter.Flush()
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

function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-Host "========== $Text =========="
}

function Write-RunLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host $Message

    Add-RunLogLine $Message
}

function Write-RunWarning {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Warning $Message

    Add-RunLogLine $Message
}

function Get-GuiCacheFileNameForPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        $item = Get-Item -LiteralPath $Path -ErrorAction Stop
        $fingerprint = "{0}|{1}|{2}" -f $item.FullName.ToLowerInvariant(), $item.Length, $item.LastWriteTimeUtc.Ticks
    }
    catch {
        $fingerprint = [System.IO.Path]::GetFullPath($Path).ToLowerInvariant()
    }

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($fingerprint)
    $sha = [System.Security.Cryptography.SHA256]::Create()

    try {
        return (([BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', '').ToUpperInvariant()) + ".png"
    }
    finally {
        $sha.Dispose()
    }
}

function Get-MaskedProxyUrl {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return "disabled"
    }

    try {
        $uri = [System.Uri]$Value
        $hostAndPort = $uri.Host

        if (-not $uri.IsDefaultPort -and $uri.Port -gt 0) {
            $hostAndPort = "{0}:{1}" -f $uri.Host, $uri.Port
        }

        $credentialMarker = ""
        if (-not [string]::IsNullOrWhiteSpace($uri.UserInfo)) {
            $credentialMarker = "***@"
        }

        return "{0}://{1}{2}/" -f $uri.Scheme, $credentialMarker, $hostAndPort
    }
    catch {
        return "[proxy configured]"
    }
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

    if ($clean -notmatch '%\(ext' -and $clean -notmatch '%ext%') {
        $clean = "$clean.%(ext)s"
    }

    $parts = $clean -split '/'
    foreach ($part in $parts) {
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

function Get-ThumbnailFileNameForPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return Get-GuiCacheFileNameForPath -Path $Path
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
        Add-RunLogLine "FFmpeg was not found. Skipping GUI thumbnail generation."
        return $false
    }

    if (-not (Test-Path -LiteralPath $MediaRoot -PathType Container)) {
        return $true
    }

    $allOk = $true

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
                        Add-RunLogLine $line
                    }
                }

            if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $thumbPath -PathType Leaf)) {
                $allOk = $false
                $msg = "FFmpeg could not generate thumbnail for: $($file.FullName)"
                Write-Warning $msg
                Add-RunLogLine $msg
                if (Test-Path -LiteralPath $thumbPath -PathType Leaf) {
                    Remove-Item -LiteralPath $thumbPath -Force -ErrorAction SilentlyContinue
                }
            }
        }
        catch {
            $allOk = $false
            $msg = "Thumbnail generation failed for $($file.FullName): $($_.Exception.Message)"
            Write-Warning $msg
            Add-RunLogLine $msg
        }
    }

    return $allOk
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
        Add-RunLogLine "FFprobe was not found. Skipping GUI media information generation."
        return $false
    }

    if (-not (Test-Path -LiteralPath $MediaRoot -PathType Container)) {
        return $true
    }

    $allOk = $true

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
                $allOk = $false
                $msg = "FFprobe could not generate media info for: $($file.FullName)"
                Write-Warning $msg
                Add-RunLogLine $msg
            }
        }
        catch {
            $allOk = $false
            $msg = "Media info generation failed for $($file.FullName): $($_.Exception.Message)"
            Write-Warning $msg
            Add-RunLogLine $msg
        }
    }

    return $allOk
}

function ConvertTo-YtDlpDate {
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

function Read-DownloadArchiveEntries {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return @()
    }

    return @(
        Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue |
            ForEach-Object { $_.Trim() } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
}

function New-ArchiveEntryLookup {
    param(
        [Parameter(Mandatory = $false)][string[]]$Entries = @()
    )

    $lookup = @{}
    foreach ($entry in $Entries) {
        $clean = [string]$entry
        if (-not [string]::IsNullOrWhiteSpace($clean) -and -not $lookup.ContainsKey($clean)) {
            $lookup[$clean] = $true
        }
    }

    return $lookup
}

function Add-UniqueDownloadArchiveEntries {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $false)][string[]]$Entries = @()
    )

    if ([string]::IsNullOrWhiteSpace($Path) -or -not $Entries -or $Entries.Count -eq 0) {
        return 0
    }

    $archiveDir = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($archiveDir) -and -not (Test-Path -LiteralPath $archiveDir)) {
        New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        New-Item -ItemType File -Path $Path -Force | Out-Null
    }

    $existing = New-ArchiveEntryLookup -Entries (Read-DownloadArchiveEntries -Path $Path)
    $toAdd = New-Object System.Collections.Generic.List[string]

    foreach ($entry in $Entries) {
        $clean = ([string]$entry).Trim()
        if ([string]::IsNullOrWhiteSpace($clean)) {
            continue
        }

        if (-not $existing.ContainsKey($clean)) {
            $existing[$clean] = $true
            [void]$toAdd.Add($clean)
        }
    }

    if ($toAdd.Count -gt 0) {
        Add-Content -LiteralPath $Path -Value $toAdd.ToArray() -Encoding UTF8
    }

    return $toAdd.Count
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
$ArchiveFileForYtDlp = $ArchiveFile
$UniversalArchiveActive = ($ArchiveMode -eq "Use" -and -not [string]::IsNullOrWhiteSpace($UniversalArchiveFile))
$UniversalArchivePreRunEntries = @{}
$script:UniversalArchiveSeededFromCase = 0
$script:UniversalArchiveNewEntriesThisRun = 0
$script:UniversalArchiveCaseEntriesAddedThisRun = 0
$script:UniversalArchiveSkipRecords = New-Object System.Collections.Generic.List[object]
$script:UniversalArchiveSkipLookup = @{}
$UniversalArchiveSkipJson = Join-Path $ManifestDir ("universal-archive-skips_{0}.json" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$UniversalArchiveSkipCsv = Join-Path $ManifestDir ("universal-archive-skips_{0}.csv" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$GlobalFailedUrlsFile = Join-Path $OutputRoot "gui-failed-urls.txt"
$GlobalCapturedUrlsFile = Join-Path $OutputRoot "gui-captured-urls.txt"
$RunLog = Join-Path $LogDir ("yt-dlp-run_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$script:RunLog = $RunLog
Initialize-RunLogWriter
$HashManifest = Join-Path $ManifestDir ("sha256-manifest_{0}.csv" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

if ([string]::IsNullOrWhiteSpace($OutputTemplate)) {
    $OutputTemplate = "%(extractor)s/%(uploader|unknown)s/%(upload_date|unknown)s_%(id)s_%(title).180B.%(ext)s"
}

$OutputTemplateForYtDlp = Test-RelativeOutputTemplate -Template $OutputTemplate

New-Item -ItemType Directory -Path $CaseDir, $MediaDir, $LogDir, $ManifestDir, $GuiThumbnailDir, $GuiMetadataDir -Force | Out-Null

if ($UniversalArchiveActive) {
    try {
        $UniversalArchiveFile = [System.IO.Path]::GetFullPath($UniversalArchiveFile)
    }
    catch {
        throw "UniversalArchiveFile is invalid: $UniversalArchiveFile"
    }

    $universalArchiveDir = Split-Path -Parent $UniversalArchiveFile
    if (-not [string]::IsNullOrWhiteSpace($universalArchiveDir) -and -not (Test-Path -LiteralPath $universalArchiveDir)) {
        New-Item -ItemType Directory -Path $universalArchiveDir -Force | Out-Null
    }

    if (-not (Test-Path -LiteralPath $UniversalArchiveFile -PathType Leaf)) {
        New-Item -ItemType File -Path $UniversalArchiveFile -Force | Out-Null
    }

    if (-not (Test-Path -LiteralPath $ArchiveFile -PathType Leaf)) {
        New-Item -ItemType File -Path $ArchiveFile -Force | Out-Null
    }

    $script:UniversalArchiveSeededFromCase = Add-UniqueDownloadArchiveEntries -Path $UniversalArchiveFile -Entries (Read-DownloadArchiveEntries -Path $ArchiveFile)
    $UniversalArchivePreRunEntries = New-ArchiveEntryLookup -Entries (Read-DownloadArchiveEntries -Path $UniversalArchiveFile)
    $ArchiveFileForYtDlp = $UniversalArchiveFile
}

function Add-GuiUrlRecord {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$CaseName,
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $false)][string]$Detail = ""
    )

    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $safeDetail = $Detail -replace "`t", " "
    $safeDetail = $safeDetail -replace "`r?`n", " "
    $line = "{0}`t{1}`t{2}`t{3}`t{4}" -f $timestamp, $Status, $CaseName, $Url, $safeDetail
    Add-Content -LiteralPath $Path -Value $line -Encoding UTF8
}

function Sync-UniversalArchiveEntriesToCase {
    if (-not $UniversalArchiveActive) {
        return
    }

    $newEntries = @(
        foreach ($entry in (Read-DownloadArchiveEntries -Path $UniversalArchiveFile)) {
            $clean = ([string]$entry).Trim()
            if (-not [string]::IsNullOrWhiteSpace($clean) -and -not $UniversalArchivePreRunEntries.ContainsKey($clean)) {
                $clean
            }
        }
    )

    if (-not $newEntries -or $newEntries.Count -eq 0) {
        return
    }

    $caseAdded = Add-UniqueDownloadArchiveEntries -Path $ArchiveFile -Entries $newEntries

    foreach ($entry in $newEntries) {
        $clean = ([string]$entry).Trim()
        if (-not [string]::IsNullOrWhiteSpace($clean)) {
            $UniversalArchivePreRunEntries[$clean] = $true
        }
    }

    $script:UniversalArchiveNewEntriesThisRun += $newEntries.Count
    $script:UniversalArchiveCaseEntriesAddedThisRun += $caseAdded

    $entryWord = if ($caseAdded -eq 1) { "entry" } else { "entries" }
    Write-RunLog "Universal archive sync: appended $caseAdded new $entryWord to the case archive."
}

function Get-UniversalArchiveSkipArchiveIdFromLine {
    param(
        [Parameter(Mandatory = $false)][string]$Line
    )

    $value = [string]$Line
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $null
    }

    if ($value -match '^\[download\]\s+(.+?)\s+has already been recorded in the archive') {
        return $matches[1].Trim()
    }

    if ($value -match 'has already been recorded in the archive') {
        return ""
    }

    return $null
}

function Add-UniversalArchiveSkipRecord {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $false)][string]$ArchiveId = "",
        [Parameter(Mandatory = $false)][string]$Message = "",
        [Parameter(Mandatory = $false)][int]$UrlIndex = 0,
        [Parameter(Mandatory = $false)][int]$UrlTotal = 0
    )

    if (-not $UniversalArchiveActive) {
        return
    }

    $cleanUrl = ([string]$Url).Trim()
    $cleanArchiveId = ([string]$ArchiveId).Trim()
    $cleanMessage = ([string]$Message).Trim()
    $lookupKey = "{0}`n{1}" -f $cleanUrl, $cleanArchiveId

    if ($script:UniversalArchiveSkipLookup.ContainsKey($lookupKey)) {
        return
    }

    $script:UniversalArchiveSkipLookup[$lookupKey] = $true

    $record = [PSCustomObject]@{
        timestamp_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        case_name = $SafeCaseName
        url = $cleanUrl
        archive_id = $cleanArchiveId
        message = $cleanMessage
        url_index = $UrlIndex
        url_total = $UrlTotal
    }

    [void]$script:UniversalArchiveSkipRecords.Add($record)

    $displayId = if ([string]::IsNullOrWhiteSpace($cleanArchiveId)) { "unknown archive id" } else { $cleanArchiveId }
    Write-RunLog "Universal archive skip detected: $displayId | URL: $cleanUrl"

    $safeArchiveId = $cleanArchiveId -replace "`t", " "
    $safeUrl = $cleanUrl -replace "`t", " "
    Write-Host ("GUI_UNIVERSAL_ARCHIVE_SKIP`t{0}`t{1}`t{2}`t{3}" -f $UrlIndex, $UrlTotal, $safeArchiveId, $safeUrl)
}

function Write-UniversalArchiveSkipSummary {
    if (-not $UniversalArchiveActive) {
        return
    }

    $skipCount = $script:UniversalArchiveSkipRecords.Count

    Write-Section "Universal archive skip summary"

    if ($skipCount -le 0) {
        Write-RunLog "No items were skipped because the universal archive already contained them."
        return
    }

    try {
        $script:UniversalArchiveSkipRecords | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $UniversalArchiveSkipJson -Encoding UTF8
        $script:UniversalArchiveSkipRecords | Export-Csv -LiteralPath $UniversalArchiveSkipCsv -NoTypeInformation -Encoding UTF8
    }
    catch {
        Write-RunWarning "Could not write universal archive skip manifest: $($_.Exception.Message)"
    }

    Write-RunLog "Universal archive skipped $skipCount item(s) because the active universal archive already contained them."
    Write-RunLog "Universal archive skip JSON: $UniversalArchiveSkipJson"
    Write-RunLog "Universal archive skip CSV: $UniversalArchiveSkipCsv"

    foreach ($record in $script:UniversalArchiveSkipRecords) {
        $displayId = if ([string]::IsNullOrWhiteSpace($record.archive_id)) { "unknown archive id" } else { $record.archive_id }
        Write-RunLog ("- {0} | {1}" -f $displayId, $record.url)
    }

    $safeJson = $UniversalArchiveSkipJson -replace "`t", " "
    $safeCsv = $UniversalArchiveSkipCsv -replace "`t", " "
    Write-Host ("GUI_UNIVERSAL_ARCHIVE_SKIP_SUMMARY`t{0}`t{1}`t{2}" -f $skipCount, $safeJson, $safeCsv)
}

$FFmpegForThumbnails = Resolve-FFmpegForThumbnail -Folder $FFmpegFolder
$FFprobeForMediaInfo = Resolve-FFprobeForMediaInfo -Folder $FFmpegFolder

$DateAfterClean = ConvertTo-YtDlpDate -Value $DateAfter -Name "DateAfter"
$DateBeforeClean = ConvertTo-YtDlpDate -Value $DateBefore -Name "DateBefore"

if ($DateAfterClean -and $DateBeforeClean -and $DateAfterClean -gt $DateBeforeClean) {
    throw "DateAfter cannot be later than DateBefore."
}

switch ($RateLimit) {
    "None" {
        $SleepBaselineSeconds = 0
        $SleepMaxSeconds = 5
        $SleepRequestSeconds = 0
    }
    "Fast" {
        $SleepBaselineSeconds = 15
        $SleepMaxSeconds = 30
        $SleepRequestSeconds = 2
    }
    "Cautious" {
        $SleepBaselineSeconds = 60
        $SleepMaxSeconds = 120
        $SleepRequestSeconds = 10
    }
    default {
        $SleepBaselineSeconds = 30
        $SleepMaxSeconds = 60
        $SleepRequestSeconds = 5
    }
}

$DownloadSpeedLimitClean = $DownloadSpeedLimit.Trim()

if ([string]::IsNullOrWhiteSpace($DownloadSpeedLimitClean)) {
    $DownloadSpeedLimitClean = "Disabled"
}

if ($DownloadSpeedLimitClean -ne "Disabled" -and $DownloadSpeedLimitClean -notmatch '^\d+$') {
    throw "DownloadSpeedLimit must be Disabled or an integer byte-per-second value generated by the GUI."
}

$ThrottledRateClean = $ThrottledRate.Trim()
if ([string]::IsNullOrWhiteSpace($ThrottledRateClean)) {
    $ThrottledRateClean = "Disabled"
}

if ($ThrottledRateClean -ne "Disabled" -and $ThrottledRateClean -notmatch '^\d+$') {
    throw "ThrottledRate must be Disabled or an integer byte-per-second value generated by the GUI."
}

$HttpChunkSizeClean = $HttpChunkSize.Trim()
if ([string]::IsNullOrWhiteSpace($HttpChunkSizeClean)) {
    $HttpChunkSizeClean = "Disabled"
}

if ($HttpChunkSizeClean -ne "Disabled" -and $HttpChunkSizeClean -notmatch '^\d+$') {
    throw "HttpChunkSize must be Disabled or an integer byte value generated by the GUI."
}

if ($ConcurrentFragments -notin @(1, 2, 4, 8)) {
    throw "ConcurrentFragments must be 1, 2, 4, or 8."
}

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
if ($CookiesFile) {
    Write-Host "Cookies file:  $CookiesFile"
}
else {
    Write-Host "Cookies file:  Disabled or not specified"
}
Write-Host "Case:          $CaseDir"

Write-Section "Version info"

& $YtDlpPath --version 2>&1 | ForEach-Object { Write-RunLog ([string]$_) }
& $DenoPath --version 2>&1 | ForEach-Object { Write-RunLog ([string]$_) }

if (-not [string]::IsNullOrWhiteSpace($FFmpegFolder)) {
    $ffmpegExe = Join-Path $FFmpegFolder "ffmpeg.exe"
    & $ffmpegExe -version 2>&1 | Select-Object -First 1 | ForEach-Object { Write-RunLog ([string]$_) }
}

Write-Section "Capture options"

$OptionLines = @(
    "Prefer MP4:             $PreferMp4",
    "Format strategy:        $FormatStrategy",
    "Metadata only:          $MetadataOnly",
    "Media only:             $MediaOnly",
    "Include playlist:       $IncludePlaylist",
    "Playlist items:         $PlaylistItemsClean",
    "Playlist order:         $PlaylistOrder",
    "Max playlist items:     $MaxPlaylistItems",
    "Break on existing:      $BreakOnExisting",
    "Skip playlist errors:   $SkipPlaylistAfterErrors",
    "Write metadata JSON:    $WriteInfoJson",
    "Write source link:      $WriteSourceLink",
    "Write description:      $WriteDescription",
    "Write thumbnail:        $WriteThumbnail",
    "Write subtitles:        $WriteSubs",
    "Write auto subtitles:   $WriteAutoSubs",
    "Write comments:         $WriteComments",
    "Embed metadata:         $EmbedMetadata",
    "Embed thumbnail:        $EmbedThumbnail",
    "Embed subtitles:        $EmbedSubs",
    "Embed chapters:         $EmbedChapters",
    "Embed info JSON:        $EmbedInfoJson",
    "Archive mode:           $ArchiveMode",
    "Universal archive:      $($UniversalArchiveActive)",
    "Universal archive file: $UniversalArchiveFile",
    "Date after:             $DateAfterClean",
    "Date before:            $DateBeforeClean",
    "Rate limit:             $RateLimit ($SleepBaselineSeconds-$SleepMaxSeconds sec between URLs; $SleepRequestSeconds sec yt-dlp request sleep)",
    "Download speed limit:   $DownloadSpeedLimitClean",
    "Retry behavior:         $RetryBehavior",
    "Throttled rate:         $ThrottledRateClean",
    "HTTP chunk size:        $HttpChunkSizeClean",
    "Concurrent fragments:   $ConcurrentFragments",
    "Keep partials:          $KeepPartials",
    "Max resolution:         $MaxResolution",
    "Save playlist metadata: $SavePlaylistMetadata",
    "Generate URL shortcuts: $GenerateUrlShortcuts",
    "Match keywords:         $MatchKeywords",
    "Reject keywords:        $RejectKeywords",
    "Failure handling:       $FailureHandling",
    "Impersonate target:     $ImpersonateTarget",
    "GUI display cache:      $GuiCacheMode",
    "File manifest:          $ManifestMode",
    "Proxy:                  $(Get-MaskedProxyUrl -Value $ProxyUrl)"
)

$OptionLines | ForEach-Object { Write-RunLog ([string]$_) }

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
Write-RunLog ("Output template: {0}" -f $OutputTemplateForYtDlp)

switch ($RetryBehavior) {
    "Light" {
        $RetryCount = "3"
        $FragmentRetryCount = "3"
        $RetrySleep = "exp=5:60"
    }
    "Aggressive" {
        $RetryCount = "10"
        $FragmentRetryCount = "10"
        $RetrySleep = "exp=10:300"
    }
    default {
        $RetryCount = "5"
        $FragmentRetryCount = "5"
        $RetrySleep = "exp=10:120"
    }
}

$CommonArgs = @(
    "--continue",
    "--restrict-filenames",
    "--trim-filenames", "180",

    "--js-runtimes", "deno:$DenoPath",

    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "--add-header", "Accept-Language: en-US,en;q=0.9",

    "--retries", $RetryCount,
    "--fragment-retries", $FragmentRetryCount,
    "--retry-sleep", $RetrySleep,

    "--paths", $MediaDir,

    "--output", $OutputTemplateForYtDlp,

    "--verbose"
)

if ($SleepRequestSeconds -gt 0) {
    $CommonArgs += @("--sleep-requests", "$SleepRequestSeconds")
}

if (-not [string]::IsNullOrWhiteSpace($ProxyUrl)) {
    $CommonArgs += @("--proxy", $ProxyUrl)
    Write-RunLog ("Proxy: {0}" -f (Get-MaskedProxyUrl -Value $ProxyUrl))
}
else {
    Write-RunLog "Proxy: disabled"
}

if ($FailureHandling -eq "Continue") {
    $CommonArgs += "--ignore-errors"
}

switch ($ArchiveMode) {
    "Use" {
        $CommonArgs += @("--download-archive", $ArchiveFileForYtDlp)
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
else {
    if ($PlaylistItemsClean) {
        $CommonArgs += @("--playlist-items", $PlaylistItemsClean)
    }

    switch ($PlaylistOrder) {
        "Reverse" {
            $CommonArgs += "--playlist-reverse"
        }
        "Random" {
            $CommonArgs += "--playlist-random"
        }
    }

    if ($MaxPlaylistItems -gt 0) {
        $CommonArgs += @("--max-downloads", "$MaxPlaylistItems")
    }

    if ($BreakOnExisting) {
        if ($ArchiveMode -eq "Use") {
            $CommonArgs += "--break-on-existing"
        }
        else {
            Write-RunWarning "Break on existing was requested but Archive Mode is not Use. The option was not passed because it requires an active download archive."
        }
    }

    if ($SkipPlaylistAfterErrors -gt 0) {
        $CommonArgs += @("--skip-playlist-after-errors", "$SkipPlaylistAfterErrors")
    }
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

if (-not $MediaOnly) {
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
}

if ($EmbedRequested) {
    if ($EmbedMetadata) {
        $CommonArgs += "--embed-metadata"
    }
    else {
        $CommonArgs += "--no-embed-metadata"
    }

    if ($EmbedThumbnail) {
        $CommonArgs += "--embed-thumbnail"
    }
    else {
        $CommonArgs += "--no-embed-thumbnail"
    }

    if ($EmbedSubs) {
        $CommonArgs += "--embed-subs"
    }
    else {
        $CommonArgs += "--no-embed-subs"
    }

    if ($EmbedChapters) {
        $CommonArgs += "--embed-chapters"
    }
    else {
        $CommonArgs += "--no-embed-chapters"
    }

    if ($EmbedInfoJson) {
        $CommonArgs += "--embed-info-json"
    }
    else {
        $CommonArgs += "--no-embed-info-json"
    }
}
else {
    $CommonArgs += @(
        "--no-embed-metadata",
        "--no-embed-thumbnail",
        "--no-embed-subs",
        "--no-embed-chapters",
        "--no-embed-info-json"
    )
}

$EffectiveFormatStrategy = $FormatStrategy
if ($PreferMp4 -and $EffectiveFormatStrategy -eq "Best") {
    $EffectiveFormatStrategy = "PreferMp4"
}

if (-not $MetadataOnly) {
    switch ($EffectiveFormatStrategy) {
        "PreferMp4" {
            if ($MaxResolution -ne "best") {
                $FormatSelector = "bv*[ext=mp4][height<=$MaxResolution]+ba[ext=m4a]/b[ext=mp4][height<=$MaxResolution]/bv*[height<=$MaxResolution]+ba/b[height<=$MaxResolution]/best[height<=$MaxResolution]/best"
            }
            else {
                $FormatSelector = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
            }
            $CommonArgs += @("--format", $FormatSelector, "--merge-output-format", "mp4")
        }
        "StrictMp4" {
            if ($MaxResolution -ne "best") {
                $FormatSelector = "bv*[ext=mp4][height<=$MaxResolution]+ba[ext=m4a]/b[ext=mp4][height<=$MaxResolution]"
            }
            else {
                $FormatSelector = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            }
            $CommonArgs += @("--format", $FormatSelector, "--merge-output-format", "mp4")
        }
        "AudioOnly" {
            $CommonArgs += @("--format", "bestaudio/best", "--extract-audio", "--audio-format", "m4a")
        }
        "LowBandwidth" {
            if ($MaxResolution -ne "best") {
                $FormatSelector = "worst[height<=$MaxResolution]/b[height<=$MaxResolution]/worst"
            }
            else {
                $FormatSelector = "worst/best"
            }
            $CommonArgs += @("--format", $FormatSelector)
        }
        default {
            if ($MaxResolution -ne "best") {
                $FormatSelector = "bv*[height<=$MaxResolution]+ba/b[height<=$MaxResolution]/best[height<=$MaxResolution]/best"
                $CommonArgs += @("--format", $FormatSelector)
            }
        }
    }
}


if ($DownloadSpeedLimitClean -ne "Disabled") {
    $CommonArgs += @("--limit-rate", $DownloadSpeedLimitClean)
}

if ($ThrottledRateClean -ne "Disabled") {
    $CommonArgs += @("--throttled-rate", $ThrottledRateClean)
}

if ($HttpChunkSizeClean -ne "Disabled") {
    $CommonArgs += @("--http-chunk-size", $HttpChunkSizeClean)
}

if ($ConcurrentFragments -gt 1) {
    $CommonArgs += @("--concurrent-fragments", "$ConcurrentFragments")
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

$RunStartTime = Get-Date
$GuiCacheWarnings = @()

function Invoke-GuiCacheGeneration {
    param(
        [Parameter(Mandatory = $true)]
        [datetime]$Since
    )

    if ($GuiCacheMode -eq "Off") {
        return @{
            ThumbnailOk = $true
            MediaInfoOk = $true
        }
    }

    $thumbnailOk = New-VideoThumbnailsForRecentCaptures -MediaRoot $MediaDir -ThumbnailRoot $GuiThumbnailDir -Since $Since -FFmpegExe $FFmpegForThumbnails
    $mediaInfoOk = New-MediaInfoForRecentCaptures -MediaRoot $MediaDir -MetadataRoot $GuiMetadataDir -Since $Since -FFprobeExe $FFprobeForMediaInfo

    if (-not $thumbnailOk) {
        $script:GuiCacheWarnings += "thumbnail"
    }

    if (-not $mediaInfoOk) {
        $script:GuiCacheWarnings += "metadata"
    }

    return @{
        ThumbnailOk = $thumbnailOk
        MediaInfoOk = $mediaInfoOk
    }
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
                Add-RunLogLine $line

                if ($UniversalArchiveActive) {
                    $skipArchiveId = Get-UniversalArchiveSkipArchiveIdFromLine -Line $line
                    if ($null -ne $skipArchiveId) {
                        Add-UniversalArchiveSkipRecord -Url $Url -ArchiveId $skipArchiveId -Message $line -UrlIndex ($i + 1) -UrlTotal $Urls.Count
                    }
                }
            }

        $YtDlpExitCode = $LASTEXITCODE
    }
    catch {
        $YtDlpExitCode = 1
        $msg = "ERROR capturing URL: $Url`r`n$($_.Exception.Message)"
        Write-Warning $msg
        Add-RunLogLine $msg
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    Sync-UniversalArchiveEntriesToCase

    $ThumbnailGenerationOk = $true
    $MediaInfoGenerationOk = $true

    if ($GuiCacheMode -eq "AfterEachUrl") {
        $cacheResult = Invoke-GuiCacheGeneration -Since $CaptureStartTime
        $ThumbnailGenerationOk = [bool]$cacheResult.ThumbnailOk
        $MediaInfoGenerationOk = [bool]$cacheResult.MediaInfoOk
    }

    if ($YtDlpExitCode -eq 0) {
        $cacheDetail = if ($GuiCacheMode -eq "Off") {
            "local-gui-cache=off"
        }
        elseif ($GuiCacheMode -eq "AfterRun") {
            "local-gui-cache=after-run"
        }
        elseif ($ThumbnailGenerationOk -and $MediaInfoGenerationOk) {
            "local-gui-cache=ok"
        }
        else {
            "local-gui-cache=warning; thumbnail=$ThumbnailGenerationOk; metadata=$MediaInfoGenerationOk"
        }

        $successDetail = if ($MediaOnly) { "exit=0; media-only; $cacheDetail" } else { "exit=0; $cacheDetail" }
        Add-GuiUrlRecord -Path $GlobalCapturedUrlsFile -Status "captured" -CaseName $SafeCaseName -Url $Url -Detail $successDetail
        Write-Host ("GUI_QUEUE_URL_COMPLETE`t{0}`t{1}`t{2}" -f ($i + 1), $Urls.Count, $Url)
    }
    else {
        $failureDetail = "exit=$YtDlpExitCode"
        Add-GuiUrlRecord -Path $GlobalFailedUrlsFile -Status "failed" -CaseName $SafeCaseName -Url $Url -Detail $failureDetail
        Write-Host ("GUI_QUEUE_URL_INCOMPLETE`t{0}`t{1}`t{2}" -f ($i + 1), $Urls.Count, $Url)
    }

    if ($YtDlpExitCode -ne 0) {
        $msg = "yt-dlp exited with code $YtDlpExitCode for URL: $Url"
        Write-Warning $msg
        Add-RunLogLine $msg

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

if ($GuiCacheMode -eq "AfterRun") {
    Write-Section "Preparing Case Browser display cache"
    $cacheResult = Invoke-GuiCacheGeneration -Since $RunStartTime
    if (-not $cacheResult.ThumbnailOk -or -not $cacheResult.MediaInfoOk) {
        Write-RunWarning "Case Browser display cache completed with warnings. Capture success is based on yt-dlp results."
    }
}
elseif ($GuiCacheMode -eq "Off") {
    Write-Section "Preparing Case Browser display cache"
    Write-RunLog "Case Browser display cache generation is off for this run."
}

if ($UniversalArchiveActive) {
    Write-Section "Synchronizing universal download archive"
    Sync-UniversalArchiveEntriesToCase

    Write-RunLog "Universal archive file: $UniversalArchiveFile"
    Write-RunLog "Case archive entries seeded into universal archive before run: $script:UniversalArchiveSeededFromCase"
    Write-RunLog "New archive entries detected this run: $script:UniversalArchiveNewEntriesThisRun"
    Write-RunLog "New entries appended to case archive: $script:UniversalArchiveCaseEntriesAddedThisRun"

    Write-UniversalArchiveSkipSummary
}

Write-Section "Hashing captured files"

$manifestSince = if ($ManifestMode -eq "RunOnly") { $RunStartTime } else { [datetime]::MinValue }
$manifestEncoding = New-Object System.Text.UTF8Encoding($false)
$manifestWriter = New-Object System.IO.StreamWriter($HashManifest, $false, $manifestEncoding)
try {
    $manifestWriter.WriteLine('"Algorithm","Hash","Path"')

    foreach ($file in Get-ChildItem -LiteralPath $CaseDir -Recurse -File -ErrorAction SilentlyContinue) {
        if ($file.FullName -eq $HashManifest) {
            continue
        }

        if ($file.FullName -like "*\.gui-cache\*") {
            continue
        }

        if ($file.FullName -like "*\manifests\*") {
            continue
        }

        if ($file.LastWriteTime -lt $manifestSince) {
            continue
        }

        try {
            $hash = Get-Sha256HashCompat -Path $file.FullName
            $safePath = $file.FullName -replace '"', '""'
            $manifestWriter.WriteLine(('"SHA256","{0}","{1}"' -f $hash, $safePath))
        }
        catch {
            Write-RunWarning "Could not hash file for manifest: $($file.FullName) - $($_.Exception.Message)"
        }
    }
}
finally {
    $manifestWriter.Dispose()
}

Write-RunLog "Hash manifest written to: $HashManifest"

Write-Section "Done"

Write-RunLog "Case folder:      $CaseDir"
Write-RunLog "Run log:          $RunLog"
Write-RunLog "Download archive: $ArchiveFile"
Write-RunLog "Universal archive: $UniversalArchiveFile"
Write-RunLog "Failed URLs:      $GlobalFailedUrlsFile"
Write-RunLog "Captured URLs:    $GlobalCapturedUrlsFile"
Write-RunLog "SHA256 manifest:  $HashManifest"
Close-RunLogWriter
