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
  - [URL Preview Tab](#url-preview-tab)
  - [Case Browser Tab](#case-browser-tab)
- [Advanced Usage](#advanced-usage)
  - [Capture Tab: Case Names and URL Sources](#capture-tab-case-names-and-url-sources)
  - [Capture Tab: Capture, Metadata, Pacing, and Advanced Options](#capture-tab-capture-metadata-pacing-and-advanced-options)
  - [Capture Tab: Domain Presets and Proxy Options](#capture-tab-domain-presets-and-proxy-options)
  - [Job Queue Tab: Queue Management](#job-queue-tab-queue-management)
  - [URL Preview Tab: Metadata, Thumbnails, and Queueing](#url-preview-tab-metadata-thumbnails-and-queueing)
  - [Case Browser Tab: Review and Verification](#case-browser-tab-review-and-verification)
  - [App Update Checks](#app-update-checks)
- [Profiles and Settings](#profiles-and-settings)
- [Cookies Handling](#cookies-handling)
- [Limitations](#limitations)
- [Changelog](#changelog)

## Overview

`yt-dlp GUI for OSINT` is a portable Windows interface for running a consistent local capture workflow with `yt-dlp` and a companion PowerShell script.

The app is intentionally narrow in scope. It helps prepare URL lists, run captures, queue work, preview URL metadata and playlist/context entries, optionally cache preview thumbnails, and review case output. It does not bundle tools, automatically install dependencies, make authorization decisions, bypass security controls, or analyze evidence.

The current workflow uses four tabs:

- **Capture**: capture setup, URL/input handling, options, preflight, and direct capture
- **Job Queue**: staged jobs, checked-job starts, persistence, interruption recovery, and queue progress
- **URL Preview**: URL metadata preview, thumbnail preview, playlist/context item review, JSON export, and preview-derived start/queue actions
- **Case Browser**: local case review, file filtering/sorting, thumbnails/media details, and SHA256 verification

## Screenshots

<p align="center">
  <img src="/screenshots/main1.png" alt="capture tab" width="750">
</p>

<p align="center">
  <img src="/screenshots/main2.png" alt="job queue tab" width="750">
</p>

<p align="center">
  <img src="/screenshots/main3.png" alt="url preview tab" width="750">
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

- preparing pasted URLs or one or more Input File(s)
- running preflight checks for local tools and paths
- capturing media, metadata, sidecar artifacts, or embedded metadata
- applying playlist, case archive, optional universal archive, pacing, retry, format, keyword, and failure-handling options
- staging and running queue jobs
- previewing URL metadata, thumbnails, and playlist/context entries before capture
- starting, queueing, exporting, or applying filters from URL Preview results
- applying domain-based capture presets
- passing optional proxy settings to `yt-dlp`
- organizing output into case folders
- creating URL records and file manifests
- browsing and verifying captured case files

## What the App Does Not Do

The app is not a downloader bundle, browser automation system, security bypass, or evidence analysis platform.

Important limits:

- it does not bundle `yt-dlp`, FFmpeg/FFprobe, Deno, Python, or PowerShell, and it does not automatically install dependencies; user-triggered update helpers can update existing local yt-dlp or Deno executables
- it does not bypass EDR/AV, ASR, firewall, proxy, allow-listing, website restrictions, login requirements, paywalls, bot challenges, or rate limits
- it does not decide whether a capture is legal, policy-approved, proportionate, or in scope
- it does not collect passwords, automate sign-ins, solve challenges, or operate a browser for the user
- it does not guarantee support for any source platform
- it does not guarantee that URL Preview metadata, titles, thumbnails, uploader names, playlist relationships, or availability fields are complete, current, or authentic
- it does not guarantee thumbnail availability, even when a media URL itself is valid
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
- treat cookies, proxy settings, URL lists, case paths, download archives, URL Preview JSON exports, cached thumbnails, and preview metadata as sensitive operational data

## Required Components

The following components must be present or provided separately:

- Python 3 for the Tkinter GUI
- Windows PowerShell for `script.ps1`
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

### Recommended Workflow for Non-Technical Users

For normal captures, keep the defaults and use this simple flow:

1. Place the app in a local non-synced folder and run `gui.py`.
   - If needed, open a terminal in the app folder and run `python gui.py` or `py gui.py`.
   - To start from a clean app state, run `python gui.py --fresh`; this also clears the temporary Output Root `.gui-cache` folder.
2. Confirm paths for `script.ps1`, `yt-dlp.exe`, Output Root, and FFmpeg folder.
3. Paste URLs into the URL box, then confirm the Case Name and Output Root.
4. Run **Preflight Check**, then click **Start Capture**.
5. Use the Case Browser to review the completed case.

Only change advanced options, cookies, VPN checks, URL Preview settings, or archive settings when the investigation specifically requires them. Use the tabs below for capture, queueing, URL preview, and case review.

### Capture Tab

Use this tab to set up and start capture work.

Typical flow:

1. Set the Output Root.
2. Enter a case name or case-name template.
3. Paste URLs or select one or more Input File(s).
4. Set capture options only as needed.
5. Run **Preflight Check**.
6. Start the capture directly or add it to the Job Queue.

Notes:

- Cookies File use is disabled by default.
- Check VPN is disabled by default.
- If the URL box is empty, valid Input File(s) can silently populate it.
- If URL Box Persistence is enabled, saved URL box text loads first on startup.
- Existing-case warnings only appear when the resolved case folder contains meaningful non-cache files; preview-only `.gui-cache` folders are ignored.

### Job Queue Tab

Use this tab when captures should be staged, split, resumed, or run in batches.

Typical flow:

1. Add work from the Capture tab or URL Preview tab.
2. Check the jobs to run.
3. Start checked jobs or run the full queue.
4. Review status, failures, interruptions, and completed work.

Queued jobs keep their own capture settings. App-level settings such as Proxy Options and Universal Download Archive are evaluated when the job runs.

### URL Preview Tab

Use this tab to inspect URLs before capture. It supports regular URLs and playlist, channel, or context-style URLs.

Typical flow:

1. Let the tab load URLs from the current URL box or selected Input File(s).
2. Use the **Preview** checkmarks to choose which URLs should be queried by **Preview Checked**.
3. Use the **Include** checkmarks to choose which rows should be used by **Start Included** or **Queue Included**.
4. Use **Preview All**, **Start All**, or **Queue All** when every top-level URL row should be acted on regardless of checkmarks. When the URL filter contains text, these buttons change to **Preview Visible**, **Start Visible**, and **Queue Visible** and act only on currently visible rows.
5. Select a previewed regular URL to review its thumbnail and metadata.
6. Select a playlist/context URL to review its thumbnail/metadata and its available item rows. Once playlist/context data is confirmed, top-level Start/Queue actions use those item URLs instead of only the source playlist URL.
7. Right-click a highlighted URL row to preview, start, queue, open, copy, or export only that highlighted row.
8. Start, queue, export, copy, or apply playlist-item filters as needed.

Previewing makes source requests through `yt-dlp` but does not download media. Thumbnail modes may create cached thumbnail files.

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
- `%playlist%` for URL Preview playlist/context captures and queue jobs

The `%playlist%` tag resolves from the URL Preview playlist/context title when playlist or context metadata is available. When URL Preview starts or queues a playlist/context source, the app automatically appends `%playlist%` to the case-name template for that run or queued job if the template does not already include it.

The default case name is `Case-%datetime%`.

The URL box supports pasted URLs and one or more Input File(s). Multiple Input File(s) are stored as a semicolon-separated list.

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

Archive behavior:

- **Use case download archive** uses the resolved case folder's `download-archive.txt` by default and passes archive tracking to yt-dlp.
- **Ignore archive for this run** does not use download archive history but still avoids overwriting exact existing files.
- **Force re-capture** requests overwrite/re-capture behavior.
- **Universal Download Archive** is an optional app-level Settings menu feature. It applies only when Archive Mode is **Use**.
- When Universal Download Archive is enabled, yt-dlp uses `universal-download-archive.txt` for skip/write behavior while the current case archive is still maintained.
- Items skipped because they already exist in the universal archive are logged during capture and summarized under the case `manifests` folder as JSON/CSV. Direct capture and queue summaries also show those skips when applicable.
- **Stop when archived item is found** uses the active archive. With Universal Download Archive enabled, it can stop on entries captured in earlier cases.

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

URL Preview queue actions pass playlist/context titles into queued jobs when metadata is available. Top-level URL Preview queue actions create one queued job per top-level row being queued. If that row has confirmed playlist/context metadata with extracted item URLs, the queued job contains those playlist/context item URLs under the playlist-tagged case name instead of only the source playlist URL. **Queue All** queues all usable top-level rows. **Queue Included** queues rows with Include checked. Playlist/context item queue actions remain grouped into one queued job for the selected playlist/context and use a single `%playlist%` value.

### URL Preview Tab: Metadata, Thumbnails, and Queueing

The tab silently parses current URL sources so the top URL list is ready when selected. The URL box takes priority; if it is empty, selected Input File(s) are used.

URL Preview uses a top-level URL list and a context-sensitive lower panel. The top list has separate checkmarks:

- **Preview** controls which rows are queried by **Preview Checked**.
- **Include** controls which rows are used by **Start Included** and **Queue Included**.
- **All** actions act on all usable top-level rows regardless of checkmark state. When the top URL filter contains text, these buttons change from **All** to **Visible** and act only on rows currently shown by the filter. Clearing the filter restores the whole list and the original **All** labels.

Top-level actions include **Preview All** / **Preview Visible**, **Preview Checked**, **Start All** / **Start Visible**, **Start Included**, **Queue All** / **Queue Visible**, **Queue Included**, **Stop**, and **Export JSON**. Right-click a highlighted row to preview, start, queue, open, copy, or export only that row.

When a previewed playlist/channel/context row has extracted item URLs, Start and Queue actions use those item URLs instead of only the source playlist URL. Top-level queue actions create one job per top-level row. Playlist/context item actions group included item URLs into one playlist-tagged job.

The top URL list has a text filter that searches visible row fields such as status, type, title, uploader, thumbnail status, and URL. The filter count shows how many URL rows are currently shown out of the loaded total. The lower **Selected URL Context** area changes based on selection:

- regular URLs show **Thumbnail** and **Metadata** tabs
- playlist/channel/context rows show those tabs plus a playlist/context item list
- selecting a playlist/context item updates the Thumbnail and Metadata tabs for that item

The playlist/context item list also has a text filter for its visible item fields and shows how many item rows are currently shown out of the loaded total. Playlist/context item actions include **Start All Items** / **Start Visible Items**, **Start Included Items**, **Queue All Items** / **Queue Visible Items**, **Queue Included Items**, **Copy Included URLs**, **Load Included URLs**, **Append Included URLs**, **Set Playlist Items**, **Include All**, and **Exclude All**. The All/Visible item actions ignore item checkmarks; Included item actions use the item **Include** checkmarks. Clearing the item filter restores the whole item list and the original **All Items** labels. Right-click a highlighted item for single-item actions.

**Load Included URLs** replaces the URL box with individual included playlist/context item URLs. **Append Included URLs** appends them to the existing URL box. **Set Playlist Items** keeps the original playlist workflow and writes included item indexes into Capture tab playlist item filtering.

The collapsible **Preview Options** panel opens from the bottom-left of the URL Preview tab. It includes preview pacing, thumbnail mode, thumbnail rate limiting, cache mode, playlist mode, max items, timeout seconds, and a cache-only **Clear URL Preview Cache** action.

Preview pacing adds delay and jitter between preview metadata requests. The app warns before querying more than 10 preview URLs and stops when output suggests rate limiting, bot challenges, or temporary blocking.

Thumbnail fetching is best-effort and may fail even when the media URL is valid. **Rate limit thumbnails** uses post-fetch cooldowns and shows a counter in the Thumbnail tab when active. Changing selection updates the active thumbnail target without queueing multiple thumbnail requests.

URL Preview cache has two modes:

- **Temporary**: stores preview cache under the resolved case folder. If the final case folder is not known yet, temporary files are staged under `<OutputRoot>\.gui-cache` and cleared after they are copied into the resolved case cache.
- **Reuse cached thumbnails**: stores reusable thumbnail cache under `<OutputRoot>\.gui-cache\url-preview-persistent`. This cache is outside case files and is cleared by `--fresh` or **Clear URL Preview Cache**.

URL Preview metadata depends on yt-dlp extractor behavior. Fast playlist scans may provide limited per-item metadata, while deep metadata mode can be slower and make more source requests.

### Case Browser Tab: Review and Verification

The Case Browser loads the selected Output Root in the background. Its status line shows how many files are currently displayed after the active file-type filter and text search. Case-level `.gui-cache` folders are rebuildable GUI cache, not case evidence; they are hidden from Case Browser listings and excluded from verification/manifests. Folders that only contain GUI cache, such as preview-only folders with `manifests\.gui-cache`, are not shown as cases. Output Root `.gui-cache` is temporary and cleared by `--fresh`.

It supports:

- folder tree navigation
- current-folder-only view
- file-type filters
- text search across loaded file names, relative paths, file types, and inferred domain fields
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

Deno updates can be started from **Tools > Update Deno**, which runs `deno upgrade` against the detected local Deno executable. The app warns first because newer Deno builds may be incompatible or blocked by endpoint controls. Deno should still be staged beside `yt-dlp.exe` for this portable workflow; script-level PATH fallback is best-effort only.

## Profiles and Settings

The app stores settings, profiles, domain presets, and app-level settings in `gui-settings.json` beside the app.

The **Default** profile is loaded on startup. Custom profiles can be created, loaded, saved, and deleted from the Profile menu.

Profile-level settings include capture paths, capture options, metadata options, pacing options, advanced options, URL/input settings, selected VPN adapter, and URL Preview settings.

Profile-level URL Preview settings include:

- preview pacing
- thumbnail mode
- thumbnail rate limiting
- URL Preview cache mode
- playlist mode
- max playlist items
- preview timeout

App-level settings include Delete Cookies on Exit, Check VPN, Dark Mode, Job Persistence, URL Box Persistence, Universal Download Archive, Case Browser preferences, and Proxy Options. Universal Download Archive applies only when Archive Mode is **Use**.

Other app-root state files:

- `gui-jobs.json` for persisted queue jobs
- `gui-url-box.txt` for URL Box Persistence, when enabled
- `universal-download-archive.txt` for the app-level universal download archive, when enabled and used

`python gui.py --fresh` deletes `gui-settings.json`, `gui-jobs.json`, `gui-url-box.txt`, `universal-download-archive.txt`, app-level captured/failed URL history files, and the temporary Output Root `.gui-cache` folder. It does not delete case folders, case-level `.gui-cache` folders, media files, cookies, binaries, or scripts.

## Cookies Handling

Cookies File use is disabled by default.

Cookie-related notes:

- cookies are not required for every capture or preview
- cookies are sensitive operational data
- URL Preview metadata requests can use the selected Cookies File when Cookies File use is enabled
- Reliable thumbnail fallback through yt-dlp can also benefit from the same cookie/session context
- cookie use does not guarantee access to private, authenticated, restricted, or challenge-protected content
- exported cookies can optionally be applied to the main Cookies File field
- local cookie encrypt/decrypt helpers are available
- Delete Cookies on Exit can remove the selected cookies file when the app closes

The app does not automate website logins or collect credentials.

## Limitations

- Site support depends on the installed `yt-dlp` build and the source platform.
- URL Preview depends on the installed `yt-dlp` build and source extractor behavior. Fast scans may return limited metadata, while deep scans and reliable thumbnail mode can be slower and make more source requests.
- Thumbnail fetching is best-effort and may fail even when the media URL is valid.
- Large playlists and very large cases can take time to preview, render, cache, export, capture, scan, or verify.
- Universal Download Archive skip behavior applies only when the setting is enabled and Archive Mode is **Use**. It is an app-level history file, not a case evidence artifact. When enabled, archive-based skipping and Stop when archived item is found can reflect captures from other cases. Universal archive skips are logged and summarized, but the app does not yet maintain a universal capture index or copy prior case media into new cases.
- Browser impersonation targets depend on the installed `yt-dlp` build.
- Proxy and VPN behavior depends on local policy and routing.
- Case Browser thumbnails and media details require FFmpeg/FFprobe.
- Manifest verification checks file hashes only; it does not assess content authenticity or legal sufficiency.
- The app is not a replacement for authorization, evidence-handling policy, or analyst judgment.

## Changelog

### v0.2026.0623 - URL Preview Filters and Case Browser Polish

- Added in-memory filters for URL Preview URL rows, playlist/context item rows, and Case Browser file cards, with visible-row counts and clearer empty-state/status messages.
- Added context-sensitive URL Preview actions that switch from **All** to **Visible** when filters are active and apply only to currently visible rows.
- Improved case-folder handling so cache-only preview folders do not appear as captured cases or trigger existing-case warnings.
- Added a URL Preview cache-clearing action for temporary and reusable preview caches.

### v0.2026.0621 - URL Preview, Universal Archive, and Cache Handling

- Replaced **Playlist Preview** with a broader **URL Preview** workflow for metadata preview, thumbnail preview, playlist/context item review, JSON export, and preview-derived start/queue actions.
- Added profile-level URL Preview options for preview pacing, thumbnail mode, thumbnail rate limiting, cache mode, playlist mode, max items, and preview timeout.
- Added playlist-aware URL Preview start/queue behavior, including expansion of confirmed playlist/context rows to extracted item URLs and `%playlist%` case-name support.
- Added optional **Universal Download Archive** skip logging and per-run skip summaries for direct captures and queued jobs.
- Added temporary and reusable URL Preview thumbnail cache modes, with Output Root `.gui-cache` treated as temporary and cleared by `--fresh`.
- Improved cache handling so case-level `.gui-cache` folders are hidden from Case Browser and excluded from verification/manifests.

### v0.2026.0616 - Playlist Preview, URL Persistence, and Case Browser Polish

- Added the **Playlist Preview** tab with manual checked/selected preview scans, request pacing, rate-limit/backoff warnings, playlist/item checkmarks, playlist-split queueing, JSON export, and context menus.
- Added `%playlist%` case-name tag support and automatic playlist-title case naming for Playlist Preview queue jobs.
- Added app-level **URL Box Persistence**, silent Input File auto-population when the URL box is empty, and `--fresh` cleanup for persisted URL-box state.
- Changed default app startup behavior so **Check VPN** and **Use Cookies File** are disabled by default.
- Improved the **Case Browser** with better filename wrapping and dynamic file-card columns that reflow with available pane width.
- Refreshed README usage sections around the four main tabs while keeping prior changelog entries intact.

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
