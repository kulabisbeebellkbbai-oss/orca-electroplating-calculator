"""Surface-area and current calculations, optionally hosted by Orca."""
try:
    import orca
except ModuleNotFoundError as exc:
    if exc.name != "orca":
        raise
    orca = None

if orca is not None:
    from .plugin import build_capability
    ElectroplatingCalculator = build_capability(orca)

    @orca.plugin
    class ElectroplatingPackage(orca.base):
        def register_capabilities(self):
            orca.register_capability(ElectroplatingCalculator)
