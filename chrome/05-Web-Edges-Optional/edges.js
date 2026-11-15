(() => {
  if (window !== window.top || document.getElementById('scarlet-protocol-web-edges')) return;
  const host = document.createElement('div');
  host.id = 'scarlet-protocol-web-edges';
  host.setAttribute('aria-hidden', 'true');
  host.style.cssText = 'all:initial!important;position:fixed!important;inset:0!important;z-index:2147483646!important;pointer-events:none!important;display:block!important';
  const root = host.attachShadow({mode:'closed'});
  const style = document.createElement('style');
  style.textContent = `
    :host{all:initial!important;pointer-events:none!important}
    .rim{position:fixed;inset:0;z-index:2147483646;pointer-events:none;border:1px solid #e4195180;box-shadow:inset 0 0 9px #ff005145,0 0 12px #ff005144}
    .light{position:fixed;top:0;left:0;width:100%;height:4px;pointer-events:none;background:linear-gradient(90deg,#670d2b,#e41951,#ff8b92,#ff0051,#670d2b);background-size:240% 100%;box-shadow:0 2px 15px #ff0051,0 4px 23px #e4195199;animation:scarlet-travel 5s linear infinite}
    .rim:after{content:'';position:absolute;bottom:0;right:0;width:80px;height:22px;border-right:2px solid #ff0051;border-bottom:2px solid #ff0051;filter:drop-shadow(0 0 5px #ff0051)}
    @keyframes scarlet-travel{to{background-position:240% 0}}
    @media(prefers-reduced-motion:reduce){.light{animation:none}}
    @media print{.rim,.light{display:none}}
  `;
  const rim=document.createElement('div'),light=document.createElement('div');
  rim.className='rim';light.className='light';root.append(style,rim,light);
  (document.documentElement || document).append(host);
})();
