export const STORAGE_KEY = 'scarlet-protocol-v4';
export const DEFAULTS = {
  motion: 'subtle', glow: 65, scanlines: true, clock24: true, paused: false,
  density: 'comfortable', corner: 'rounded', reticle: true, edges: true,
  units: 'fahrenheit', engine: 'google', notes: '', soundCue: false,
  tasks: [], shortcuts: [],
  widgets: {today: true, system: true, weather: true, focus: true, tabs: true, workspace: true},
  order: ['tabs', 'workspace'], city: null, sensors: false,
  timer: {minutes: 25, remaining: 1500, end: 0}
};

export function website(value) {
  const raw = String(value).trim();
  if (!raw || /\s/.test(raw) || (/^[a-z][a-z0-9+.-]*:/i.test(raw) && !/^https?:\/\//i.test(raw))) return null;
  try {
    const url = new URL(/^https?:\/\//i.test(raw) ? raw : 'https://' + raw);
    return ['http:', 'https:'].includes(url.protocol) && url.hostname && !url.username && !url.password ? url.href : null;
  } catch {
    return null;
  }
}

export function sanitize(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) data = {};
  const state = structuredClone(DEFAULTS);
  for (const key of ['scanlines', 'clock24', 'paused', 'reticle', 'edges', 'sensors', 'soundCue']) {
    if (typeof data[key] === 'boolean') state[key] = data[key];
  }
  const choices = {
    motion: ['subtle', 'full', 'off'], density: ['comfortable', 'compact'],
    corner: ['soft', 'rounded', 'pill'], units: ['fahrenheit', 'celsius'],
    engine: ['google', 'duckduckgo', 'brave', 'bing']
  };
  for (const [key, allowed] of Object.entries(choices)) {
    if (allowed.includes(data[key])) state[key] = data[key];
  }
  if (Number.isFinite(data.glow)) state.glow = Math.min(100, Math.max(0, data.glow));
  if (typeof data.notes === 'string') state.notes = data.notes.slice(0, 30000);
  if (Array.isArray(data.tasks)) {
    const seen = new Set();
    for (const task of data.tasks) {
      if (!task || typeof task.id !== 'string' || typeof task.title !== 'string') continue;
      const id = task.id.slice(0, 80);
      const title = task.title.trim().slice(0, 160);
      if (!id || !title || seen.has(id)) continue;
      state.tasks.push({id, title, done: task.done === true});
      seen.add(id);
      if (state.tasks.length === 30) break;
    }
  }
  if (Array.isArray(data.shortcuts)) {
    state.shortcuts = data.shortcuts.filter(item => item && typeof item.name === 'string' && website(item.url))
      .slice(0, 24).map(item => ({name: item.name.slice(0, 28), url: website(item.url)}));
  }
  for (const key of Object.keys(state.widgets)) {
    if (typeof data.widgets?.[key] === 'boolean') state.widgets[key] = data.widgets[key];
  }
  if (Array.isArray(data.order) && new Set(data.order).size === 2 &&
      data.order.includes('tabs') && data.order.includes('workspace')) state.order = [...data.order];
  const city = data.city;
  if (city && typeof city.name === 'string' && Number.isFinite(city.latitude) &&
      Number.isFinite(city.longitude) && Math.abs(city.latitude) <= 90 && Math.abs(city.longitude) <= 180) {
    state.city = {name: city.name.slice(0, 120), latitude: city.latitude, longitude: city.longitude};
  }
  const timer = data.timer;
  if (timer && [15, 25, 50].includes(timer.minutes)) {
    state.timer = {
      minutes: timer.minutes,
      remaining: Number.isFinite(timer.remaining) ? Math.max(0, Math.min(timer.minutes * 60, timer.remaining)) : timer.minutes * 60,
      end: Number.isFinite(timer.end) && timer.end > 0 ? Math.min(timer.end, Date.now() + timer.minutes * 60000) : 0
    };
  }
  return state;
}

export function loadState() {
  try {
    return sanitize(JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'));
  } catch {
    return sanitize({});
  }
}
export function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}
export function cpuUsage(previous, current) {
  if (!previous || previous.length !== current.length) return null;
  let total = 0;
  let idle = 0;
  for (let i = 0; i < current.length; i++) {
    const totalDelta = current[i].usage.total - previous[i].usage.total;
    const idleDelta = current[i].usage.idle - previous[i].usage.idle;
    if (totalDelta < 0 || idleDelta < 0) return null;
    total += totalDelta;
    idle += idleDelta;
  }
  return total > 0 ? Math.max(0, Math.min(100, (1 - idle / total) * 100)) : null;
}
