// Exercise the panel replacement script against Plasma's documented object API.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');
let nextId = 10;
function makePanel() {
    const panel = {id: 1, items: []};
    panel.addWidget = function(type) {
        const widget = {id: nextId++, type, currentConfigGroup: ['General'], settings: {}, globalShortcut: '',
            get configKeys() { return Object.keys(this.settings); },
            get index() { return panel.items.indexOf(this); },
            set index(index) { panel.items.splice(panel.items.indexOf(this),1); panel.items.splice(index,0,this); },
            readConfig(key) { return this.settings[key]; },
            writeConfig(key,value) { this.settings[key] = value; },
            reloadConfig() {},
            remove() { panel.items.splice(panel.items.indexOf(this),1); }};
        panel.items.push(widget);return widget;
    };
    panel.widgets = () => panel.items.slice();
    return panel;
}
const script = fs.readFileSync(path.join(__dirname,'panel_tools.js'),'utf8');
const panel = makePanel();
const launcher = panel.addWidget('org.kde.plasma.kickoff');
launcher.settings.favoriteApps = ['applications:org.kde.konsole.desktop'];
launcher.globalShortcut = 'Alt+F1';
const tray = panel.addWidget('org.kde.plasma.systemtray');
const clock = panel.addWidget('org.kde.plasma.digitalclock');
const output = [];
const context = vm.createContext({panels: () => [panel], print: message => output.push(JSON.parse(message))});
vm.runInContext(script,context);
assert.deepStrictEqual(panel.items.map(x=>x.type),['org.scarletprotocol.launcher','org.kde.plasma.systemtray','org.scarletprotocol.clock']);
assert.deepStrictEqual(panel.items[0].settings.favoriteApps,['applications:org.kde.konsole.desktop']);
assert.strictEqual(panel.items[0].globalShortcut,'Alt+F1');
assert.strictEqual(panel.items[1],tray);
assert.strictEqual(output[0].replaced,2);
vm.runInContext(script,context);
assert.strictEqual(output[1].replaced,0);
assert.strictEqual(panel.items.length,3);
const failed = makePanel();
failed.addWidget('org.kde.plasma.kicker');
failed.addWidget('org.kde.plasma.digitalclock');
const originalAdd=failed.addWidget;
failed.addWidget = type => type==='org.scarletprotocol.clock'?null:originalAdd(type);
assert.throws(() => vm.runInNewContext(script,{panels: () => [failed],print: ()=>{}}));
assert.strictEqual(failed.items[0].type,'org.kde.plasma.kicker');
assert.strictEqual(failed.items[1].type,'org.kde.plasma.digitalclock');
assert.strictEqual(failed.items.length,2);
console.log('PASS: panel positions, unrelated tray, favorites and launcher shortcut retained; repeat creates no duplicates; failed creation keeps original');
