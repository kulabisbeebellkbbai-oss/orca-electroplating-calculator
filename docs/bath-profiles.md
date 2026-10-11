# Bath profiles and voltage settings — 0.2.0

References reviewed October 10, 2026. Each named product's data applies to that formulation and its process conditions, not every bath depositing the same metal. References do not validate direct plating onto a conductive coating. The catalog keeps source units and converts A/ft² using exactly 929.0304 cm² per square foot.

The selector changes reference context while retaining manual entries. **Use profile settings** replaces the bath label, loads the published density point (or lower range endpoint), clears starting density, and leaves missing values blank. In constant-voltage mode it also loads an operating-voltage point or lower endpoint. In constant-current mode it clears voltage: an operating-voltage reference is not a compliance limit. Changing control modes also clears voltage. No profile assumes a startup density appropriate to a painted print.

Blank density means area can still be reported and settings saved, but running current is unknown. Blank voltage means no limit/setpoint has been selected. Electroless nickel/copper and immersion tin clear and disable electrical fields; their reports show area and electrical settings as not applicable.

## Numeric references

| Product/profile | Density reference | Operating voltage reference | Source |
| --- | --- | --- | --- |
| Caswell acid copper | 0.07–0.20 A/in² | Unverified | [Product](https://caswellplating.com/electroplating-anodizing/copper-plating-kits/acid-copper-electroforming-kits.html) |
| GPS Bright Acid Copper | Unverified | 1–3 V, optimum 1.5 | [ProLab 5 L chart](https://www.goldplating.com/pages/bath-plating-5000-ml-setup) |
| GPS Bright Nickel | 20–50 A/ft² | 5–7 V smaller tanks; 6–12 V larger tanks; manual entry | [2026 bath TDS](https://cdn.shopify.com/s/files/1/1344/1717/files/Bright_Nickel_Bath_TDS_8_20_26.pdf?v=1787260133) |
| Caswell sulfamate nickel electroforming | 0.07–0.3 A/in² | Approx. 2–4 V | [Product](https://caswellplating.com/nickel-electroforming-solution-part-a-1-quart.html) |
| Caswell black nickel | 0.01 A/in² | Unverified | [Crystals listing](https://caswellplating.com/electroplating-anodizing/nickel-plating-kits.html) |
| Caswell zinc-nickel | Unverified | 6 V | [Product](https://caswellplating.com/zinc-nickel-plating-kit-4-5-gal.html) |
| Caswell brass | 0.02–0.1 A/in² | 3–12 V | [Product](https://caswellplating.com/electroplating-anodizing/brass-plating-kits.html) |
| Caswell decorative bronze | 0.07 A/in² | 3 V | [Product](https://caswellplating.com/electroplating-anodizing/bronze-plating-kits.html) |
| GPS Bright Silver NC | 1–20 A/ft², optimum 10 | 1.5–3 V | [2026 TDS](https://cdn.shopify.com/s/files/1/1344/1717/files/Silver_NC_TDS_8_20_26.pdf?v=1787260133) |
| GPS 24K Pure Gold (soft) | 3 A/ft² | 1.5 V; may vary under current control | [2026 bath TDS](https://cdn.shopify.com/s/files/1/1344/1717/files/Pure_Gold_Bath_TDS_8_20_26.pdf?v=1787261244) |
| GPS Bright Gold (hard) | 5–15 A/ft²; deposition example 6 | Deposition example 2.8 V | [2026 bath TDS](https://cdn.shopify.com/s/files/1/1344/1717/files/Bright_Gold_-_TDS_8_20_26.pdf?v=1787865291) |
| GPS Bath Rose Gold | Unverified | 4–6 V | [ProLab 5 L chart](https://www.goldplating.com/pages/bath-plating-5000-ml-setup) |
| GPS Rhodium ProLab reference | Unverified | 2–4 V | [ProLab 5 L chart](https://www.goldplating.com/pages/bath-plating-5000-ml-setup) |
| GPS Bright Palladium | Unverified | 1.5–2 V, optimum 2 | [2026 TDS](https://cdn.shopify.com/s/files/1/1344/1717/files/Bright_Palladium_TDS_8_20_26.pdf?v=1787260134) |

Temperature, tank-size and agitation qualifications appear alongside each reference in the calculator and copied report. The GPS 2026 TDS takes precedence over older web charts for nickel, silver, pure/hard gold and palladium. Brush-plating voltages and anode current density are not used for bath cathode-current calculations.

## Profiles requiring supplier values

Alkaline copper, acid zinc, alkaline zinc, tin electroplating, trivalent chromium, hexavalent chromium, and Custom have no preloaded electrical numbers. Copper/zinc/tin entries link to the reviewed manufacturer product family; those links identify the process rather than substantiate a numeric setting. Chromium and Custom require the user's specific product sheet. Do not substitute a chrome-look nickel/cobalt bath for actual chromium.

Electroless nickel, electroless copper, and immersion tin are area-only profiles. Their bath chemistry and process conditions remain user-supplied.

## Upgrade

Schema 1 migrates to schema 2 in memory; existing values stay unchanged and default power mode is constant current with voltage unset. Explicit Save writes schema 2. Orca's local plugin key includes its wheel version, so installation updates must transfer the capability configuration to the new key. Retain a backup of the old package, install-state permissions and config before changing the package directory. See testing evidence for the actual local update state.
