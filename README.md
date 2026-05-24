# yt-dlp GUI for OSINT

A lightweight, portable Windows GUI for running an approved `yt-dlp` capture workflow in an organizational environment.

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
- [Recommended Deployment Approach](#recommended-deployment-approach)

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
- selecting an FFmpeg folder
- choosing a supported impersonation target
- checking the selected VPN/network adapter status
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

The app can reference a cookies file and includes helper options to export, encrypt, or decrypt cookies files.

Cookies files should be treated as sensitive. A raw cookies file may function like a browser session and should not be shared or stored casually.

For storage or transfer, use the app's encrypted cookies option or follow the organization's approved secure handling process.

The app does not display cookie contents in the GUI.

## Limitations

The app depends on the underlying PowerShell script and locally staged binaries. If those tools are missing, blocked, outdated, unsigned, or not permitted by policy, the app may not function.

The VPN check only confirms whether the selected adapter is up. It does not prove that traffic is routed through the VPN.

The preflight check confirms common prerequisites, but it cannot guarantee that every target URL will be accessible or capturable.

The app is only a workflow wrapper. It does not make authorization, policy, or legal decisions.

## Recommended Deployment Approach

For organizational use, I recommend the following approach:

1. IT or an approved administrator stages Python and all required binaries.
2. The app folder is placed in a local writable directory.
3. Users run the GUI from that local folder.
4. Active captures are written to a local case folder.
5. Completed case folders are moved or archived according to organizational policy.
6. Raw cookies files are kept local and short-lived, or stored only in encrypted form.

This keeps the app portable while avoiding installer behavior, automatic binary downloads, and other activity that may be flagged by ASR or endpoint security tools.
