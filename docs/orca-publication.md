# OrcaSlicer distribution and inclusion

Research checked October 11, 2026. This project has not yet been submitted, listed, or approved by OrcaSlicer. Recheck the linked documentation before publishing because the plugin platform is in beta.

## Documented distribution route

Orca Cloud currently requires a plugin-enabled nightly. In **Plugins → Shared Plugins → +**, upload the wheel, fill in the listing/version/type/compatibility/changelog/tags, and enable **Public Plugin** for Plugin Hub discovery. Optional artwork is limited to 2 MB. Uploads accept `.py`/`.whl` with a supported OS suffix, including `any`; our wheel uses `py3-none-any`. Actual upload acceptance remains to be tested. See the [official creator guide](https://cloud.orcaslicer.com/wiki/#create-a-plugin).

For later releases, connect one repository to the owned listing under **GitHub publishing**. A release workflow requests GitHub OIDC with audience `orcacloud` and posts files plus version/changelog metadata to the documented publishing API. It needs `id-token: write` and `contents: read`; versions must increase. The first manual listing already consumes its version, so automation starts with the next version. Use the [official workflow and API instructions](https://cloud.orcaslicer.com/wiki/#publish-from-github). This repository deliberately contains no active Cloud publishing workflow.

The guide documents public listing, but no mandatory maintainer-review gate or bundled-inclusion application. Listing therefore does not establish endorsement. For explicit approval, ask maintainers which review they want through [OrcaSlicer Discussions](https://github.com/OrcaSlicer/OrcaSlicer/discussions); do not assume a core-code pull request is required.

## Proposed listing

| Field | Prepared value |
| --- | --- |
| Name | Electroplating Calculator |
| Version | 0.2.1 |
| Type | Script |
| File | `electroplating_calculator-0.2.1-py3-none-any.whl` |
| Tags | electroplating, surface-area, utility |
| Compatibility | Plugin-enabled nightly; tested Windows x64 v2.5.0-dev, October 8 build |
| Visibility | Public, only after release approval |
| Source/license | Public repository and GPL-3.0-or-later license, after publication |

If the compatibility picker cannot represent a nightly build, ask Orca Cloud support how to label it. Do not select stable 2.4.2 or claim Linux/macOS verification merely to satisfy the form.

Description to paste:

```text
Measure loaded model surface area and estimate electroplating current from your selected current density. Supports transformed model copies, per-part masking adjustments, area/density units, independent starting current, 24 bath reference profiles, saved voltage settings, and a copyable report.

Requires a plugin-enabled OrcaSlicer nightly. Native validation covers Windows x64 v2.5.0-dev; Linux and macOS remain unverified. Voltage is entered by the user, not calculated from area. The plugin does not control a power supply. Mesh area can include hidden/internal surfaces; adjust for actual bath exposure and use operating values appropriate to your supplier's formulation.

Independent community plugin. See the source repository for installation, reference sources, validation evidence, and limitations.
```

Changelog to paste:

```text
0.2.1: Public release packaging, GPL-3.0-or-later licensing, installation and validation documentation, and automated build/test checks. Includes the 0.2.0 calculator with 24 bath profiles and independent voltage settings. Calculator behavior is unchanged from 0.2.0.
```

## Proposed maintainer review request

After the public source and release links exist, include them with this draft. Sending it is a separate action from preparing it.

```text
I have developed an independent Electroplating Calculator script plugin for OrcaSlicer's plugin-enabled nightly. It reads loaded triangle meshes, accounts for instance transforms, and calculates current from user-adjusted area and selected density. It includes manufacturer-linked bath references and independent voltage settings; it does not modify models or control equipment.

The repository provides source, license, a wheel, automated tests, and native Windows validation notes, including remaining limitations. I would like to publish it through Orca Cloud Plugin Hub and have the integration reviewed. Is there a required review or approval process beyond creating the public listing? If recommended or bundled inclusion has separate criteria, where should I submit it?
```

For user installation after listing, follow [Orca's Cloud plugin documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/plugins_cloud). Developer packaging is described in [the official plugin development guide](https://github.com/OrcaSlicer/OrcaSlicer/wiki/plugin_development).
