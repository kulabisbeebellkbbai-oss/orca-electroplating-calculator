"""Offline, product-specific bath references. Unknown values are deliberately null.

Density ranges retain their source units. Voltage references are operating
voltages, never assumed to be constant-current compliance limits.
"""
from dataclasses import asdict, dataclass

CASWELL_SOURCE = 'https://caswellplating.com/electroplating-anodizing/copper-plating-kits/acid-copper-electroforming-kits.html'
GPS_CHART = 'https://www.goldplating.com/pages/bath-plating-5000-ml-setup'
GPS_PDF = 'https://cdn.shopify.com/s/files/1/1344/1717/files/'
DENSITY_TO_ADM2 = {'A/dm2': 1., 'A/in2': 10000 / 645.16, 'A/ft2': 10000 / 92903.04}
VOLTAGE_GUIDANCE = ('Voltage cannot be calculated from mesh area. In constant-current mode, the supply adjusts voltage to reach the selected current within your voltage limit. In constant-voltage mode, actual current must be measured; it is not predicted from voltage.')


@dataclass(frozen=True)
class BathProfile:
    label: str
    source: str = ''
    notes: str = 'Supplier settings required for your formulation.'
    density_range: tuple[float, float] | None = None
    density_unit: str = 'A/dm2'
    density_pick: float | None = None
    voltage_range: tuple[float, float] | None = None
    voltage_pick: float | None = None
    electrical: bool = True
    voltage_text: str = ''

    def as_data(self):
        data = asdict(self)
        # A range's lower end is an editable reference, not a startup recommendation.
        pick = self.density_pick if self.density_pick is not None else (self.density_range[0] if self.density_range else None)
        data['running_adm2'] = None if pick is None else pick * DENSITY_TO_ADM2[self.density_unit]
        data['voltage_v'] = self.voltage_pick if self.voltage_pick is not None else (self.voltage_range[0] if self.voltage_range else None)
        data['reference'] = self.reference()
        return data

    def reference(self):
        if not self.electrical:
            return f'{self.label}. Area only; no external plating current or voltage. {self.notes}'
        units = {'A/dm2':'A/dm²', 'A/in2':'A/in²', 'A/ft2':'A/ft²'}
        def span(values):
            return f'{values[0]:g}' if values[0] == values[1] else f'{values[0]:g}–{values[1]:g}'
        density = f'{span(self.density_range)} {units[self.density_unit]}' if self.density_range else 'not verified; enter supplier value'
        voltage = f'{span(self.voltage_range)} V' if self.voltage_range else (self.voltage_text or 'not verified; enter supplier value')
        return f'{self.label}. Density reference: {density}. Operating voltage reference: {voltage}. {self.notes}'


PROFILES = {
    'caswell_acid_copper': BathProfile('Acid copper — Caswell', CASWELL_SOURCE,
        'For the specified Caswell bath; additives alone do not establish equivalent operating conditions.', (.07,.20), 'A/in2'),
    'acid_copper_gps': BathProfile('Acid copper — GPS Bright Acid Copper', GPS_CHART,
        'ProLab 5 L setup, room temperature, agitation; published voltage optimum 1.5 V.', voltage_range=(1,3), voltage_pick=1.5),
    'copper_alkaline': BathProfile('Alkaline copper — supplier settings',
        'https://caswellplating.com/electroplating-anodizing/copper-plating-kits/flash-alkaline-copper-plating-kits.html'),
    'nickel_bright': BathProfile('Bright nickel — GPS', GPS_PDF+'Bright_Nickel_Bath_TDS_8_20_26.pdf?v=1787260133',
        '135–155°F (optimum 140°F), agitation. Voltage depends on tank size: 5–7 V smaller tanks; 6–12 V larger tanks. Enter the applicable voltage manually.', (20,50), 'A/ft2', voltage_text='tank-size dependent; see notes'),
    'nickel_sulfamate': BathProfile('Sulfamate nickel — Caswell electroforming',
        'https://caswellplating.com/nickel-electroforming-solution-part-a-1-quart.html',
        'Caswell nickel electroforming formulation; approximate operating voltage.', (.07,.3), 'A/in2', voltage_range=(2,4)),
    'nickel_black': BathProfile('Black nickel — Caswell',
        'https://caswellplating.com/electroplating-anodizing/nickel-plating-kits.html',
        'Black Nickel Plating Crystals product reference; nickel anode.', (.01,.01), 'A/in2'),
    'zinc_acid': BathProfile('Acid zinc — supplier settings',
        'https://www.columbiachemical.com/metal-finishing-products/functional-plating/zinc-plating/'),
    'zinc_alkaline': BathProfile('Alkaline zinc — supplier settings',
        'https://www.columbiachemical.com/metal-finishing-products/functional-plating/zinc-plating/'),
    'zinc_nickel': BathProfile('Zinc-nickel — Caswell',
        'https://caswellplating.com/zinc-nickel-plating-kit-4-5-gal.html',
        'For this Caswell kit. Current density was not published in the reviewed product page.', voltage_range=(6,6)),
    'tin': BathProfile('Tin electroplating — supplier settings',
        'https://caswellplating.com/electroplating-anodizing/tin-plating-kits/tin-electroplating-kits.html'),
    'brass': BathProfile('Brass — Caswell cyanide-free',
        'https://caswellplating.com/electroplating-anodizing/brass-plating-kits.html',
        'Caswell alkaline brass tank plating formulation.', (.02,.1), 'A/in2', voltage_range=(3,12)),
    'bronze': BathProfile('Bronze — Caswell decorative',
        'https://caswellplating.com/electroplating-anodizing/bronze-plating-kits.html',
        'Caswell decorative bronze formulation at 80°F.', (.07,.07), 'A/in2', voltage_range=(3,3)),
    'silver_nc': BathProfile('Silver — GPS Bright Silver NC', GPS_PDF+'Silver_NC_TDS_8_20_26.pdf?v=1787260133',
        'Non-cyanide formulation, room temperature, moderate movement. Published density optimum 10 A/ft².', (1,20), 'A/ft2', 10, (1.5,3)),
    'gold_soft': BathProfile('Soft gold — GPS 24K Pure Gold', GPS_PDF+'Pure_Gold_Bath_TDS_8_20_26.pdf?v=1787261244',
        '120–150°F (optimum 150°F), moderate movement. Conversion uses the stated 3 A/ft², not the rounded parenthetical mA/in². Voltage may vary under current control.', (3,3), 'A/ft2', voltage_range=(1.5,1.5)),
    'gold_hard': BathProfile('Hard gold — GPS Bright Gold', GPS_PDF+'Bright_Gold_-_TDS_8_20_26.pdf?v=1787865291',
        'Cobalt-hardened bath gold, 90–105°F (optimum 100°F), agitation. Published deposition example uses 6 A/ft² or 2.8 V.', (5,15), 'A/ft2', 6, (2.8,2.8)),
    'gold_rose': BathProfile('Rose gold — GPS Bath Rose Gold', GPS_CHART,
        'ProLab 5 L setup at 120–130°F with agitation; not Eco-Rose.', voltage_range=(4,6)),
    'rhodium': BathProfile('Rhodium — GPS ProLab reference', GPS_CHART,
        'ProLab 5 L procedure chart, room temperature, agitation. Verify the exact rhodium product instructions.', voltage_range=(2,4)),
    'palladium': BathProfile('Palladium — GPS Bright Palladium', GPS_PDF+'Bright_Palladium_TDS_8_20_26.pdf?v=1787260134',
        'Bath application at 120°F; published voltage optimum 2 V. Brush settings differ.', voltage_range=(1.5,2), voltage_pick=2),
    'chromium_trivalent': BathProfile('Trivalent chromium — supplier settings'),
    'chromium_hexavalent': BathProfile('Hexavalent chromium — supplier settings'),
    'electroless_nickel': BathProfile('Electroless nickel', notes='Follow the specific bath process sheet.', electrical=False),
    'electroless_copper': BathProfile('Electroless copper', notes='Follow the specific bath process sheet.', electrical=False),
    'immersion_tin': BathProfile('Immersion tin', notes='Immersion deposition; follow the specific bath process sheet.', electrical=False),
    'custom': BathProfile('Custom bath'),
}


def profile_data():
    return {key: profile.as_data() for key, profile in PROFILES.items()}
