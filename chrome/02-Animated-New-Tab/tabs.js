const $ = id => document.getElementById(id);
export class TabPanel {
  constructor(getState, say) {
    this.getState = getState;
    this.say = say;
    this.enabled = false;
    this.all = [];
    this.refreshTimer = null;
    $('enable-tabs').onclick = () => this.enable();
    $('tab-filter').oninput = () => this.render();
  }
  start() {
    this.refresh();
    if (!globalThis.chrome?.tabs) return;
    for (const event of ['onCreated', 'onRemoved', 'onActivated', 'onUpdated']) {
      chrome.tabs[event]?.addListener(() => {
        clearTimeout(this.refreshTimer);
        this.refreshTimer = setTimeout(() => this.refresh(), 180);
      });
    }
  }
  async hasPermission() {
    try { return Boolean(await chrome.permissions.contains({permissions: ['tabs']})); }
    catch { return false; }
  }
  async enable() {
    try {
      const granted = await chrome.permissions.request({permissions: ['tabs']});
      if (granted) this.refresh();
      else this.say('Tab access was not granted.');
    } catch { this.say('Open the installed extension to use open-tab controls.'); }
  }
  async refresh() {
    if (!this.getState().widgets.tabs || document.hidden) return;
    this.enabled = await this.hasPermission();
    $('enable-tabs').hidden = this.enabled;
    $('tab-filter').hidden = !this.enabled;
    if (!this.enabled) {
      $('tab-empty').textContent = 'Enable access to find, pin, mute and switch between your tabs.';
      $('tab-empty').hidden = false;
      $('tab-list').replaceChildren();
      $('tab-count').textContent = '';
      return;
    }
    try {
      this.all = await chrome.tabs.query({currentWindow: true});
      this.render();
    } catch {
      $('tab-empty').textContent = 'Tabs are unavailable in this window.';
      $('tab-empty').hidden = false;
    }
  }
  async update(id, changes) {
    try {
      await chrome.tabs.update(id, changes);
      await this.refresh();
    } catch { this.say('That tab is no longer available.'); }
  }
  render() {
    const filter = $('tab-filter').value.toLowerCase().trim();
    const filtered = this.all.filter(tab => (tab.title || tab.url || '').toLowerCase().includes(filter));
    $('tab-count').textContent = this.all.length + ' open';
    $('tab-list').replaceChildren();
    $('tab-empty').textContent = filter ? 'No matching tabs.' : 'No other tabs open.';
    $('tab-empty').hidden = filtered.length > 0;
    for (const tab of filtered.slice(0, 60)) {
      const row = document.createElement('div');
      row.className = 'tab-card' + (tab.active ? ' active' : '');
      const open = document.createElement('button');
      open.className = 'tab-open';
      open.textContent = tab.title || tab.url || 'Untitled tab';
      open.title = tab.title || tab.url || '';
      open.onclick = () => this.update(tab.id, {active: true});
      row.append(open);
      for (const [kind, label, pressed, changes] of [
        ['pin', tab.pinned ? 'Unpin' : 'Pin', Boolean(tab.pinned), {pinned: !tab.pinned}],
        ['mute', tab.mutedInfo?.muted ? 'Unmute' : 'Mute', Boolean(tab.mutedInfo?.muted), {muted: !tab.mutedInfo?.muted}]
      ]) {
        const button = document.createElement('button');
        button.className = 'tab-' + kind;
        button.textContent = label;
        button.setAttribute('aria-label', label + ' ' + (tab.title || 'tab'));
        button.setAttribute('aria-pressed', String(pressed));
        button.onclick = () => this.update(tab.id, changes);
        row.append(button);
      }
      const close = document.createElement('button');
      close.className = 'tab-close';
      close.textContent = '×';
      close.setAttribute('aria-label', 'Close ' + (tab.title || 'tab'));
      close.onclick = () => chrome.tabs.remove(tab.id).then(() => this.refresh()).catch(() => this.say('That tab has closed.'));
      row.append(close);
      $('tab-list').append(row);
    }
  }
}
