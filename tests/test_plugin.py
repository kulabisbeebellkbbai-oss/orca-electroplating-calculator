from dataclasses import asdict
from types import SimpleNamespace as NS
import pytest
from tests.test_adapter import model
from electroplating_calculator.calculation import RowChoice
from electroplating_calculator.settings import default_settings
from electroplating_calculator.plugin import build_capability


class Base:
    def __init__(self): self.saved=[];self.raw="";self.save_outcome=True
    def get_config(self): return self.raw
    def save_config(self,raw):
        self.saved.append(raw)
        if isinstance(self.save_outcome,Exception): raise self.save_outcome
        return self.save_outcome


class UI:
    WINDOW_MODAL=1;PD_CAN_ABORT=16;PD_APP_MODAL=1;PD_AUTO_HIDE=4
    def __init__(self): self.windows=[];self.cancel=False;self.progress_closed=False
    def create_progress_dialog(self,**kwargs):
        return NS(pulse=lambda: not self.cancel,close=lambda:setattr(self,"progress_closed",True))
    def create_window(self,html,**kwargs):
        self.windows.append((html,kwargs)); return NS(close=lambda:None,is_open=lambda:True)


def host():
    ui=UI()
    outcomes=NS(success=lambda msg:('success',msg),skipped=lambda msg:('skipped',msg),failure=lambda status,msg:('failure',msg))
    return NS(host=NS(model=model,ui=ui),script=NS(ScriptPluginCapabilityBase=Base),ExecutionResult=outcomes,PluginResult=NS(RecoverableError=1))


def form():
    return dict(action="save",choices=[asdict(RowChoice("0:0:0"))],settings=asdict(default_settings()))


def test_no_implicit_save_and_close():
    orca=host();cap=build_capability(orca)()
    assert cap.get_name()=="Electroplating Calculator"
    assert cap.execute()[0]=='success' and cap.saved==[] and orca.host.ui.progress_closed
    orca.host.ui.windows[-1][1]['on_submit']({'action':'close'})
    assert cap.saved==[]


@pytest.mark.parametrize("outcome",[False,RuntimeError("disk full"),True])
def test_explicit_save_outcome_keeps_temporary_choices(outcome):
    orca=host();cap=build_capability(orca)();cap.save_outcome=outcome;cap.execute()
    p=form();p['choices'][0]['plated_percent']=50
    orca.host.ui.windows[-1][1]['on_submit'](p)
    assert len(cap.saved)==1 and len(orca.host.ui.windows)==2
    html=orca.host.ui.windows[-1][0]
    assert '"plated_percent": 50' in html
    assert ('Settings saved.' in html)==(outcome is True)
    if outcome is not True: assert 'Could not save settings' in html


def test_cancel_saves_nothing_and_closes_progress():
    orca=host();orca.host.ui.cancel=True;cap=build_capability(orca)()
    assert cap.execute()[0]=='skipped'
    assert cap.saved==[] and orca.host.ui.windows==[] and orca.host.ui.progress_closed


def test_unsupported_host_and_invalid_config():
    orca=host();orca.host.ui=NS(create_window=lambda:None,create_progress_dialog=lambda:None)
    result=build_capability(orca)().execute()
    assert result[0]=='failure' and 'WINDOW_MODAL' in result[1]


def test_bad_configuration_not_overwritten():
    orca=host();cap=build_capability(orca)();cap.raw='{broken'
    assert cap.execute()[0]=='failure' and cap.saved==[] and orca.host.ui.windows==[]


def test_missing_host_named():
    orca=host();orca.host.model=None;cap=build_capability(orca)()
    result=cap.execute()
    assert result[0]=='failure' and 'orca.host.model' in result[1]


def test_exactly_one_registered_script(monkeypatch):
    import sys
    from pathlib import Path
    orca=host();packages=[];capabilities=[]
    orca.base=object
    orca.plugin=lambda cls:packages.append(cls) or cls
    orca.register_capability=capabilities.append
    monkeypatch.setitem(sys.modules,'orca',orca)
    namespace={'__name__':'electroplating_calculator','__package__':'electroplating_calculator'}
    exec(Path('src/electroplating_calculator/__init__.py').read_text(),namespace)
    assert len(packages)==1
    packages[0]().register_capabilities()
    assert len(capabilities)==1
    assert issubclass(capabilities[0],Base)


def test_missing_cancellation_flag_fails_before_window():
    orca=host()
    orca.host.ui=NS(create_window=orca.host.ui.create_window,create_progress_dialog=orca.host.ui.create_progress_dialog,WINDOW_MODAL=1,PD_APP_MODAL=1)
    result=build_capability(orca)().execute()
    assert result[0]=='failure' and 'PD_CAN_ABORT' in result[1]


def test_incomplete_progress_handle_reports_named_error():
    orca=host();orca.host.ui.create_progress_dialog=lambda **kw:NS(close=lambda:None)
    result=build_capability(orca)().execute()
    assert result[0]=='failure' and 'progress.pulse' in result[1]
