(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('data').textContent);
  const $ = id => document.getElementById(id);
  const areaFactors = {cm2:100, dm2:10000, in2:645.16};
  const areaLabels = {cm2:'cm²',dm2:'dm²',in2:'in²'};
  const densityFactors = {'A/dm2':1,'A/in2':10000/645.16};
  const controls = [];
  let densityUnit = data.settings.density_unit;
  let running = data.settings.running_adm2;
  let starting = data.settings.starting_adm2;
  let state = null;
  // Same eight significant digits as the Python plain-text report.
  function number(value) {
    if (value === 0) return '0';
    const parts = value.toExponential(7).split('e');
    const exponent = Number(parts[1]);
    const trim = text => text.includes('.') ? text.replace(/0+$/,'').replace(/\.$/,'') : text;
    if (exponent < -4 || exponent >= 8) {
      return trim(parts[0]) + 'e' + (exponent < 0 ? '-' : '+') + String(Math.abs(exponent)).padStart(2,'0');
    }
    return trim(Number(parts.join('e')).toFixed(Math.max(0,7-exponent)));
  }
  function numeric(input,name,minimum=0,positive=false) {
    if (input.value.trim() === '') throw new Error('Enter ' + name + '.');
    const value = Number(input.value);
    if (!Number.isFinite(value) || value < minimum || (positive && value === 0)) throw new Error('Enter a valid ' + name + '.');
    return value;
  }
  Object.entries(data.profiles).forEach(([id,profile])=>{
    const option=document.createElement('option');option.value=id;option.textContent=profile.label;$('profile').append(option);
  });
  $('profile').value = data.settings.profile;
  $('bath').value = data.settings.bath_label;
  $('coating').value = data.settings.coating_label;
  $('density-unit').value = densityUnit;
  $('area-unit').value = data.settings.area_unit;
  $('running').value = running === null ? '' : String(running/densityFactors[densityUnit]);
  $('use-start').checked = starting !== null;
  $('starting').disabled = starting === null;
  $('starting').value = starting === null ? '' : String(starting/densityFactors[densityUnit]);
  $('message').textContent = data.message;
  $('power-mode').value=data.settings.power_mode;
  $('voltage').value=data.settings.voltage_v === null ? '' : String(data.settings.voltage_v);
  $('voltage-guidance').textContent=data.voltage_guidance;

  data.rows.forEach((row,index) => {
    const choice = data.choices[index];
    const tr = document.createElement('tr');
    const cells = Array.from({length:5},() => tr.appendChild(document.createElement('td')));
    const include = document.createElement('input');
    include.type='checkbox'; include.checked=choice.selected; include.disabled=!!row.error;
    include.setAttribute('aria-label','Include '+row.label);
    const label = document.createElement('label'); label.append(include,document.createTextNode(' '+row.label));
    cells[0].append(label);
    if (row.error) { const error=document.createElement('small');error.textContent=row.error;cells[0].append(error); }
    const percent = document.createElement('input'); percent.type='number';percent.step='any';percent.min='0';percent.max='100';percent.value=String(choice.plated_percent);percent.disabled=!!row.error;
    percent.setAttribute('aria-label','Plated percentage for '+row.label);
    const excluded = document.createElement('input');excluded.type='number';excluded.step='any';excluded.min='0';excluded.value=String(choice.excluded_cm2);excluded.disabled=!!row.error;
    excluded.setAttribute('aria-label','Excluded cm² for '+row.label);
    cells[2].append(percent);cells[3].append(excluded);$('parts').append(tr);
    controls.push({row,include,percent,excluded,measured:cells[1],adjusted:cells[4]});
  });

  function report(settings,choices,total,run,start,warnings) {
    const profile=data.profiles[settings.profile];
    const lines=['Electroplating Calculator','Bath: '+settings.bath_label,'Coating: '+settings.coating_label,'Measured mesh area / adjusted plated estimate:'];
    controls.forEach((c,i) => {
      if (choices[i].selected) lines.push(c.row.label+': '+number(c.row.area_mm2/100)+' cm² / '+number(choices[i].adjusted/100)+' cm²');
      else if (c.row.error) lines.push('Excluded invalid mesh: '+c.row.label+': '+c.row.error);
    });
    lines.push('Total adjusted plated estimate: '+Object.keys(areaFactors).map(u=>number(total/areaFactors[u])+' '+areaLabels[u]).join(' / '));
    if(profile.electrical) {
      lines.push(settings.running_adm2===null?'Selected running density: not set; supplier value required':'Selected running density: '+number(settings.running_adm2)+' A/dm² ('+number(settings.running_adm2/densityFactors['A/in2'])+' A/in²)');
      if (settings.starting_adm2 !== null) lines.push('Selected starting density: '+number(settings.starting_adm2)+' A/dm²');
      lines.push('Calculated current at your selected density: '+(total===0?'no plated area selected':run===null?'density not set':'running '+number(run)+' A'));
      if (total>0 && start!==null) lines.push('Calculated starting current: '+number(start)+' A');
      const cc=settings.power_mode==='constant_current';
      lines.push('Power supply mode: '+(cc?'constant current':'constant voltage'));
      lines.push((cc?'Voltage limit: ':'Voltage setpoint: ')+(settings.voltage_v===null?'not set':number(settings.voltage_v)+' V'));
      lines.push(data.voltage_guidance);
    } else lines.push('Current and voltage: not applicable (area-only process)');
    lines.push(...warnings,data.limitation);
    lines.push(profile.reference);
    if(profile.source) lines.push('Source (reviewed 2026-10-10): '+profile.source);
    if(profile.density_range && settings.running_adm2!==null) {
      const factor={'A/dm2':1,'A/in2':10000/645.16,'A/ft2':10000/92903.04}[profile.density_unit];
      const density=settings.running_adm2/factor, [low,high]=profile.density_range;
      if(density<low*(1-1e-12)||density>high*(1+1e-12)) lines.push("Selected running density is outside this profile's published reference range.");
    }
    return lines.join('\n');
  }
  function update() {
    state=null; $('validation').textContent='';$('copy-status').textContent='';
    const unit=$('area-unit').value;
    const profile=data.profiles[$('profile').value], electrical=profile.electrical;
    ['density-unit','running','use-start','power-mode','voltage'].forEach(id=>$(id).disabled=!electrical);
    $('starting').disabled=!electrical||!$('use-start').checked;
    $('voltage-label').textContent=$('power-mode').value==='constant_current'?'Voltage limit (V)':'Voltage setpoint (V)';
    const warnings=Array.from(new Set(data.rows.flatMap(r=>r.warnings)));
    $('warnings').replaceChildren();
    [...warnings,data.limitation].forEach(w=>{const li=document.createElement('li');li.textContent=w;$('warnings').append(li);});
    $('reference').textContent=profile.reference;
    $('source').replaceChildren();
    if(profile.source) {
      const link=document.createElement('a');link.href=profile.source;link.textContent='Manufacturer source (reviewed 2026-10-10)';link.target='_blank';link.rel='noopener noreferrer';$('source').append(link);
    }
    controls.forEach(c=>{c.measured.textContent=c.row.error?'Unavailable':number(c.row.area_mm2/areaFactors[unit])+' '+areaLabels[unit];c.adjusted.textContent='—';});
    try {
      // Canonical densities change only when the corresponding field is edited.
      if(electrical && ['running','voltage'].some(id=>$(id).validity.badInput)) throw new Error('Complete the number or clear the field.');
      if (electrical && $('running').value.trim()!=='') numeric($('running'),'running density',0,true);
      if (electrical && $('use-start').checked) numeric($('starting'),'starting density',0,true);
      if (electrical && ((running!==null&&(!Number.isFinite(running)||running<=0))||($('use-start').checked&&(!Number.isFinite(starting)||starting<=0)))) throw new Error('Enter valid current densities.');
      const voltage=electrical && $('voltage').value.trim()!==''?numeric($('voltage'),'voltage',0,true):null;
      const settings={...data.settings,profile:$('profile').value,bath_label:$('bath').value,coating_label:$('coating').value,density_unit:densityUnit,area_unit:unit,running_adm2:electrical?running:null,starting_adm2:electrical&&$('use-start').checked?starting:null,power_mode:$('power-mode').value,voltage_v:voltage};
      let total=0;
      const choices=controls.map(c=>{
        let percent=Number(c.percent.value),excluded=Number(c.excluded.value),adjusted=0;
        if (c.include.checked) {
          if (c.row.error) throw new Error(c.row.error);
          percent=numeric(c.percent,'plated percentage');excluded=numeric(c.excluded,'excluded area');
          if (percent>100) throw new Error('Plated percentage must be between 0 and 100.');
          const available=c.row.area_mm2*(percent/100);
          const exclusion=excluded*100;
          if (!Number.isFinite(exclusion)||exclusion>available) throw new Error('Excluded area exceeds the percentage-adjusted area.');
          adjusted=available-exclusion;total+=adjusted;
          c.adjusted.textContent=number(adjusted/areaFactors[unit])+' '+areaLabels[unit];
        }
        // Unselected fields are not used; keep payload JSON finite even after a cleared field.
        return {row_id:c.row.row_id,selected:c.include.checked,plated_percent:Number.isFinite(percent)?percent:100,excluded_cm2:Number.isFinite(excluded)?excluded:0,adjusted};
      });
      const run=settings.running_adm2===null?null:total/10000*settings.running_adm2,start=settings.starting_adm2===null?null:total/10000*settings.starting_adm2;
      if (!Number.isFinite(total)||(run!==null&&!Number.isFinite(run))||(start!==null&&!Number.isFinite(start))) throw new Error('Calculation is outside the numeric range.');
      $('total').textContent=Object.keys(areaFactors).map(u=>number(total/areaFactors[u])+' '+areaLabels[u]).join(' / ');
      $('running-result').textContent=!electrical?'Not applicable':total>0&&run!==null?number(run)+' A':'—';$('starting-result').textContent=!electrical?'Not applicable':total>0&&start!==null?number(start)+' A':'—';
      if (total===0) $('validation').textContent='No plated area selected. Select and adjust a part to calculate current.';
      else if(electrical && run===null) $('validation').textContent='Running density not set. Area and voltage can be saved; running current is unknown.';
      $('report').value=report(settings,choices,total,run,start,warnings);
      state={settings,choices:choices.map(({adjusted,...c})=>c),total};
    } catch(error) {
      $('validation').textContent=error.message;$('total').textContent='—';$('running-result').textContent='—';$('starting-result').textContent='—';$('report').value='';
    }
    $('copy').disabled=!state||state.total===0;$('save').disabled=!state;
  }
  document.querySelectorAll('input,select').forEach(input=>input.addEventListener('input',()=>{
    if(['profile','bath','coating','density-unit','area-unit','running','starting','use-start','power-mode','voltage'].includes(input.id)) $('message').textContent='Settings have unsaved changes.';
    if(input.id==='running') running=input.value.trim()===''?null:Number(input.value)*densityFactors[densityUnit];
    if(input.id==='starting') starting=Number(input.value)*densityFactors[densityUnit];
    if(input.id==='use-start') $('starting').disabled=!input.checked;
    if(input.id==='power-mode') $('voltage').value='';
    if(input.id==='profile' && !data.profiles[input.value].electrical) {
      running=null;starting=null;$('running').value='';$('starting').value='';$('use-start').checked=false;$('voltage').value='';
    }
    update();
  }));
  $('density-unit').addEventListener('change',()=>{
    densityUnit=$('density-unit').value;
    if($('running').value.trim()!==''&&Number.isFinite(running)) $('running').value=String(running/densityFactors[densityUnit]);
    if($('starting').value.trim()!==''&&starting!==null&&Number.isFinite(starting)) $('starting').value=String(starting/densityFactors[densityUnit]);
    update();
  });
  $('use-profile').addEventListener('click',()=>{
    const profile=data.profiles[$('profile').value];
    running=profile.running_adm2;starting=null;
    $('bath').value=profile.label;
    $('running').value=running===null?'':String(running/densityFactors[densityUnit]);
    $('starting').value='';$('use-start').checked=false;
    $('voltage').value=profile.electrical&&$('power-mode').value==='constant_voltage'&&profile.voltage_v!==null?String(profile.voltage_v):'';
    $('message').textContent='Profile reference values loaded. Review the source and save settings when ready.';
    update();
  });
  $('copy').addEventListener('click',async()=>{
    if(!state||state.total===0) return;
    try{await navigator.clipboard.writeText($('report').value);$('copy-status').textContent='Report copied.';}
    catch{ $('report').focus();$('report').select();$('copy-status').textContent='Report selected. Press Ctrl+C to copy.'; }
  });
  $('save').addEventListener('click',()=>{
    if(!state) return;
    if(typeof window.orca?.submit==='function') window.orca.submit({action:'save',choices:state.choices,settings:state.settings});
    else $('message').textContent='Saving settings is available inside OrcaSlicer.';
  });
  $('close').addEventListener('click',()=>{
    if(typeof window.orca?.close==='function') window.orca.close();
    else if(typeof window.orca?.submit==='function') window.orca.submit({action:'close'});
  });
  update();
})();
