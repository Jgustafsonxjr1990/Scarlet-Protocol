const $ = id => document.getElementById(id);

export class Workspace {
  constructor(getState, save, say, tabs) {
    this.getState = getState;
    this.save = save;
    this.say = say;
    this.tabs = tabs;
    this.results = [];
    this.selected = 0;
    this.timerCue = new Audio('sounds/focus-complete.oga');
    this.timerCue.volume = .55;
    this.installTasks();
    this.installPalette();
    this.installGlow();
    $('sound-cue').onchange = () => {
      this.getState().soundCue = $('sound-cue').checked;
      this.save();
    };
    $('test-cue').onclick = () => this.playCue();
    $('show-today').onchange = () => {
      this.getState().widgets.today = $('show-today').checked;
      this.save();
      this.sync();
    };
    this.sync();
  }

  playCue() {
    this.timerCue.currentTime = 0;
    this.timerCue.play().catch(() => this.say('Use Test sound to allow audio on this dashboard.'));
  }

  completeFocus(completedEnd) {
    if (!this.getState().soundCue) return;
    const playOnce = () => {
      const key = 'scarlet-last-focus-cue';
      if (localStorage.getItem(key) === String(completedEnd)) return;
      localStorage.setItem(key, String(completedEnd));
      this.playCue();
    };
    if (navigator.locks) {
      navigator.locks.request('scarlet-focus-cue', {ifAvailable: true}, lock => {
        if (lock) playOnce();
      }).catch(() => this.playCue());
    } else playOnce();
  }

  sync() {
    const state = this.getState();
    $('sound-cue').checked = state.soundCue;
    $('show-today').checked = state.widgets.today;
    $('today-widget').hidden = !state.widgets.today;
    this.renderTasks();
  }

  installTasks() {
    $('task-form').onsubmit = event => {
      event.preventDefault();
      const title = $('task-title').value.trim();
      if (!title) return;
      const tasks = this.getState().tasks;
      if (tasks.length >= 30) {
        this.say('Your checklist holds 30 items. Clear completed items to make room.');
        return;
      }
      tasks.push({id: crypto.randomUUID(), title, done: false});
      this.save();
      $('task-title').value = '';
      this.renderTasks();
    };
    $('clear-tasks').onclick = () => {
      const state = this.getState();
      state.tasks = state.tasks.filter(task => !task.done);
      this.save();
      this.renderTasks();
    };
  }

  renderTasks() {
    const tasks = this.getState().tasks;
    const completed = tasks.filter(task => task.done).length;
    $('task-progress').textContent = completed + ' / ' + tasks.length;
    $('task-empty').hidden = tasks.length > 0;
    $('clear-tasks').disabled = completed === 0;
    $('task-list').replaceChildren();
    for (const task of tasks) {
      const row = document.createElement('li');
      row.className = task.done ? 'task done' : 'task';
      const label = document.createElement('label');
      const toggle = document.createElement('input');
      toggle.type = 'checkbox';
      toggle.checked = task.done;
      toggle.onchange = () => {
        task.done = toggle.checked;
        this.save();
        this.renderTasks();
      };
      const title = document.createElement('span');
      title.textContent = task.title;
      label.append(toggle, title);
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'task-remove';
      remove.textContent = '×';
      remove.setAttribute('aria-label', 'Remove ' + task.title);
      remove.onclick = () => {
        const state = this.getState();
        state.tasks = state.tasks.filter(item => item.id !== task.id);
        this.save();
        this.renderTasks();
      };
      row.append(label, remove);
      $('task-list').append(row);
    }
  }

  installPalette() {
    $('commands').onclick = () => this.openPalette();
    document.addEventListener('keydown', event => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        if ($('command-dialog').open) $('command-dialog').close();
        else if (!document.querySelector('dialog[open]')) this.openPalette();
      }
    });
    $('command-query').oninput = () => {
      this.selected = 0;
      this.renderCommands();
    };
    $('command-query').onkeydown = event => {
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        const count = this.results.length;
        if (!count) return;
        this.selected = (this.selected + (event.key === 'ArrowDown' ? 1 : count - 1)) % count;
        this.markSelected();
      } else if (event.key === 'Enter') {
        event.preventDefault();
        this.activate(this.results[this.selected]);
      }
    };
  }

  openPalette() {
    $('command-query').value = '';
    this.selected = 0;
    this.renderCommands();
    $('command-dialog').showModal();
    $('command-query').focus();
  }

  commands() {
    const actions = [...document.querySelectorAll('#quick-actions .action')].map(button => ({
      title: button.textContent, detail: 'Chrome action', run: () => button.click()
    }));
    actions.push(
      {title: 'Customize dashboard', detail: 'Appearance', run: () => $('customize').click()},
      {title: 'Focus view', detail: 'Workspace', run: () => $('focus-mode').click()},
      {title: 'Start or pause focus timer', detail: 'Timer', run: () => $('timer-start').click()},
      {title: 'Search the web', detail: 'Search', run: () => $('query').focus()}
    );
    for (const shortcut of this.getState().shortcuts) {
      actions.push({
        title: shortcut.name,
        detail: new URL(shortcut.url).hostname,
        run: () => location.assign(shortcut.url)
      });
    }
    if (this.tabs.enabled) {
      for (const tab of this.tabs.all) {
        actions.push({
          title: tab.title || 'Untitled tab', detail: 'Open tab',
          run: () => chrome.tabs.update(tab.id, {active: true}).catch(() => this.say('That tab has closed.'))
        });
      }
    }
    return actions;
  }

  renderCommands() {
    const query = $('command-query').value.trim().toLowerCase();
    this.results = this.commands().filter(item => (item.title + ' ' + item.detail).toLowerCase().includes(query)).slice(0, 20);
    $('command-results').replaceChildren();
    $('command-empty').hidden = this.results.length !== 0;
    for (const [index, item] of this.results.entries()) {
      const button = document.createElement('button');
      button.type = 'button';
      button.id = 'command-item-' + index;
      button.className = 'command-result';
      button.setAttribute('role', 'option');
      const title = document.createElement('span');
      const detail = document.createElement('small');
      title.textContent = item.title;
      detail.textContent = item.detail;
      button.append(title, detail);
      button.onclick = () => this.activate(item);
      $('command-results').append(button);
    }
    this.markSelected();
  }

  markSelected() {
    const buttons = [...$('command-results').children];
    buttons.forEach((button, index) => {
      button.classList.toggle('selected', index === this.selected);
      button.setAttribute('aria-selected', String(index === this.selected));
    });
    const current = buttons[this.selected];
    $('command-query').setAttribute('aria-activedescendant', current?.id || '');
    current?.scrollIntoView({block: 'nearest'});
  }

  activate(item) {
    if (!item) return;
    $('command-dialog').close();
    item.run();
  }

  installGlow() {
    let pending = false;
    let position;
    document.addEventListener('pointermove', event => {
      const state = this.getState();
      if (state.paused || state.motion === 'off' || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const card = event.target.closest('.panel');
      if (!card) return;
      position = {card, x: event.clientX, y: event.clientY};
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => {
        pending = false;
        const {card, x, y} = position;
        const bounds = card.getBoundingClientRect();
        card.style.setProperty('--spot-x', (x - bounds.left) + 'px');
        card.style.setProperty('--spot-y', (y - bounds.top) + 'px');
      });
    }, {passive: true});
  }
}
