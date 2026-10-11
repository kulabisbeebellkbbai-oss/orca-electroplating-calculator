# Verification evidence

## Release preparation — 0.2.1 (2026-10-11)

Calculator source is unchanged from 0.2.0. This release adds public documentation, licensing/metadata, CI, and version-aware wheel checks. Local build/test and package-audit results are recorded in the release preparation report outside the public source tree. A green GitHub Actions run must be obtained after publication; local checks do not claim hosted CI execution.

Native evidence below applies to 0.1.0/0.2.0. Installing and opening the exact 0.2.1 wheel is still a release smoke-check item.

## Automated coverage

The 0.2.0 suite passed 122 tests on Windows with Python 3.12.14, NumPy 2.5.3, pytest 9.1.1, and Playwright 1.63.0 / Chromium 153. Coverage includes transformed geometry, numerical/unit calculations, selections and masking, malformed meshes, cancellation contracts, settings migration, all 24 profiles, independent voltage/current behavior, resource loading, host callbacks, browser validation/report parity, and wheel contents.

The release wheel was imported from a separate verification environment and its HTML/JavaScript resources loaded. Fake-host tests and standalone browser tests are distinct from native OrcaSlicer evidence.

## Native host

Windows x64 portable OrcaSlicer v2.5.0-dev, compiled October 8 and downloaded October 9, 2026; embedded Python 3.12.13. The nightly archive SHA-256 was `D9645ECC8FE525F3F7D5AD6EEC0A318D8EA4D80A914E3BD426193D54DAD74622`. The moving nightly tag alone does not identify this exact binary.

The calculator wheel loaded and registered one script capability. The native plugin manager displayed version 0.2.0 as activated. Installation used Orca's supported local package layout; this does not verify the complete file-picker or Orca Cloud subscription flow.

A development probe measured the actual 10 mm cube through the installed adapter and rendered production resources in the native webview. [Recorded evidence](native-cube-evidence.json) shows 600 mm², 6 cm², and approximately 0.06510013 A at 0.07 A/in². The [user-copied report](native-user-report.txt) separately records a scaled cube and independent starting current.

## User-reported native checks

Reports were collected during guided checks on October 9–11, 2026. They are user observations, not automated native assertions.

| Check | Reported result |
| --- | --- |
| Run the calculator from the loaded project | Working |
| Uniform 200% scale | 24 cm² |
| Duplicate that cube | Two 24 cm² rows, total 48 cm² |
| Deselect one copy | Total returns to 24 cm² |
| Change density units | Converted density, unchanged amperage |
| Starting density 0.5 A/dm² on 24 cm² | 0.12 A, running current unchanged |
| Copy report | Correct text supplied and arithmetic independently checked |
| Change area units | 0.24 dm² with unchanged current |
| Save and restart | Edited bath label, tested density/start state and units retained |
| 0.2.0 bath profiles | Profiles reported working |
| Constant-voltage value changed from 2 V to 3 V | Calculated current unchanged |
| Save, close and reopen calculator | Constant-voltage mode and 3 V retained |

The voltage values above are software test inputs, not recommended process settings. Reopening the calculator does not establish whole-application restart persistence for the new voltage fields.

## Remaining checks

- Exact 0.2.1 wheel installation/opening in the native host.
- Native large-mesh cancellation and responsiveness under load.
- Linux and macOS native operation; a universal Python wheel is not evidence of host compatibility on those systems.
- Orca Cloud upload, subscription, activation, and upgrade behavior.
- Physical plating results and suitability of any reference for a particular bath or conductive coating.

## Reproduce and troubleshoot

Use the [development commands](../README.md#development), then install the built wheel in an isolated plugin-enabled nightly. Load `tests/fixtures/10mm_cube.stl`. Verify 6 cm², scale to 200% for 24 cm², duplicate for 48 cm², and compare current with the independent formula. Change units, exercise profile/voltage controls, and explicitly save/reopen preferences. Record exact versions and observations.

If the script asks for a printable model, load a normal model part before running it. If extraction fails on Windows, use a short writable test data directory; long nested package paths caused extraction failures during development. Orca's supported `--datadir` option isolates preferences. Do not alter global Windows path policy just to run this plugin.

Orca may prompt to read its own Python resource-reader bytecode when the calculator loads packaged HTML/JavaScript. Review the path: a standard-library read request is different from an unexplained request for unrelated files. Native UI automation was unable to operate some embedded webview controls, so the corresponding checks were completed manually and recorded above.
