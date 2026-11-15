from pathlib import Path
import subprocess
from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QJSEngine
ROOT=Path(__file__).resolve().parents[1]
parts=[ROOT/'tests/events.js',ROOT/'kwin6_effect_scarlet_vector_wake/contents/code/main.js',ROOT/'tests/assertions.js']
script='\n'.join(p.read_text() for p in parts)
p=subprocess.run(['node','-e',script],capture_output=True,text=True)
assert p.returncode==0,p.stderr
app=QCoreApplication([])
engine=QJSEngine();engine.installExtensions(QJSEngine.ConsoleExtension)
result=engine.evaluate(script,'scarlet-drag-regression.js')
assert not result.isError(),f'{result.toString()} line {result.property("lineNumber").toInt()}'
assert engine.globalObject().property('checksPassed').toBool()
print('PASS Node + Qt 6 QJSEngine: immediate attachment; 1000 updates without restart; no-argument signals; missing-start recovery; resize/lock/fullscreen/close/config/desktop cleanup; no stacking changes.')
