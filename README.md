# Electroplating Calculator for OrcaSlicer

Measure model surface area and calculate electroplating current inside OrcaSlicer. The calculator uses the loaded model's scale and instances, supports masking adjustments, and includes 24 bath reference profiles with independent starting-current and voltage settings.

**Beta:** requires a plugin-enabled OrcaSlicer nightly. Native testing covers Windows x64, OrcaSlicer v2.5.0-dev (October 8, 2026 build). Stable 2.4.2 does not support this plugin. Linux and macOS native operation remain unverified. This is an independent community plugin; it is not endorsed by OrcaSlicer or the referenced chemical suppliers.

## Install

Download the `.whl` file from this repository's Releases page, or [build it locally](#development). Use an [official OrcaSlicer nightly](https://github.com/OrcaSlicer/OrcaSlicer/releases/tag/nightly-builds) with a separate test data directory so your usual printer profiles are preserved.

1. Open the main menu beside **File**, then **Plugins**.
2. Open the dropdown beside **Install plugin**, choose **Install local plugin**, and select `electroplating_calculator-0.2.1-py3-none-any.whl`.
3. Enable the package and its **Electroplating Calculator** script capability.
4. Load a model containing a printable part, then run the calculator from the Plugins window.

Orca manages the plugin's Python environment. Initial dependency installation needs NumPy and may need an Internet connection. The calculator itself makes no network requests and does not modify meshes, printer presets, or power-supply settings. It reads loaded geometry, displays a report, and saves plugin preferences only when requested. Orca may ask for read permission for Python's resource-loading modules.

On Windows, use a short writable data-directory path if wheel extraction hits path-length limits. See [verification and troubleshooting](docs/testing.md). Disable or remove the package through Orca's Plugins manager to uninstall it.

## Use

1. Load and scale your model. Reopen the calculator after geometry changes; each run measures a snapshot.
2. Select the copies and parts you will plate. Reduce coverage or subtract excluded area for masking and unexposed regions. Exclusion is subtracted **after** the coverage percentage.
3. Select a bath reference. **Use profile settings** loads the named product's available references and clears starting density. Enter densities appropriate to your actual process; a blank running density leaves current unknown.
4. Choose constant-current or constant-voltage mode. Enter a voltage limit or setpoint respectively. Changing modes clears voltage because these settings have different meanings. Profile voltage references load only in constant-voltage mode.
5. Copy the report, or select its text and use your operating system's copy shortcut. **Save settings** stores labels, densities, units, mode, and voltage. Selection and masking are temporary; closing alone saves nothing.

**Current (A) = adjusted plated area (dm²) × selected current density (A/dm²).**

For example, a 10 mm cube has 6 cm² of mesh area. At 0.07 A/in² it gives approximately 0.0651 A. A 200% scaled cube has 24 cm², giving approximately 0.2604 A. A separate starting density of 0.5 A/dm² gives 0.12 A for that scaled cube. These are arithmetic examples, not bath operating recommendations.

Voltage is a saved user setting; it is not calculated from area and does not alter the area-based current estimate. Actual current in constant-voltage operation must be measured. The plugin does not control equipment or estimate deposition time or thickness.

## Bath references

The [reference catalog](docs/bath-profiles.md) covers copper, nickel, zinc, zinc-nickel, tin, brass, bronze, silver, gold, rhodium, palladium, chromium, electroless/immersion processes, and Custom. Missing verified numeric references require manual entry. Electroless and immersion profiles show area only and clear electrical fields.

The initial reference is Caswell acid copper at an editable 0.07 A/in²; the displayed supplier range applies to its specified formulation. The initial coating label is MG Chemicals 843AR. Labels do not establish compatibility or infer a starting density. Use the supplier's process documentation for the actual chemistry, preparation, and operating conditions.

Changing the selected reference retains manual entries until **Use profile settings** is pressed, except for non-electrical processes. Schema-1 copper settings migrate without changing existing labels, densities, starting state, or units. Voltage begins unset. Orca may identify local packages by versioned wheel name; record your preferences before upgrading and verify them afterward.

## What the area means

The plugin sums transformed triangle areas in Orca's millimeter geometry, including nonuniform scaling and mirrored instances. Modifier, negative, and support volumes are excluded, but **negative cuts and boolean unions are not applied** to the remaining positive meshes. Multipart interfaces, overlaps, internal shells, and modeled cavities can therefore be counted. Degenerate and non-manifold meshes produce notices; malformed geometry remains visible as an excluded error row.

Use a final exterior mesh when the model contains substantial boolean geometry, then adjust for bath exposure. STL coordinates are unitless; Orca's interpreted dimensions are authoritative here. Printed texture, trapped air, coating coverage, resistance, contact quality, and uneven current distribution are not measured.

## Development

Use Python 3.12 or newer. From the repository root, create and activate a virtual environment using your platform's normal commands, then run:

```sh
python -m pip install -e ".[dev]"
python -m playwright install chromium
python -m build
python -m pytest -q
```

On Linux, Playwright may also need OS libraries; its `install --with-deps chromium` command installs those in CI. Build before testing because the suite inspects the wheel. [CONTRIBUTING.md](CONTRIBUTING.md) explains changes and validation; [docs/testing.md](docs/testing.md) separates automated coverage from native evidence and open checks.

Development probes in `tools/` are excluded from the wheel. The optional live probe only writes evidence when explicitly given a destination and requires an installed calculator. It is not needed for normal use.

## Releases and licensing

See the [changelog](CHANGELOG.md), [release checklist](docs/releasing.md), and [Orca publishing guide](docs/orca-publication.md). The package is GPL-3.0-or-later; see [LICENSE](LICENSE). Supplier product names identify reference sources and do not imply endorsement. NumPy is a separately installed dependency; see [third-party notices](THIRD_PARTY_NOTICES.md).
