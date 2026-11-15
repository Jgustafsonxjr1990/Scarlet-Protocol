"""Decode every cue and check the sound installer in isolated fixtures."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,wave
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import sound_backend as backend


def audio():
    profiles=json.loads((ROOT/'profiles.json').read_text());catalog=json.loads((ROOT/'catalog.json').read_text());report=[];hashes=set()
    assert len(catalog)==39 and len(profiles)==3
    for key,profile in profiles.items():
        for item in catalog:
            path=ROOT/'WAV'/key/(item['name']+'.wav')
            with wave.open(str(path)) as f:
                assert (f.getnchannels(),f.getsampwidth(),f.getframerate())==(2,2,48000)
                pcm=np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2)/32768
            assert len(pcm)>4000 and len(pcm)<48000*2
            assert np.max(np.abs(pcm))<=.521 and np.max(np.abs(pcm))>.08
            assert np.max(np.abs(pcm.mean(axis=0)))<.002
            assert not pcm[0].any() and not pcm[-1].any()
            assert np.corrcoef(pcm.T)[0,1]>.65
            identity=hashlib.sha256(path.read_bytes()).hexdigest();assert identity not in hashes;hashes.add(identity)
            report.append({'edition':key,'cue':item['name'],'duration':len(pcm)/48000,'peak_dbfs':round(20*np.log10(np.max(np.abs(pcm))),2),'rms_dbfs':round(20*np.log10(np.sqrt(np.mean(pcm**2))),2)})
        files=list((ROOT/'themes'/profile['id']/'stereo').glob('*.oga'));assert len(files)==57
        for path in files:
            result=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar','48000','-ac','2','-'],check=True,capture_output=True)
            pcm=np.frombuffer(result.stdout,'<f4');assert len(pcm) and np.isfinite(pcm).all()
            assert np.abs(pcm).max()<.75,(path,np.abs(pcm).max())
    (ROOT/'audio-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: 117 distinct stereo masters; 171 Ogg files decode; duration, fades, DC, peaks and mono compatibility')


def installer():
    backend.HERE=ROOT;backend.program=lambda name:name
    values={};calls=[];fail={'write':False,'readback':False}
    def native(argv):
        calls.append(argv);key=argv[argv.index('--key')+1]
        if argv[0]=='kreadconfig6':return values.get(key,argv[-1])
        if key=='Enable' and fail['write']:fail['write']=False;raise RuntimeError('simulated settings failure')
        if argv[-1]=='--delete':values.pop(key,None)
        else:values[key]='OtherTheme' if key=='Theme' and fail['readback'] and argv[-1].startswith('scarlet-protocol-cyber2') else argv[-1]
        return ''
    backend.run=native
    with tempfile.TemporaryDirectory(prefix='scarlet-sound-test-') as directory:
        root=Path(directory);data=root/'data';config=root/'config';state=root/'state'
        assert backend.selection(config)=={'Theme':None,'Enable':None}
        first=backend.apply(data,config,state);assert first['changed']==3
        assert values=={'Theme':'scarlet-protocol-cyber2','Enable':'true'}
        backups=len(list(state.glob('before-sound-selection-*')))
        repeat=backend.apply(data,config,state);assert repeat['current'] and repeat['backup'] is None
        assert len(list(state.glob('before-sound-selection-*')))==backups
        target=data/'sounds/scarlet-protocol-cyber2/stereo/message.oga';target.write_bytes(b'previous customized audio')
        changed=backend.apply(data,config,state,'overdrive');assert changed['changed']==1
        backend.restore(data,config,Path(changed['backup']));assert values['Theme']=='scarlet-protocol-cyber2'
        assert target.read_bytes()==b'previous customized audio'
        backend.restore(data,config,Path(first['backup']));assert values=={} and not target.exists()
        values.update(Theme='ocean',Enable='false');original=dict(values)
        for failure in ('write','readback'):
            fail[failure]=True
            try:backend.apply(data,config,state)
            except RuntimeError:pass
            else:raise AssertionError('Expected '+failure+' failure')
            fail[failure]=False
            assert values==original and not (data/'sounds/scarlet-protocol-cyber2').exists()
        path=data/'sounds/scarlet-protocol-cyber2';path.mkdir();(path/'index.theme').write_text('Name=Unrelated')
        try:backend.install(data,state)
        except ValueError:pass
        else:raise AssertionError('Unrelated theme was overwritten')
        assert (path/'index.theme').read_text()=='Name=Unrelated'
        shutil.rmtree(path);backend.apply(data,config,state)
        changed_paths=[data/'sounds'/name/'stereo/message.oga' for name in ('scarlet-protocol-cyber2','scarlet-protocol-cyber2-night')]
        for index,p in enumerate(changed_paths):p.write_bytes(('custom audio '+str(index)).encode())
        before=[p.read_bytes() for p in changed_paths];prior=dict(values);original_rename=Path.rename
        def fail_second(self,target):
            if self.name=='scarlet-protocol-cyber2-night' and '.scarlet-sound-stage-' in str(self):raise OSError('simulated staged rename failure')
            return original_rename(self,target)
        with patch.object(Path,'rename',fail_second):
            try:backend.install(data,state)
            except OSError:pass
            else:raise AssertionError('Expected file-stage failure')
        assert [p.read_bytes() for p in changed_paths]==before and values==prior

        assert all(str(config/'kdeglobals') in argv for argv in calls)
    print('PASS: fresh/repeat/modified-file upgrades, all editions installed, absent settings and audio restored, write/readback rollback, unrelated theme protection')


if __name__=='__main__':audio();installer()
