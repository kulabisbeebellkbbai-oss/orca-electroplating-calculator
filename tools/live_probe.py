# /// script
# dependencies = []
# [tool.orcaslicer.plugin]
# name = "Calculator Live Probe"
# description = "Development-only read-only cube acceptance probe"
# version = "0.1.0"
# ///
"""Run only in isolated development data with an explicit output destination.

The helper waits for the main loop, measures the loaded fixture using the
installed calculator engine, and opens its actual HTML in Orca's webview.
It does not save calculator settings or mutate native models/presets.
"""
import json
import os
import sys
from pathlib import Path
import orca


class LiveProbe(orca.script.ScriptPluginCapabilityBase):
    def get_name(self):
        return "Calculator Live Probe"

    def on_load(self):
        destination=os.environ.get("ORCA_CALCULATOR_LIVE_OUTPUT")
        if not destination:
            return
        self._destination=Path(destination)
        self._done=False
        self._window=orca.host.ui.create_window(
            '<html><body><p>Development cube probe waiting for the loaded model…</p><script>let n=0;const t=setInterval(()=>{window.orca.postMessage({ready:true});if(++n>40)clearInterval(t);},500);</script></body></html>',
            title="Calculator Live Probe",width=700,height=250,on_message=self._measure)

    def _measure(self,payload):
        if self._done:
            return
        if "electroplating_calculator" not in sys.modules:
            return
        try:
            from electroplating_calculator.orca_adapter import collect_rows,require_host
            from electroplating_calculator.calculation import RowChoice,calculate
            from electroplating_calculator.settings import default_settings
            from electroplating_calculator.dialog import render_dialog
            require_host(orca)
            rows=collect_rows(orca.host.model())
            if not rows:
                return
            if any("10mm_cube" not in r.label for r in rows):
                raise RuntimeError("Live probe expects only the development cube fixture")
            settings=default_settings()
            choices=[RowChoice(r.row_id) for r in rows]
            result=calculate(rows,choices,running_adm2=settings.running_adm2)
            from dataclasses import asdict
            self._evidence={"rows":[asdict(r) for r in rows],"total_mm2":result.total_mm2,"running_a":result.running_a,"native_render":None}
            self._destination.write_text(json.dumps(self._evidence,indent=2),encoding="utf-8")
            self._done=True
            self._window.close()
            html=render_dialog(rows,settings)
            verification='<script>setTimeout(()=>window.orca.postMessage({total:document.getElementById("total").textContent,current:document.getElementById("running-result").textContent,report:document.getElementById("report").value}),800);</script>'
            html=html.replace('</body>',verification+'</body>')
            self._window=orca.host.ui.create_window(html,title="Development Calculator Preview",width=1050,height=850,on_message=self._rendered)
        except Exception as exc:
            self._destination.write_text(json.dumps({"error":str(exc)}),encoding="utf-8")

    def _rendered(self,payload):
        self._evidence["native_render"]=payload
        self._destination.write_text(json.dumps(self._evidence,indent=2),encoding="utf-8")

    def execute(self):
        return orca.ExecutionResult.skipped("Development-only automatic fixture probe.")


@orca.plugin
class LiveProbePackage(orca.base):
    def register_capabilities(self):
        orca.register_capability(LiveProbe)
