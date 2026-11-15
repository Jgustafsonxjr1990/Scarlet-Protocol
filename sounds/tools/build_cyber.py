"""Original, deterministic cyberpunk UI sound design. CC0-1.0."""
from pathlib import Path
import hashlib,json,subprocess,wave
import numpy as np
from scipy.signal import butter,sosfilt,resample_poly

ROOT=Path(__file__).resolve().parents[1]
RATE=48000
SR=96000
ALIASES={"desktop-logout-cancel":"window-unminimized","bell":"dialog-information","bell-window-system":"dialog-information","dialog-error-critical":"dialog-error-serious","battery-full":"outcome-success","complete-media-burn":"outcome-success","complete-media-error":"outcome-failure","completion-success":"outcome-success","completion-fail":"outcome-failure","completion-partial":"dialog-question","message-highlight":"message-attention","screen-capture":"button-pressed","suspend-start":"window-minimized","suspend-resume":"window-unminimized","system-ready":"desktop-login","desktop-screen-lock":"service-logout","desktop-screen-unlock":"service-login"}
PROFILES={
    'protocol':{'title':'Cyber Circuit','id':'scarlet-protocol-cyber2','drive':1.6,'digital':.18,'gain':1.,'cutoff':7200},
    'night':{'title':'Night Shift','id':'scarlet-protocol-cyber2-night','drive':1.2,'digital':.055,'gain':.56,'cutoff':4300},
    'overdrive':{'title':'Overdrive','id':'scarlet-protocol-cyber2-overdrive','drive':2.8,'digital':.32,'gain':1.04,'cutoff':7600},
}
D=146.8324;F=174.6141;A=220.;C=261.6256;E=329.6276


def envelope(t,duration,attack=.003,decay=4):
    return (1-np.exp(-t/attack))*np.exp(-decay*t/duration)*np.clip((duration-t)/.018,0,1)


def voice(freq,duration,rng,drive=1.6,kind='fm',end=None):
    t=np.arange(round(SR*duration))/SR
    if end is None:end=freq*.96
    hz=freq*(end/freq)**(t/duration);phase=2*np.pi*np.cumsum(hz)/SR
    env=envelope(t,duration)
    if kind=='fm':
        mod=(3.7*np.exp(-t/.042)+.7)*np.sin(phase*2.01)
        carrier=.75*np.sin(phase+mod)+.3*np.sin(phase*.5)+.12*np.sin(phase*3.01)
        return np.tanh(carrier*drive)*env
    if kind=='bass':
        tri=2/np.pi*np.arcsin(np.sin(phase))
        carrier=np.sin(phase)+.3*tri+.1*np.sin(phase*2.004)
        return np.tanh(carrier*drive)*envelope(t,duration,decay=2.7)
    if kind=='metal':
        carrier=np.sin(phase)*.5+np.sin(phase*1.49)*.24+np.sin(phase*2.127)*.12
        return np.tanh(carrier*drive)*envelope(t,duration,attack=.001,decay=6)
    if kind=='sweep':
        noise=sosfilt(butter(2,[650,4200],btype='bandpass',fs=SR,output='sos'),rng.normal(size=len(t)))
        carrier=np.sin(phase+.5*np.sin(phase*2))*.66+noise*.18
        return np.tanh(carrier*drive)*np.sin(np.pi*t/duration)**1.2
    raise ValueError(kind)


def data_burst(duration,rng,drive):
    t=np.arange(round(SR*duration))/SR
    n=sosfilt(butter(2,[850,5600],btype='bandpass',fs=SR,output='sos'),rng.normal(size=len(t)))
    gate=(np.sin(2*np.pi*83*t)>-.1).astype(float)
    return np.tanh((n*.4+np.sin(2*np.pi*1370*t)*.14)*drive)*gate*envelope(t,duration,attack=.0008,decay=5)


def design(name,profile):
    opts=PROFILES[profile];rng=np.random.default_rng(int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'little'))
    layers=[];description='';role='Notification';family='System';peak=.38
    def add(at,hz,duration=.19,gain=.5,kind='fm',end=None,pan=0):layers.append((at,voice(hz,duration,rng,opts['drive'],kind,end)*gain,pan))
    def data(at=0,duration=.06,gain=.14,pan=0):layers.append((at,data_burst(duration,rng,opts['drive'])*gain,pan))
    if name=='desktop-login':
        family='Session';description='Boot handshake, rising scan, distorted sub pulse and a resolved D-minor signal.';peak=.5
        data(0,.12,.18,-.12);data(.14,.08,.15,.12)
        add(.03,76,.64,.45,'bass',D/2);add(.20,130,.58,.20,'sweep',780)
        for at,hz,gain in [(.30,D,.45),(.41,F,.35),(.52,A,.38),(.78,D*2,.36),(.78,F*2,.22),(.78,A*2,.19)]:add(at,hz,.75,gain,pan=.12 if hz==F else -.08)
        data(.66,.05,.13);add(.91,D,.72,.22,'bass')
    elif name in ('desktop-logout','system-shutdown'):
        family='Session';description='Descending lock sequence with a low filtered power-down.';peak=.43
        for i,hz in enumerate([A*2,F*2,D*2,D]):add(i*.11,hz,.32,.38)
        add(.25,280,.52,.28,'sweep',55);data(.08,.05,.1);add(.40,D/2,.40,.26,'bass')
    elif name in ('service-login','service-logout'):
        family='Session';description='Two-stage encrypted access handshake.'
        sequence=[D*2,A*2] if name=='service-login' else [A*2,D*2]
        for i,hz in enumerate(sequence):add(i*.075,hz,.18,.4)
        data(0,.035,.10)
    elif name.startswith('button-') or name in ('menu-click','menu-popup','audio-volume-change','trash-empty'):
        role='Support';family='Interface';peak=.23
        description='Short metallic contact with a dry digital edge.'
        f={'button-pressed':640,'button-released':440,'button-pressed-modifier':830,'menu-click':750,'menu-popup':360,'audio-volume-change':585,'trash-empty':170}[name]
        add(0,f,.075 if name!='menu-popup' else .13,.6,'metal',f*.7)
        data(0,.031,.14)
        if name in ('menu-popup','trash-empty'):add(.045,f*.6,.12,.3,'bass')
    elif name.startswith('window-'):
        role='Support';family='Windows';peak=.29
        description='Filtered energy sweep with a brief data tear and a low mechanical lock.'
        upward=name in ('window-open','window-maximized','window-unminimized')
        start,end=(100,660) if upward else (620,100)
        duration=.24 if name=='window-maximized' else .18
        add(0,start,duration,.3,'sweep',end);data(.028,.045,.16,-.15)
        add(duration*.65,D if upward else D/2,.13,.38,'bass');add(.04,A*2,.065,.11,'metal')
    elif name in ('dialog-warning','dialog-warning-auth','dialog-error','dialog-error-serious','message-attention','battery-low','battery-caution','network-connectivity-lost','outcome-failure'):
        role='Alert';family='Alerts';peak=.45
        description='Gated low synth warning; pitch and rhythm identify the event.'
        seq={
            'dialog-warning':[D*2,F*2,D*2], 'dialog-warning-auth':[A,D*2,A*2],
            'dialog-error':[D,155.563,D], 'dialog-error-serious':[D,155.563,D,155.563,D],
            'message-attention':[F*4,D*4], 'battery-low':[A,F,D], 'battery-caution':[F,D,D],
            'network-connectivity-lost':[A*2,F*2,D*2], 'outcome-failure':[A,155.563,D],
        }[name]
        gap=.12 if name not in ('battery-caution','dialog-error-serious') else .15
        for i,hz in enumerate(seq):
            add(i*gap,hz,.18,.40,'bass' if hz<180 else 'fm',hz*.98,pan=(-.1,.1)[i%2])
            data(i*gap,.035,.09)
        if name=='dialog-error-serious':add(.05,D/2,.7,.2,'bass')
    elif name=='alarm-clock-elapsed':
        role='Alert';family='Alerts';peak=.43;description='Two syncopated scan bursts resolving into the completion motif.'
        for i,hz in enumerate([D*2,A*2,F*2,D*4,A*2]):add(i*.13+(0 if i<3 else .10),hz,.22,.42)
        data(0,.065,.13);data(.48,.065,.13)
    else:
        family='Messages' if name.startswith('message') else 'System'
        description='Crisp FM packet tones, small stereo reflections and a low circuit accent.'
        sequence={
            'message':[F*2,A*2], 'message-new-instant':[D*4,F*4], 'message-new-email':[D*2,F*2,A*2],
            'message-sent-instant':[A*2,D*4], 'dialog-information':[D*2,A*2], 'dialog-question':[D*2,E*2],
            'power-plug':[D,A,D*2], 'power-unplug':[D*2,A,D],
            'device-added':[D*4,A*4], 'device-removed':[A*4,D*4],
            'network-connectivity-established':[D*2,F*2,A*2], 'outcome-success':[D*2,A*2,D*4],
        }[name]
        gap=.065 if name in ('message-new-instant','message-sent-instant','device-added','device-removed') else .095
        for i,hz in enumerate(sequence):add(i*gap,hz,.20 if len(sequence)<3 else .23,.42,pan=(-.12,.12)[i%2])
        data(0,.035,.09)
        if name in ('power-plug','power-unplug','outcome-success'):add(.07,D/2,.25,.18,'bass')
    end=max(at+len(x)/SR for at,x,_ in layers)+.07
    out=np.zeros((round(end*SR),2))
    for at,mono,pan in layers:
        offset=round(at*SR);out[offset:offset+len(mono),0]+=mono*np.sqrt((1-pan)/2);out[offset:offset+len(mono),1]+=mono*np.sqrt((1+pan)/2)
    # Quiet sample-held detail adds a digital grain behind the primary transient.
    held=np.repeat(np.round(out[::8]*31)/31,8,axis=0)[:len(out)]
    out=out*(1-opts['digital'])+held*opts['digital']
    dry=out.copy()
    for delay,gain in [(.027,.105),(.061,.045)]:
        k=round(delay*SR);out[k:]+=dry[:-k,::-1]*gain
    out=sosfilt(butter(3,opts['cutoff'],fs=SR,output='sos'),out,axis=0)
    out=sosfilt(butter(2,48,btype='highpass',fs=SR,output='sos'),out,axis=0)
    out=resample_poly(out,1,2,axis=0);out-=out.mean(axis=0)
    fade=min(round(.010*RATE),len(out)//4);out[:fade]*=np.linspace(0,1,fade)[:,None];out[-fade:]*=np.linspace(1,0,fade)[:,None]
    maximum=np.abs(out).max();out*=peak*opts['gain']/maximum if maximum else 1
    return out,role,family,description


def wav(path,x):
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(np.rint(x*32767).astype('<i2').tobytes())


def main():
    legacy=json.loads((ROOT/'legacy-catalog.json').read_text());catalog=[];signals={}
    for profile,opts in PROFILES.items():
        theme=ROOT/'themes'/opts['id'];stereo=theme/'stereo';stereo.mkdir(parents=True,exist_ok=True)
        (theme/'index.theme').write_text('[Sound Theme]\nName=Scarlet Protocol — '+opts['title']+'\nComment=Cyber Circuit 2: FM pulses, circuit glitches and filtered power sweeps\nInherits=freedesktop\nDirectories=stereo\nExample=theme-demo\n\n[stereo]\nOutputProfile=stereo\n')
        for item in legacy:
            name=item['name'];x,role,family,description=design(name,profile);signals[profile,name]=x
            path=ROOT/'WAV'/profile/(name+'.wav');wav(path,x)
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(path),'-c:a','libvorbis','-q:a','6',str(stereo/(name+'.oga'))],check=True)
            (stereo/(name+'.sound')).write_text('[Sound Data]\nDisplayName='+item['title'].replace('Soft click','Circuit click')+'\n')
            if profile=='protocol':catalog.append(dict(name=name,title=item['title'].replace('Soft click','Circuit click'),category=role,family=family,description=description,duration=round(len(x)/RATE,3)))
        for name,target in ALIASES.items():(stereo/(name+'.oga')).write_bytes((stereo/(target+'.oga')).read_bytes())
        selected=['desktop-login','button-pressed','message','message-new-instant','message-new-email','power-plug','device-added','window-open','window-minimized','window-maximized','outcome-success','dialog-warning','dialog-error','alarm-clock-elapsed','desktop-logout']
        demo=np.vstack([piece for name in selected for piece in (signals[profile,name],np.zeros((round(.24*RATE),2)))])
        wav(ROOT/('Theme-Demo'+('' if profile=='protocol' else '-'+profile)+'.wav'),demo)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/('Theme-Demo'+('' if profile=='protocol' else '-'+profile)+'.wav')),'-c:a','libvorbis','-q:a','6',str(stereo/'theme-demo.oga')],check=True)
        if profile=='protocol':
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'Theme-Demo.wav'),'-c:a','libmp3lame','-q:a','2',str(ROOT.parent/'Scarlet-Protocol-Sound-Preview.mp3')],check=True)
    (ROOT/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    (ROOT/'profiles.json').write_text(json.dumps(PROFILES,indent=2)+'\n')
    print(len(catalog),'original cues ×',len(PROFILES),'editions;',len(ALIASES),'aliases per edition')


if __name__=='__main__':main()
