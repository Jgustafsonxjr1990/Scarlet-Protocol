"""Per-user sound-theme install, selection verification and reversible updates."""
from pathlib import Path
import json,os,shutil,subprocess,tempfile,sys

HERE=Path(__file__).resolve().parent
ABSENT='__SCARLET_SOUND_ABSENT_2__'


def native_environment():
    environment=os.environ.copy()
    if getattr(sys,'frozen',False):
        if 'LD_LIBRARY_PATH_ORIG' in environment:environment['LD_LIBRARY_PATH']=environment['LD_LIBRARY_PATH_ORIG']
        else:environment.pop('LD_LIBRARY_PATH',None)
        for key in ('QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','QML_IMPORT_PATH','QML2_IMPORT_PATH','PYTHONHOME','PYTHONPATH'):environment.pop(key,None)
    return environment


def program(name):
    result=shutil.which(name)
    if not result:raise RuntimeError('Open Sound Studio on your Plasma 6 desktop; missing '+name+'.')
    return result


def run(argv):
    return subprocess.run(argv,check=True,text=True,capture_output=True,timeout=30,env=native_environment()).stdout.strip()


def selection(config_home):
    reader=program('kreadconfig6');result={}
    for key in ('Theme','Enable'):
        value=run([reader,'--file',str(config_home/'kdeglobals'),'--group','Sounds','--key',key,'--default',ABSENT])
        result[key]=None if value==ABSENT else value
    return result


def set_selection(config_home,values):
    writer=program('kwriteconfig6')
    for key in ('Theme','Enable'):
        value=values[key]
        args=[writer,'--notify','--file',str(config_home/'kdeglobals'),'--group','Sounds','--key',key]
        if value is None:args+=['--delete']
        elif key=='Enable':args+=['--type','bool',value]
        else:args+=[value]
        run(args)
    if selection(config_home)!=values:raise RuntimeError('Plasma did not retain the requested sound settings.')


def same_tree(a,b):
    if not b.is_dir():return False
    one={p.relative_to(a) for p in a.rglob('*') if p.is_file()}
    two={p.relative_to(b) for p in b.rglob('*') if p.is_file()}
    return one==two and all((a/p).read_bytes()==(b/p).read_bytes() for p in one)


def install(data_home,state_home):
    profiles=json.loads((HERE/'profiles.json').read_text());sources=[]
    for item in profiles.values():
        source=HERE/'themes'/item['id'];target=data_home/'sounds'/item['id']
        if not source.is_dir() or source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')):raise ValueError('Incomplete sound collection: '+item['id'])
        if target.is_symlink() or target.exists() and not target.is_dir():raise ValueError('The sound-theme target is not a regular directory.')
        if target.exists():
            index=target/'index.theme'
            if any(p.is_symlink() for p in target.rglob('*')) or not index.is_file() or 'Name=Scarlet Protocol — ' not in index.read_text():raise ValueError('The installed directory has a different identity.')
        if not same_tree(source,target):sources.append((source,target))
    if not sources:return {'changed':0,'backup':None}
    state_home.mkdir(parents=True,exist_ok=True)
    backup=Path(tempfile.mkdtemp(prefix='before-cyber-sounds-',dir=state_home));backup.chmod(0o700)
    target_parent=data_home/'sounds';target_parent.mkdir(parents=True,exist_ok=True)
    completed=[]
    with tempfile.TemporaryDirectory(prefix='.scarlet-sound-stage-',dir=target_parent) as temporary:
        temporary=Path(temporary)
        for source,target in sources:shutil.copytree(source,temporary/target.name)
        try:
            for source,target in sources:
                previous=backup/'themes'/target.name
                if target.exists():previous.parent.mkdir(exist_ok=True);shutil.copytree(target,previous)
                completed.append((target,previous))
                if target.exists():shutil.rmtree(target)
                (temporary/target.name).rename(target)
        except Exception:
            for target,previous in reversed(completed):
                if target.exists():shutil.rmtree(target)
                if previous.exists():shutil.copytree(previous,target)
            raise
    (backup/'installed.json').write_text(json.dumps([str(target) for _,target in sources],indent=2)+'\n')
    return {'changed':len(sources),'backup':str(backup)}


def rollback_files(result,data_home):
    if not result.get('backup'):return
    backup=Path(result['backup'])
    for raw in json.loads((backup/'installed.json').read_text()):
        target=Path(raw)
        if target.parent!=data_home/'sounds' or not target.name.startswith('scarlet-protocol-cyber2'):raise ValueError('Invalid sound backup target.')
        if target.is_symlink():raise ValueError('The sound target was replaced by a symbolic link.')
        if target.exists():shutil.rmtree(target)
        previous=backup/'themes'/target.name
        if previous.exists():shutil.copytree(previous,target)


def apply(data_home,config_home,state_home,profile='protocol'):
    if hasattr(os,'geteuid') and os.geteuid()==0:raise RuntimeError('Open Sound Studio as your normal user, without sudo.')
    program('kreadconfig6');program('kwriteconfig6')
    profiles=json.loads((HERE/'profiles.json').read_text());theme=profiles[profile]['id']
    previous=selection(config_home);selected={'Theme':theme,'Enable':'true'}
    result=install(data_home,state_home)
    if previous==selected and result['changed']==0:return dict(result,theme=theme,current=True)
    state_home.mkdir(parents=True,exist_ok=True)
    backup=Path(tempfile.mkdtemp(prefix='before-sound-selection-',dir=state_home));backup.chmod(0o700)
    (backup/'selection.json').write_text(json.dumps({'previous':previous,'files':result},indent=2)+'\n')
    try:set_selection(config_home,selected)
    except Exception:
        try:set_selection(config_home,previous)
        except Exception:pass
        rollback_files(result,data_home);raise
    return dict(result,backup=str(backup),theme=theme,current=False)


def restore(data_home,config_home,backup):
    record=json.loads((backup/'selection.json').read_text());previous=record['previous']
    if set(previous)!=set(('Theme','Enable')) or any(value is not None and not isinstance(value,str) for value in previous.values()):raise ValueError('Invalid previous sound settings.')
    set_selection(config_home,previous)
    rollback_files(record['files'],data_home)
    return previous


def player_command(path):
    for name in ('pw-play','paplay','aplay'):
        if exe:=shutil.which(name):return [exe,str(path)]
    raise RuntimeError('No system audio player was found. Use Open Sound Browser to audition the WAV files in your browser.')
