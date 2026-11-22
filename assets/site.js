const notice = document.querySelector('#cookie-notice');
if (notice) {
  let dismissed = false;
  try { dismissed = localStorage.getItem('agencia-privacy-v1') === 'ok'; } catch {}
  notice.hidden = dismissed;
  const sync = () => {
    document.body.classList.toggle('notice-open', !notice.hidden);
    document.documentElement.style.setProperty('--notice-height', `${notice.hidden ? 0 : Math.ceil(notice.getBoundingClientRect().height)}px`);
  };
  sync();
  if (typeof ResizeObserver === 'function') new ResizeObserver(sync).observe(notice);
  window.addEventListener('resize', sync);
  notice.querySelector('[data-dismiss]').addEventListener('click', () => {
    notice.hidden = true;
    try { localStorage.setItem('agencia-privacy-v1', 'ok'); } catch {}
    sync();
  });
}
