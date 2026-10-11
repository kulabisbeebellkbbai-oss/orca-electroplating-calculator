"""Orca script capability with an asynchronous host-owned modal window."""
from dataclasses import asdict
from .calculation import RowChoice
from .dialog import render_dialog, parse_submission
from .geometry import CalculationCancelled
from .orca_adapter import require_host, collect_rows, required_method
from .settings import default_settings, decode_settings, encode_settings


def build_capability(orca):
    class ElectroplatingCalculator(orca.script.ScriptPluginCapabilityBase):
        def get_name(self):
            return "Electroplating Calculator"

        def get_description(self):
            return "Measure transformed model mesh area and calculate current at your selected density."

        def get_default_config(self):
            return asdict(default_settings())

        def execute(self):
            progress = None
            try:
                require_host(orca)
                window = getattr(self,"_window",None)
                if window is not None and window.is_open():
                    return orca.ExecutionResult.skipped("The calculator is already open.")
                settings = decode_settings(self.get_config())
                ui = orca.host.ui
                style = ui.PD_APP_MODAL | ui.PD_CAN_ABORT
                progress = ui.create_progress_dialog(title=self.get_name(),message="Measuring model meshes…",maximum=100,style=style)
                pulse = required_method(progress,"pulse","progress")
                required_method(progress,"close","progress")
                rows = collect_rows(orca.host.model(),progress=lambda done,total: pulse())
                progress.close();progress=None
                if not rows:
                    return orca.ExecutionResult.skipped("Load a model with a printable model part before running the calculator.")
                choices = [RowChoice(row.row_id,selected=not bool(row.error)) for row in rows]
                self._open(rows,settings,choices)
                return orca.ExecutionResult.success("Calculator opened. Results use the model snapshot measured at launch.")
            except CalculationCancelled:
                return orca.ExecutionResult.skipped("Measurement cancelled; no partial result or settings were saved.")
            except Exception as exc:
                return orca.ExecutionResult.failure(orca.PluginResult.RecoverableError,str(exc))
            finally:
                if progress is not None and callable(getattr(progress,"close",None)):
                    progress.close()

        def _open(self,rows,settings,choices,message=""):
            # Closures retain scalar snapshots, never native model or mesh handles.
            def submitted(payload):
                self._window = None
                try:
                    action,new_choices,new_settings = parse_submission(payload,rows)
                except (ValueError,TypeError) as exc:
                    self._open(rows,settings,choices,"Invalid form: " + str(exc))
                    return
                if action == "close":
                    return
                try:
                    saved = self.save_config(encode_settings(new_settings))
                    message = "Settings saved." if saved is True else "Could not save settings. Your temporary choices are retained; saved settings were not confirmed."
                except Exception as exc:
                    message = "Could not save settings: " + str(exc)
                self._open(rows,new_settings,new_choices,message)

            def closed():
                self._window = None

            self._window = orca.host.ui.create_window(
                render_dialog(rows,settings,message=message,choices=choices),
                title=self.get_name(),width=1050,height=850,
                style=orca.host.ui.WINDOW_MODAL,on_submit=submitted,on_close=closed)

        def on_unload(self):
            window=getattr(self,"_window",None)
            if window is not None:
                window.close()
            self._window=None

    return ElectroplatingCalculator
