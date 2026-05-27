# yt-dlp GUI for OSINT

A lightweight, portable Windows GUI for running an approved `yt-dlp` capture workflow in an organizational environment.

![Screenshot](/screenshots/main.png)

## Table of Contents

- [Overview](#overview)
- [Intended Users](#intended-users)
- [What the App Does](#what-the-app-does)
- [What the App Does Not Do](#what-the-app-does-not-do)
- [Organizational Compatibility](#organizational-compatibility)
- [Required Components](#required-components)
- [Basic Usage](#basic-usage)
- [Profiles and Settings](#profiles-and-settings)
- [Cookies Handling](#cookies-handling)
- [Limitations](#limitations)
- [Changelog](#changelog)

## Overview

`yt-dlp GUI for OSINT` is a simple desktop interface I created to make `yt-dlp` capture workflows easier, more consistent, and more approachable for OSINT users working inside a managed organization.

The app is intentionally narrow in scope. It is not a general OSINT platform, web scraper, browser automation tool, or evidence analysis suite. It is a GUI wrapper around an existing PowerShell and `yt-dlp` workflow, with supporting options for case folders, cookies, profiles, preflight checks, VPN adapter status, and output organization.

## Intended Users

This app is intended for investigators, analysts, or support staff who need a repeatable way to collect media or metadata using `yt-dlp` without manually assembling command-line arguments each time.

It assumes the user is working under their organization's policies and has authorization to perform the captures they are attempting.

## What the App Does

The app provides a guided interface for:

- selecting the PowerShell capture script
- selecting the local `yt-dlp` executable
- choosing an input URL file or pasting URLs directly
- setting a case name and output folder
- selecting a cookies file when needed
- optionally deleting the selected cookies file when the GUI exits
- selecting an FFmpeg folder
- choosing a supported impersonation target, with an option to show all returned yt-dlp targets
- choosing capture options such as max resolution, archive mode, date filters, source scope, and sidecar artifacts
- configuring advanced filters such as match/reject title keywords, failure handling, and request pacing
- browsing output root case folders in a separate case browser window
- viewing generated GUI thumbnails for captured videos when FFmpeg is available
- viewing cached video/audio media details through case browser cards and tooltips
- opening selected folders, captured media, and sidecar files from the case browser
- single-clicking folders to expand them and show their contents in the case browser
- optionally checking the selected VPN/network adapter status
- running a preflight check before capture
- starting and stopping the capture workflow
- opening the current case folder
- saving and loading settings
- creating reusable profiles

The goal is to reduce mistakes, make captures more repeatable, and keep the workflow understandable for users who are not comfortable running commands manually.

## What the App Does Not Do

The app does not:

- include or distribute `yt-dlp`, FFmpeg, Deno, Python, or any other binaries
- download binaries automatically
- bypass organizational security controls
- bypass website access controls
- perform credential collection
- automate logins
- perform browser automation
- perform content analysis
- perform identity matching
- determine whether a capture is legally or organizationally authorized

The app only helps run a local, approved capture workflow.

## Organizational Compatibility

This app is designed with managed environments in mind.

To reduce the chance of triggering Attack Surface Reduction (ASR), endpoint protection, or application control policies, the app does **not** include downloaded binaries and does **not** attempt to fetch executables from the internet.

All required tools must be obtained, reviewed, and staged separately according to the organization's process.

This design is intentional. The app should operate as a wrapper around approved local tools, not as a downloader or installer.

## Required Components

The following components must be provided separately:

- Python
- the PowerShell capture script
- `yt-dlp.exe`
- `ffmpeg.exe`
- `ffprobe.exe`
- `deno.exe`

Python may require administrative privileges to install, depending on the organization's software installation policies.

All required binaries, including `yt-dlp`, FFmpeg, and Deno, should be official signed releases whenever available. They should be downloaded only from trusted official sources and staged by IT or another approved process.

## Basic Usage

1. Launch the app.
2. Confirm the paths for the PowerShell script, `yt-dlp`, cookies file, output folder, and FFmpeg folder.
3. Enter a case name.
4. Paste URLs into the URL box or select an input file.
5. Select the VPN/network adapter used for the capture, if applicable.
6. Run **Preflight Check**.
7. Start the capture with **Start Capture**.
8. Review the output log.
9. Open the case folder using the **Open** button beside the case name.

The URL box takes priority over the input file. If the URL box contains URLs, those URLs are used for the run.

## Profiles and Settings

The app stores settings in a portable JSON settings file located beside the app.

Profiles are stored inside the same settings file.

The **Default** profile is always loaded on startup and is used for normal persistent settings. Custom profiles can be created for different capture workflows and loaded from the Profile menu.

Resetting defaults only resets the Default profile. It does not remove custom profiles.

## Cookies Handling

The app can reference a cookies file and includes helper options to export, encrypt, decrypt, or delete the selected cookies file on exit.

Cookies files should be treated as sensitive. A raw cookies file may function like a browser session and should not be shared or stored casually.

For storage or transfer, use the app's encrypted cookies option or follow the organization's approved secure handling process.

The app does not display cookie contents in the GUI.

The **Delete Cookies on Exit** setting is stored as an app-level setting, not a profile setting. When enabled, the app attempts to delete the file currently shown in the Cookies File field when the GUI closes.

The **Check VPN** setting is also stored as an app-level setting, not a profile setting. When disabled, the VPN Status section is hidden, the VPN-related Tools menu actions are disabled, and capture start does not warn if the VPN is not connected.

## Limitations

The app depends on the underlying PowerShell script and locally staged binaries. If those tools are missing, blocked, outdated, unsigned, or not permitted by policy, the app may not function.

The VPN check only confirms whether the selected adapter is up. It does not prove that traffic is routed through the VPN.

The preflight check confirms common prerequisites, but it cannot guarantee that every target URL will be accessible or capturable.

The case browser uses FFmpeg to generate PNG thumbnails in a `.gui-cache` folder. It also uses FFprobe to cache media information such as duration, size, codec, resolution, frame rate, and audio details. If FFmpeg or FFprobe is unavailable, the app displays fallback placeholders and unavailable media details instead.

The app is only a workflow wrapper. It does not make authorization, policy, or legal decisions.

## Changelog

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
