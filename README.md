# AVI Capture GUI for OSINT

A portable Windows GUI for approved audio/video/image capture workflows using `yt-dlp`, `gallery-dl`, and companion PowerShell scripts.

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Intended Users](#intended-users)
- [What the App Does](#what-the-app-does)
- [What the App Does Not Do](#what-the-app-does-not-do)
- [Required Components](#required-components)
- [Basic Usage](#basic-usage)
  - [Setup and Staging](#setup-and-staging)
  - [Start a Capture](#start-a-capture)
  - [Use the Job Queue](#use-the-job-queue)
  - [Resume Interrupted Captures](#resume-interrupted-captures)
  - [Preview Audio/Video Links](#preview-audiovideo-links)
  - [Review a Case](#review-a-case)
- [Advanced Usage](#advanced-usage)
  - [Portable Layout](#portable-layout)
  - [Audio/Video Capture](#audiovideo-capture)
  - [Image Capture](#image-capture)
  - [Job Queue, Persistence, and Recovery](#job-queue-persistence-and-recovery)
  - [Domain Presets, Proxy, VPN, and Archives](#domain-presets-proxy-vpn-and-archives)
  - [Update Checks](#update-checks)
- [Profiles and Settings](#profiles-and-settings)
- [Cookies Handling](#cookies-handling)
- [Limitations](#limitations)
- [Changelog](#changelog)

## Overview

`Audio/Video/Image Capture GUI for OSINT` (`AVI Capture GUI for OSINT`) is a local, portable interface for repeatable capture work in managed environments.

The app has five main tabs:

- **Audio/Video Capture** for `yt-dlp` captures.
- **Image Capture** for `gallery-dl` captures.
- **Job Queue** for staged, concurrent, and recoverable jobs.
- **Audio/Video Preview** for metadata, thumbnails, playlist/context review, and queueing from preview results.
- **Case Browser** for local review, thumbnails, metadata, and hash verification.

The app does not bundle capture tools or make authorization decisions. Tools, credentials, network paths, cookies, proxy/VPN use, and capture scope should be approved separately through normal organizational processes.

## Screenshots

<p align="center">
  <img src="/screenshots/main1.png" alt="audio/video capture tab" width="720">
</p>

<p align="center">
  <img src="/screenshots/main2.png" alt="image capture tab" width="720">
</p>

<p align="center">
  <img src="/screenshots/main3.png" alt="job queue tab" width="720">
</p>

<p align="center">
  <img src="/screenshots/main4.png" alt="audio/video preview tab" width="720">
</p>

<p align="center">
  <img src="/screenshots/main5.png" alt="case browser tab" width="720">
</p>

## Intended Users

This app is intended for investigators, analysts, and support staff who need a consistent way to collect approved audio/video, image, gallery, or metadata output without manually rebuilding command-line arguments for every case.

It is designed for local Windows use. Keep the app folder and case output on local storage during active captures, then move or archive cases through approved evidence-handling processes.

## What the App Does

The app helps users:

- prepare URL lists or input files
- run preflight checks for required local tools
- capture audio/video with `yt-dlp`
- capture image/gallery content with `gallery-dl`
- organize output into case folders
- apply case names, filename templates, cookies, proxy settings, pacing, archive, and metadata options
- queue multiple jobs and recover interrupted work when Job Persistence is enabled
- preview audio/video metadata and thumbnails before capture
- browse local case files and verify SHA256 manifests

## What the App Does Not Do

The app does not:

- include or auto-install `yt-dlp`, `gallery-dl`, FFmpeg/FFprobe, Deno, Python, or PowerShell
- bypass endpoint security, firewalls, website controls, access restrictions, login requirements, bot challenges, or rate limits
- decide whether a capture is legal, approved, proportionate, or in scope
- collect passwords, automate sign-ins, or solve interactive challenges
- guarantee that any source platform is supported
- analyze evidence, identify people, assess authenticity, or determine evidentiary value
- upload, sync, or retain cases outside the selected local output paths

## Required Components

Place the GUI, scripts, and approved tools in a local portable folder unless your organization uses a different staged path.

Required files/tools:

- `gui.py`
- `script-ytdlp.ps1`
- `script-gallerydl.ps1`
- `yt-dlp.exe`
- `gallery-dl.exe`
- `ffmpeg.exe`
- `ffprobe.exe`
- `deno.exe`
- Python 3 with Tkinter
- Windows PowerShell

`deno.exe` should be beside `yt-dlp.exe`. `gallery-dl.exe` can be beside the app or selected manually in the Image Capture tab. The app creates temporary handoff files under its own `gui-temp` folder and removes them after use.

Recommended source pages:

- AVI Capture GUI releases: <https://github.com/jmashuque/avi-capture-gui-for-osint/releases/latest>
- Python: <https://apps.microsoft.com/detail/9PNRBTZXMB4Z>
- yt-dlp releases: <https://github.com/yt-dlp/yt-dlp/releases>
- yt-dlp nightly builds: <https://github.com/yt-dlp/yt-dlp-nightly-builds/releases>
- gallery-dl releases: <https://codeberg.org/mikf/gallery-dl/releases>
- Deno releases: <https://github.com/denoland/deno/releases>
- FFmpeg Windows builds by Gyan.dev: <https://www.gyan.dev/ffmpeg/builds/>

Use approved releases for your environment. For FFmpeg, the Gyan.dev release essentials build is usually enough because it includes both `ffmpeg.exe` and `ffprobe.exe`.

## Basic Usage

This section is for normal users who only need to stage the app and run approved captures. Most users should not need to change Advanced Options.

### Setup and Staging

Do this once before the first capture, or whenever you are preparing a fresh copy of the app. Use organization-approved download locations or staged files when your environment provides them.

1. Create a local folder for the app, such as:

   ```text
   C:\AVI-Capture-GUI
   ```

2. Download the latest AVI Capture GUI release ZIP from:

   ```text
   https://github.com/jmashuque/avi-capture-gui-for-osint/releases/latest
   ```

3. Right-click the downloaded ZIP, choose **Properties**, select **Unblock** if that option appears, then choose **Extract All**. Do not run the app from inside the ZIP.

4. Move or extract the app files into the local app folder. The folder should contain at least:

   ```text
   gui.py
   script-ytdlp.ps1
   script-gallerydl.ps1
   README.md
   VERSION.txt
   VERIFY_HASHES.txt
   ```

5. Install Python 3 if it is not already installed. The easiest user-facing option is the Microsoft Store Python 3 package. If your organization uses Software Center, Company Portal, Intune, winget, or another approved source, use that instead.

6. Download the required capture tools and place the executable files in the same app folder unless your team gives you a different staged folder:

   | Tool | What to place in the app folder | Source page |
   |---|---|---|
   | yt-dlp | `yt-dlp.exe` | <https://github.com/yt-dlp/yt-dlp/releases> |
   | gallery-dl | `gallery-dl.exe` | <https://codeberg.org/mikf/gallery-dl/releases> |
   | Deno | `deno.exe` | <https://github.com/denoland/deno/releases> |
   | FFmpeg | `ffmpeg.exe` and `ffprobe.exe` | <https://www.gyan.dev/ffmpeg/builds/> |

   For FFmpeg, download a Windows release build, open the ZIP, then copy `ffmpeg.exe` and `ffprobe.exe` from the `bin` folder into the app folder.

7. Confirm the app folder now looks similar to this:

   ```text
   C:\AVI-Capture-GUI\
     gui.py
     script-ytdlp.ps1
     script-gallerydl.ps1
     yt-dlp.exe
     gallery-dl.exe
     deno.exe
     ffmpeg.exe
     ffprobe.exe
   ```

Keep this folder together. `deno.exe` should be beside `yt-dlp.exe`. Keep the app on a local drive during active captures instead of running it from inside the ZIP, email attachment, browser download preview, or network share.

### Start a Capture

1. Open the app folder in File Explorer.

2. Start the GUI. Use one of these methods:

   - If `.py` files already open with Python, double-click `gui.py`.
   - If double-clicking does not work, click the File Explorer address bar, type `powershell`, and press **Enter**. In the PowerShell window that opens, run:

     ```powershell
     py .\gui.py
     ```

   - If Windows says `py` is not recognized, try:

     ```powershell
     python .\gui.py
     ```

   - If both commands fail, Python is not installed or is not available to the user session. Install Python through an approved source or ask IT to stage it.

3. Choose the correct tab:

   - **Audio/Video Capture** for video, audio, and supported media posts handled by `yt-dlp`.
   - **Image Capture** for image links, galleries, albums, and supported photo-post sources handled by `gallery-dl`.

4. Confirm the tool paths shown on the tab. If a path is blank or points to the wrong folder, use the browse button beside that field.

5. Enter or keep the case name. The app resolves the final case folder before capture.

6. Paste approved URLs into the URL box, or select an input file containing one URL per line.

7. Run **Preflight Check**. Fix any missing tool or folder warning before starting the capture.

8. Click **Start Capture**.

9. Leave the app open until the capture finishes, then review the output log and case folder.

The URL box takes priority over input files. Clear the URL box if you want the selected input file to be used instead.

### Use the Job Queue

Use **Job Queue** when you want to prepare several captures before running them.

1. Add work from **Audio/Video Capture**, **Image Capture**, or **Audio/Video Preview**.
2. Review the queued jobs.
3. Start the full queue, checked jobs, or highlighted jobs from the right-click menu.
4. Leave the app open while the queue runs.
5. Review failed or interrupted jobs after the run.

The Job Queue is also where interrupted work is resumed when **Job Persistence** is enabled.

### Resume Interrupted Captures

If the app closes, crashes, or a capture is stopped while **Job Persistence** is enabled, reopen the app and go to **Job Queue**. The interrupted capture should appear with an **Interrupted** status.

To resume it:

1. Open **Job Queue**.
2. Select the interrupted job.
3. Use **Continue Checked Interrupted** or right-click the highlighted job and choose **Continue Highlighted Interrupted**.
4. Leave the app open while the resumed queue job runs.

Direct captures are also saved as running recovery jobs only when **Job Persistence** is enabled. If Job Persistence is disabled, direct captures are not saved to the queue and cannot be resumed from the app after a close or crash.

Audio/Video jobs continue from the first URL that was not fully marked complete. Image jobs resubmit the original URLs and rely on gallery-dl archive skipping to avoid repeating completed items.

### Preview Audio/Video Links

Use **Audio/Video Preview** when you want to inspect media metadata or playlist/context entries before capture.

1. Add URLs to the preview list.
2. Run Preview for all, selected, or visible rows.
3. Review metadata, thumbnails, and playlist/context items.
4. Start or queue the previewed rows you want to capture.

Preview is best-effort. It can be slower or incomplete depending on the site, cookies, network path, and installed `yt-dlp` build.

### Review a Case

Use **Case Browser** to review local case output.

- Select an Output Root.
- Filter or sort case files.
- Open case folders or individual files.
- Generate or verify SHA256 manifests.

Case Browser is for local review only. It does not determine evidentiary value.

## Advanced Usage

This section is for users who understand the tools, site behavior, rate limits, and organizational handling requirements.

### Portable Layout

Keep these files together unless paths are intentionally changed in the GUI:

```text
gui.py
script-ytdlp.ps1
script-gallerydl.ps1
yt-dlp.exe
gallery-dl.exe
deno.exe
ffmpeg.exe
ffprobe.exe
```

Recommended layout:

- keep the app folder local
- keep active Output Roots local and non-synced
- avoid running active captures from network shares
- treat cookies, URL lists, logs, archives, preview exports, and case metadata as sensitive operational data

### Audio/Video Capture

Audio/Video Capture uses `script-ytdlp.ps1` and `yt-dlp.exe`.

Useful advanced controls include:

- case-name and filename-template tags
- playlist/source-scope controls
- capture mode and format strategy
- sidecar and embedded metadata options
- rate limit, retry, throttling, HTTP chunk size, and concurrent fragments
- keyword filters and failure handling
- yt-dlp update checks and stable/nightly update targets

### Image Capture

Image Capture uses `script-gallerydl.ps1` and `gallery-dl.exe`.

Useful advanced controls include:

- image-specific case name and filename template
- media versus metadata-only mode
- case archive, ignore archive, or force re-capture modes
- max item and item-range limits
- metadata, info JSON, and tags sidecars
- pacing, retries, timeout, and Image Capture concurrent captures
- gallery-dl update checks and stable/dev update targets

The image filename template is relative to the case `media` folder. Case/context tags resolve when the job is created. gallery-dl item tags resolve per downloaded item.

### Job Queue, Persistence, and Recovery

The Job Queue runs staged work, manages concurrent captures, and resumes interrupted jobs. It supports both `yt-dlp` and `gallery-dl` jobs.

**Job Persistence** controls whether queue state is saved to `gui-jobs.json`. When it is enabled, queued jobs and direct captures are saved while they run. If a running job is still present when the app reopens, it is treated as interrupted and can be continued from the Job Queue. When Job Persistence is disabled, direct captures are not recoverable through the app after a close or crash.

Recovery behavior is engine-specific:

- **Audio/Video Capture (`yt-dlp`)** records completed URL markers. Continuing an interrupted job submits the first incomplete URL and anything after it.
- **Image Capture (`gallery-dl`)** uses archive-backed retry. Continuing an interrupted image job resubmits the original URLs and lets the case archive, or the image universal archive when enabled, skip completed items.

Concurrent queue behavior:

- Audio/Video and Image Capture have separate concurrent-capture limits.
- `yt-dlp` and `gallery-dl` jobs may run at the same time when their domains do not collide.
- Same-domain concurrent jobs trigger a collision prompt so users can continue, wait, or cancel.

Each recoverable job can write `manifests/gui-job-recovery-<job-id>.json` under the case folder. These files explain what the app tried to resume; they are not a replacement for the normal case manifest or review notes.

### Domain Presets, Proxy, VPN, and Archives

- **Domain Presets** can apply capture settings automatically to matching Audio/Video or Image Capture URLs.
- **Proxy Options** are app-level and can be passed to both capture scripts.
- **Check VPN** is disabled by default and warns before capture when enabled and the selected adapter does not look connected.
- **Universal Download Archive** uses separate app-level archive files:
  - `universal-download-archive.txt` for Audio/Video Capture
  - `universal-gallerydl-archive.sqlite3` for Image Capture

Universal archives are useful for avoiding repeat captures across cases, but they are not evidence artifacts for a specific case.

### Update Checks

The app has user-triggered update helpers for staged local tools:

- **Check/Update yt-dlp** on the Audio/Video Capture tab
- **Check/Update gallery-dl** on the Image Capture tab
- **Tools > Update Deno** for the detected local `deno.exe`

The app does not auto-update tools on launch. Updates should be used only when approved for the environment.

## Profiles and Settings

The app stores settings beside the app in `gui-settings.json`. **Job Persistence** should stay enabled if users need queue recovery or direct-capture recovery after a close or crash.

Common state files:

- `gui-settings.json` for settings, profiles, app settings, and domain presets
- `gui-jobs.json` for persisted queue jobs when Job Persistence is enabled
- `gui-url-box.txt` and `gui-image-url-box.txt` when URL Box Persistence is enabled
- `universal-download-archive.txt` and `universal-gallerydl-archive.sqlite3` when universal archives are enabled
- case-level `manifests/gui-job-recovery-<job-id>.json` files for recovery details

The **Default** profile loads on startup. Custom profiles can be managed from the Profile menu.

`python gui.py --fresh` clears app settings/state files, app-owned temp files, URL-box persistence files, universal archives, and temporary GUI cache folders under known Output Roots. It does not delete captured case folders, media files, cookies, binaries, or scripts.

## Cookies Handling

Cookies File use is disabled by default.

Cookies can help with approved authenticated captures or previews, but they are sensitive operational data. Cookie use does not guarantee access to restricted, private, expired, challenge-protected, or unsupported content.

The app can:

- use a selected cookies file for Audio/Video Capture, Image Capture, and Audio/Video Preview when enabled
- export browser cookies through yt-dlp's supported cookie export flow
- optionally encrypt or decrypt local cookies files
- delete selected Audio/Video and/or Image Capture cookies files on exit when configured

The app does not collect credentials or automate website logins.

## Limitations

- Source support depends on the installed `yt-dlp` and `gallery-dl` versions and the source platform.
- Preview metadata and thumbnails are best-effort and may be incomplete, stale, unavailable, or slow.
- Large playlists, large galleries, and large cases may take time to capture, scan, cache, export, or verify.
- Universal archive skips can reflect captures from other cases by design.
- Browser impersonation depends on the installed `yt-dlp` build and may be blocked by endpoint policy.
- Proxy/VPN behavior depends on local routing, policy, and source-platform handling.
- Case Browser thumbnails and media details generally require FFmpeg/FFprobe.
- Manifest verification checks file hashes only; it does not assess authenticity, context, or legal sufficiency.
- The app is not a substitute for authorization, evidence-handling policy, or analyst judgment.

## Changelog

### v1.2026.0626 - AVI Capture, Image Capture, and Dual-Engine Queueing

- Renamed the app from **yt-dlp GUI for OSINT** to **AVI Capture GUI for OSINT**, with the full name **Audio/Video/Image Capture GUI for OSINT**.
- Added a full **Image Capture** workflow powered by `gallery-dl`, including its own tab, PowerShell script, URL/input handling, case naming, filename templates, cookies, output root, preflight checks, capture options, and output log.
- Added `script-gallerydl.ps1` for gallery-dl captures, with app-local temp handling, input/error files, metadata sidecars, item limits, pacing, retries, timeout, archive modes, cookies, and proxy support.
- Renamed **URL Preview** to **Audio/Video Preview** to separate yt-dlp preview workflows from gallery-dl Image Capture workflows.
- Expanded the shared **Job Queue** to support both `yt-dlp` and `gallery-dl` jobs, including Add Current selection, highlighted-job actions, persistence, interruption recovery, per-job recovery manifests, and engine-aware resume behavior.
- Added recoverable direct-capture tracking when Job Persistence is enabled, so interrupted direct Audio/Video and Image captures can be continued from the Job Queue.
- Added separate universal archive handling for Audio/Video and Image Capture, using `universal-download-archive.txt` for yt-dlp and `universal-gallerydl-archive.sqlite3` for gallery-dl.
- Added gallery-dl version checking and update support matching the yt-dlp update workflow.
- Expanded Domain Presets, Proxy Options, VPN checks, case-folder collision checks, and domain-collision detection across both capture workflows.
- Added separate concurrent-capture settings for Audio/Video and Image Capture, allowing yt-dlp and gallery-dl jobs to run alongside each other while guarding against same-domain concurrent captures.
- Added Image Capture support to Case Browser, URL history clearing, cookie cleanup, settings/profile persistence, reset-defaults behavior, and README guidance.
- Cleaned up deprecated code paths and fixed parity/stability issues around queue validation, output-template handling, universal archive state, duplicate helpers, and settings migration.

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
