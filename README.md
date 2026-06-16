# yt-dlp GUI for OSINT

A lightweight, portable Windows GUI for running an approved yt-dlp capture workflow in an organizational environment.

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Intended Users](#intended-users)
- [What the App Does](#what-the-app-does)
- [What the App Does Not Do](#what-the-app-does-not-do)
- [Organizational Compatibility](#organizational-compatibility)
- [Required Components](#required-components)
- [Basic Usage](#basic-usage)
  - [Capture Tab](#capture-tab)
  - [Job Queue Tab](#job-queue-tab)
  - [Playlist Preview Tab](#playlist-preview-tab)
  - [Case Browser Tab](#case-browser-tab)
- [Advanced Usage](#advanced-usage)
  - [Capture Tab: Case Names and URL Sources](#capture-tab-case-names-and-url-sources)
  - [Capture Tab: Capture, Metadata, Pacing, and Advanced Options](#capture-tab-capture-metadata-pacing-and-advanced-options)
  - [Capture Tab: Domain Presets and Proxy Options](#capture-tab-domain-presets-and-proxy-options)
  - [Job Queue Tab: Queue Management](#job-queue-tab-queue-management)
  - [Playlist Preview Tab: Playlist Review and Queueing](#playlist-preview-tab-playlist-review-and-queueing)
  - [Case Browser Tab: Review and Verification](#case-browser-tab-review-and-verification)
  - [App Update Checks](#app-update-checks)
- [Profiles and Settings](#profiles-and-settings)
- [Cookies Handling](#cookies-handling)
- [Limitations](#limitations)
- [Changelog](#changelog)

## Overview

`yt-dlp GUI for OSINT` is a portable Windows interface for running a consistent local capture workflow with `yt-dlp` and a companion PowerShell script.

The app is intentionally narrow in scope. It helps prepare URL lists, run captures, queue work, preview playlists, and review case output. It does not install tools, make authorization decisions, bypass security controls, or analyze evidence.

The current workflow uses four tabs:

- **Capture**: capture setup, URL/input handling, options, preflight, and direct capture
- **Job Queue**: staged jobs, checked-job starts, persistence, interruption recovery, and queue progress
- **Playlist Preview**: playlist source checks, playlist item review, preview pacing, and playlist-derived queue jobs
- **Case Browser**: local case review, file filtering/sorting, thumbnails/media details, and SHA256 verification

## Screenshots

<p align="center">
  <img src="/screenshots/main1.png" alt="capture tab" width="750">
</p>

<p align="center">
  <img src="/screenshots/main2.png" alt="job queue tab" width="750">
</p>

<p align="center">
  <img src="/screenshots/main3.png" alt="playlist preview tab" width="750">
</p>

<p align="center">
  <img src="/screenshots/main4.png" alt="case browser tab" width="750">
</p>

## Intended Users

This app is intended for investigators, analysts, or support staff who need a repeatable way to collect media or metadata with `yt-dlp` without rebuilding command-line arguments for every case.

It is designed for internal use in managed environments where binaries, scripts, proxy/VPN use, cookies, storage paths, and capture authority are reviewed separately through normal organizational processes.

## What the App Does

The app helps run a repeatable local capture workflow around approved tools.

Key capabilities include:

- preparing pasted URLs or one or more Input Files
- running preflight checks for local tools and paths
- capturing media, metadata, sidecar artifacts, or embedded metadata
- applying playlist, archive, pacing, retry, format, keyword, and failure-handling options
- staging and running queue jobs
- previewing playlists before capture
- applying domain-based capture presets
- passing optional proxy settings to `yt-dlp`
- organizing output into case folders
- creating URL records and file manifests
- browsing and verifying captured case files

## What the App Does Not Do

The app is not a downloader bundle, browser automation system, security bypass, or evidence analysis platform.

Important limits:

- it does not include or install `yt-dlp`, FFmpeg/FFprobe, Deno, Python, or PowerShell
- it does not bypass EDR/AV, ASR, firewall, proxy, allow-listing, website restrictions, login requirements, paywalls, or rate limits
- it does not decide whether a capture is legal, policy-approved, proportionate, or in scope
- it does not collect passwords, automate sign-ins, solve challenges, or operate a browser for the user
- it does not guarantee support for any source platform
- it does not make proxy/VPN traffic anonymous or invisible to endpoint, network, or administrative controls
- it does not identify people, assess authenticity, classify evidence, summarize media, or determine evidentiary value
- it does not upload, sync, retain, or archive cases to external services

## Organizational Compatibility

This app is designed for managed Windows environments.

Recommended assumptions:

- keep the app folder and Output Root in local non-synced storage
- stage approved builds of `yt-dlp`, FFmpeg/FFprobe, Deno, and Python separately
- expect endpoint protection to inspect or block newly introduced binaries until approved
- keep case folders local during capture, then move or archive through approved processes
- treat cookies, proxy settings, URL lists, and case paths as sensitive operational data

## Required Components

The following components must be present or provided separately:

- Python
- PowerShell
- the Python GUI script, `gui.py`
- the PowerShell capture script, `script.ps1`
- `yt-dlp.exe`
- `ffmpeg.exe`
- `ffprobe.exe`
- `deno.exe`

The GUI script and PowerShell script should stay together in the same portable app folder unless the paths are intentionally changed in the GUI.

Place `deno.exe` in the same folder as `yt-dlp.exe`. From source repos/build packages, keep only the binaries required by this app: `yt-dlp.exe`, `deno.exe`, `ffmpeg.exe`, and `ffprobe.exe`.

Windows includes Windows PowerShell, which is sufficient for `script.ps1`; PowerShell 7 is not required.

Recommended source pages:

- Python downloads: <https://www.python.org/downloads/windows/>
- Microsoft Store - Python: <https://apps.microsoft.com/detail/9PNRBTZXMB4Z>
- Microsoft Store - Python Install Manager: <https://apps.microsoft.com/detail/9NQ7512CXL7T>
- yt-dlp releases: <https://github.com/yt-dlp/yt-dlp/releases>
- yt-dlp nightly builds: <https://github.com/yt-dlp/yt-dlp-nightly-builds/releases>
- Deno releases: <https://github.com/denoland/deno/releases>
- FFmpeg Windows builds by Gyan.dev: <https://www.gyan.dev/ffmpeg/builds/>

Use official releases whenever possible. For FFmpeg, the Gyan.dev **release essentials** build is usually sufficient because it includes `ffmpeg.exe` and `ffprobe.exe`.

## Basic Usage

1. Place the app in a local non-synced folder.
2. Run `gui.py`.
   - If needed, open a terminal in the app folder and run `python gui.py` or `py gui.py`.
   - To start from a clean app state, run `python gui.py --fresh`.
3. Confirm paths for `script.ps1`, `yt-dlp.exe`, Output Root, and FFmpeg folder.
4. Use the tabs below for capture, queueing, playlist review, and case review.

### Capture Tab

Use this tab to set up and start capture work.

Typical flow:

1. Set the Output Root.
2. Enter a case name or case-name template.
3. Paste URLs or select one or more Input Files.
4. Set capture options only as needed.
5. Run **Preflight Check**.
6. Start the capture directly or add it to the Job Queue.

Notes:

- Cookies File use is disabled by default.
- Check VPN is disabled by default.
- If the URL box is empty, valid Input Files can silently populate it.
- If URL Box Persistence is enabled, saved URL box text loads first on startup.

### Job Queue Tab

Use this tab when captures should be staged, split, resumed, or run in batches.

Typical flow:

1. Add work from the Capture tab or Playlist Preview tab.
2. Check the jobs to run.
3. Start selected jobs or run the full queue.
4. Review status, failures, interruptions, and completed work.

Queued jobs keep their own capture settings. App-level proxy settings are evaluated when the job runs.

### Playlist Preview Tab

Use this tab to inspect playlist-like URLs before capture.

Typical flow:

1. Let the tab load URLs from the current URL box or selected Input Files.
2. Check URL rows and start a preview scan.
3. Review detected playlists and item rows.
4. Queue checked playlists or checked items as needed.

Previewing makes source requests through `yt-dlp` but does not download media.

### Case Browser Tab

Use this tab to review local case output.

Typical flow:

1. Select a case folder or subfolder.
2. Filter or sort files as needed.
3. Open files or related artifacts from file cards.
4. Verify case files against the latest SHA256 manifest when needed.

File-card columns automatically reflow based on the available pane width and selected icon scale.

## Advanced Usage

### Capture Tab: Case Names and URL Sources

Case names can use tags from the **Insert Tag** menu. Tags resolve when a capture starts or when a job is queued.

Useful tags include:

- date/time tags
- URL-domain tags
- preset-related tags
- `%playlist%` for Playlist Preview queue jobs

The default case name is `Case-%datetime%`.

The URL box supports pasted URLs and one or more Input Files. Multiple Input Files are stored as a semicolon-separated list.

URL box helpers can normalize, validate, deduplicate, group, summarize, copy, save, or clear URL text. Failed and captured URL tools use app-level URL history files under the Output Root.

### Capture Tab: Capture, Metadata, Pacing, and Advanced Options

Capture options are split into four panels:

- **Capture Options**: capture mode, source scope, playlist behavior, format, archive behavior, date filters, and Output Records
- **Metadata Options**: sidecar artifacts and embedded metadata
- **Pacing Options**: request delay, retries, throttling behavior, HTTP chunk size, speed limits, and fragment concurrency
- **Advanced Options**: browser impersonation, failure behavior, concurrent queue captures, keyword filters, and partial-file handling

Capture modes:

- **Media + sidecars**: media plus selected sidecar files
- **Media + embedded metadata**: media plus selected embedded metadata, without sidecar artifact files
- **Media only**: media without sidecars or embeds
- **Metadata/artifacts only**: supported artifacts without media download

Output Records controls Case Browser cache timing and file manifest scope.

### Capture Tab: Domain Presets and Proxy Options

Domain Presets save capture-option combinations for one or more domains. Matching active presets can apply automatically, with higher-priority presets overriding lower-priority matches.

Proxy Options are app-level. Supported protocol choices are **None**, `http`, `https`, `socks4`, and `socks5`.

Proxy settings can include credentials. If saved, they are stored unencrypted in `gui-settings.json`. Enable the session-only option when proxy details should not be saved.

### Job Queue Tab: Queue Management

The queue supports:

- checked-job starts
- full-queue starts
- split-and-queue workflows
- interruption recovery
- clearing completed, failed, interrupted, or selected jobs
- persisted queue state in `gui-jobs.json`
- schema warnings for older queued jobs

Concurrent queue capture is available, with domain-collision checks to reduce accidental simultaneous captures against the same domain.

### Playlist Preview Tab: Playlist Review and Queueing

The tab silently parses current URL sources so the list is ready when selected.

The three lists use checkmarks:

- **URLs to Preview** controls which source URLs are queried
- **Playlists Found** controls playlist-level copy and queue actions
- **Playlist Items** controls item-level copy, URL-box, split, queue, and playlist-item-range actions

Preview pacing presets add delay and jitter between preview requests. The app warns before querying more than 10 preview URLs and stops when output suggests rate limiting, bot challenges, or temporary blocking.

Playlist Preview queue actions automatically append `%playlist%` to the queued case template when the template does not already include it.

### Case Browser Tab: Review and Verification

The Case Browser loads the selected Output Root in the background.

It supports:

- folder tree navigation
- current-folder-only view
- file-type filters
- sorting by name, domain, type, size, newest, or oldest
- dynamic file-card columns
- icon scale options
- right-click file actions
- FFmpeg thumbnails in `.gui-cache\thumbnails`
- FFprobe media details in `.gui-cache\metadata`
- SHA256 manifest verification

Verification applies to a selected case folder or subfolder. The Output Root itself cannot be verified. `.gui-cache` and `manifests` are excluded from verification scope.

### App Update Checks

The app update checker opens the latest app release page for manual download. It does not download, extract, replace, or run app files.

yt-dlp updates are separate from normal capture runs and use the selected local `yt-dlp.exe`.

Deno updates can be started from **Tools > Update Deno**, which runs `deno upgrade` against the detected local Deno executable. The app warns first because newer Deno builds may be incompatible or blocked by endpoint controls.

## Profiles and Settings

The app stores settings, profiles, domain presets, and app-level settings in `gui-settings.json` beside the app.

The **Default** profile is loaded on startup. Custom profiles can be created, loaded, saved, and deleted from the Profile menu.

Profile-level settings include capture paths, capture options, metadata options, pacing options, advanced options, URL/input settings, and selected VPN adapter.

App-level settings include Delete Cookies on Exit, Check VPN, Dark Mode, Job Persistence, URL Box Persistence, Case Browser preferences, and Proxy Options.

Other app-root state files:

- `gui-jobs.json` for persisted queue jobs
- `gui-url-box.txt` for URL Box Persistence, when enabled

`python gui.py --fresh` deletes `gui-settings.json`, `gui-jobs.json`, `gui-url-box.txt`, and app-level captured/failed URL history files. It does not delete case folders, media files, cookies, binaries, or scripts.

## Cookies Handling

Cookies File use is disabled by default.

Cookie-related notes:

- cookies are not required for every capture
- cookies are sensitive operational data
- exported cookies can optionally be applied to the main Cookies File field
- local cookie encrypt/decrypt helpers are available
- Delete Cookies on Exit can remove the selected cookies file when the app closes

The app does not automate website logins or collect credentials.

## Limitations

- Site support depends on the installed `yt-dlp` build and the source platform.
- Browser impersonation targets depend on the installed `yt-dlp` build.
- Proxy and VPN behavior depends on local policy and routing.
- Case Browser thumbnails and media details require FFmpeg/FFprobe.
- Very large cases can take time to scan, render, cache, or verify.
- Manifest verification checks file hashes only; it does not assess content authenticity or legal sufficiency.
- The app is not a replacement for authorization, evidence-handling policy, or analyst judgment.

## Changelog

### v0.2026.0614 - Tabs, Presets, Proxy, and Output Records

- Added a bottom-tab workflow for **Capture**, **Job Queue**, and **Case Browser**, with Case Browser loading the selected Output Root in the background and supporting Domain sort.
- Expanded input and queue workflows with multiple Input Files, queue checkmarks, Start Selected, split-and-add-to-queue, persisted jobs, interrupted job handling, and clearer active preset visibility.
- Reworked Domain Presets so presets use names plus one or more match domains, support priority ordering, import conflict choices, and expose matching preset information in the queue.
- Added app-level Proxy Options with protocol/address/port/credential fields, optional session-only storage, script-side proxy validation, and masked proxy logging.
- Added Output Records controls for Case Browser cache timing and file manifest scope; script success now follows yt-dlp results while cache warnings remain non-fatal.
- Improved responsiveness and cleanup by moving Case Browser scans/cache work off the main UI path, chunking large Case Browser renders, deferring startup work, and removing stale hidden UI/menu code.

### v0.2026.0612 - Queue, URL Workflow, and Advanced Controls

- Added concurrent queue execution with domain-collision checks and queue-aware Start Capture behavior.
- Added failed/captured URL tracking, URL validation/statistics/grouping tools, and failed URL queueing.
- Added concurrent fragments, expanded request pacing options, and refined Advanced Options layout.
- Added Load versus Append URL behavior, duplicate removal, queue horizontal scrolling, and updated case name time tags.
- Reorganized README usage sections and expanded screenshot references.

### v0.2026.0611 - Job Queue and Summary Refinements

- Added a sequential Job Queue window with queued job controls, URL-based progress, completed-job summary copying, and non-active job clearing.
- Added a Start Capture split-menu action to add the current configuration to the queue.
- Changed queued jobs to run from snapshotted job settings without rewriting the visible main GUI fields.
- Changed the default case name template to `Case-%datetime%`.
- Updated URL box saving to always prompt with a Save As dialog.
- Refined case summaries and verification so manifest files are counted in summaries while `.gui-cache` and `manifests` remain outside verification scope.

### v0.2026.0529 - URL Controls, Cookie Scope, Download Limits, and Verification Scope

#### URL Box Workflow

- Added one-word URL box buttons for Load, Save, Clear, and Strip.
- Changed URL loading so input file contents append to the existing URL box instead of replacing it.
- Removed URL load, save, and clear commands from the File menu.
- Refined the optional Strip action to decode common HTML ampersands and remove parameter-like ampersand segments.

#### Cookies and Profiles

- Added a profile-level Use Cookies File setting.
- Added a Cookies File row checkbox that disables the path field and Browse button when cookies are not in use.
- Made preflight and capture skip cookies file validation and `-CookiesFile` passing when Use Cookies File is disabled.
- Changed browser cookie export to use `https://example.com/` as the generic reference URL.
- Removed the separate Load Default Profile command because Default is already available from the profile selection list.

#### Advanced Capture Controls

- Added an Advanced Options download speed limit control with disabled as the default.
- Added download speed presets including 500K, 1M, 2M, 5M, 10M, and 50M.
- Added custom download speed limit support for yt-dlp `--limit-rate` values.
- Changed yt-dlp nightly build querying from 30 releases to 20 releases.

#### PowerShell Capture Script

- Added PowerShell support for passing yt-dlp `--limit-rate` when a download speed limit is selected.
- Removed yt-dlp `--sleep-interval` and `--max-sleep-interval` while keeping `--sleep-requests` and the script-level pause between URLs.
- Added logging for whether a cookies file is provided or disabled.

#### Case Browser Verification

- Excluded `.gui-cache` and `manifests` from SHA256 manifest generation and verification scope.
- Updated case file verification to ignore `.gui-cache` and `manifests` paths, including older manifests that may reference cache files.
- Changed Verify Case Files so Output Root cannot be verified directly; users must select a case folder or one of its subfolders.

### v0.2026.0528 - Workflow Polish, Preflight Validation, and Case Browser Refinements

#### App Workflow and Update Checks

- Added Help menu entries for About and Check for Updates.
- Added GitHub latest-release lookup for app updates without downloading, extracting, replacing, or running files.
- Updated the app version to `v0.2026.0528`.

#### Case Naming and Case Safety

- Added case name templates with an Insert Tag menu and default `Case-%date%` naming.
- Added resolved case folder preview under the Case Name field.
- Added a warning before using an existing populated case folder.

#### Preflight and Logging

- Changed Preflight Check to append to the output log instead of clearing previous entries.
- Added preflight execution/version checks for yt-dlp, FFmpeg, FFprobe, and Deno.
- Updated the yt-dlp version status label when preflight confirms yt-dlp is runnable.
- Reduced unnecessary settings and Dark Mode log noise.

#### Case Browser Improvements

- Added Case Browser filter, sort, current-folder-only view, and icon scale preferences.
- Added horizontal scrolling and Small, Medium, and Large icon scale options.
- Added right-click actions for file cards, including open, open folder, open related metadata, open related source link, and copy path/name actions.
- Added case file verification against the latest SHA256 manifest.

#### Settings and Appearance

- Added settings schema migration with recognized-value import, default creation for newer settings, and preservation of unrecognized values.
- Added app-level Dark Mode using built-in Tk/ttk styling only.
- Added app-level Delete Settings File option with confirmation and reset behavior.
- Saved Case Browser preferences as app-level settings.

### v0.2026.0527 - Advanced Capture, App Settings, and Case Browser

#### Capture Options and Advanced Options

- Added archive mode controls for using the case download archive, ignoring the archive for a run, or forcing a re-capture.
- Added date filters for capture date after and date before values.
- Added max resolution presets.
- Added playlist metadata capture when playlist or multi-item capture is enabled.
- Added Windows URL shortcut generation.
- Added match and reject keyword filters with clear buttons.
- Added failure handling options to continue after failed URLs or stop on the first failed URL.
- Moved rate limit controls into the Advanced Options panel.
- Added keep partial files/fragments on failure.
- Preserved persistent settings and profile support for the new capture options.

#### PowerShell Capture Script Changes

- Added PowerShell handling for archive mode, date filters, max resolution, playlist metadata, URL shortcuts, keyword filters, failure handling, rate limits, and partial-file retention.
- Added FFmpeg-driven GUI thumbnail generation at the end of each URL capture, independent of the capture thumbnail checkbox.
- Added FFprobe-driven media information caching at the end of each URL capture.
- Fixed single-URL input handling so one pasted URL is treated as one URL instead of being indexed as individual characters.
- Continued keeping yt-dlp updating separate from the capture script.

#### Case Browser

- Added `Tools > Open Case Browser`.
- Added a separate case browser window with a folder tree for the selected Output Root.
- Added media and sidecar file cards for selected folders.
- Added double-click file opening from the case browser.
- Added an `Open Folder` button for the selected folder.
- Added single-click folder behavior that expands the selected tree item and shows its contents.
- Added FFmpeg-generated PNG thumbnails stored in `.gui-cache\thumbnails`.
- Added FFprobe-generated media metadata stored in `.gui-cache\metadata`.
- Added case browser card summaries and hover tooltips with media details such as duration, size, bitrate, codec, resolution, frame rate, audio channels, and sample rate.
- Added fallback placeholders when thumbnails or media information cannot be generated.

#### Settings and Profiles

- Added app-level `Delete Cookies on Exit` setting under the Settings menu.
- Added app-level `Check VPN` setting under the Settings menu.
- Made `Delete Cookies on Exit` and `Check VPN` save to the settings file but not to individual profiles.
- Made `Check VPN` show or hide the VPN Status section.
- Made Start Capture skip the VPN warning when `Check VPN` is disabled.
- Disabled VPN-related Tools menu actions when `Check VPN` is disabled.
- Changed custom profile saving so saving a custom profile no longer overwrites the Default profile.

#### Impersonate Target Handling

- Added `Show all targets` behavior for impersonate target discovery.
- Kept the main yt-dlp-supported browser choices visible: `chrome`, `edge`, and `firefox`.
- Added OS labels beside discovered impersonate targets when available.
- Filtered yt-dlp log/status lines such as `[info]` from the target list.
- Preserved Windows-focused target discovery as the default behavior.

### v0.2026.0526 - yt-dlp Update Workflow and Capture Options Foundation

#### yt-dlp Update Changes

- Removed yt-dlp updating from the normal capture workflow.
- Removed the previous update checkbox from the main GUI capture options.
- Added dedicated controls to check the current yt-dlp version and run updates on request.
- Added a Python-based update dialog that runs independently of the PowerShell script.
- Added update choices for latest stable, latest nightly, or a selected nightly build from GitHub.
- Added a warning that very recent nightlies may be blocked by ASR or endpoint protection.

#### Capture Options Foundation

- Replaced the always-visible `Prefer MP4` checkbox with a `Capture Options` button.
- Moved MP4 preference into the Capture Options panel.
- Added capture mode options for media capture or metadata/artifacts-only capture.
- Added source scope options for single-item capture or playlist/multi-item capture.
- Added sidecar artifact options for metadata JSON, source links, descriptions, thumbnails, subtitles, automatic subtitles, and comments.
- Added persistent settings and profile support for capture options.

#### PowerShell Capture Script Foundation

- Added support for GUI-driven capture options.
- Added switches for MP4 preference, metadata-only capture, playlist inclusion, metadata JSON, source links, descriptions, thumbnails, subtitles, automatic subtitles, and comments.
- Preserved single-item capture by default unless playlist or multi-item capture is explicitly selected.
- Added FFmpeg folder support through yt-dlp's FFmpeg location option.
- Kept yt-dlp updating separate from the PowerShell capture process.
