const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
if (menu && nav) {
  menu.hidden = false;
  const small = matchMedia('(max-width:767px)');
  const reset = () => { nav.dataset.collapsed = String(small.matches); menu.setAttribute('aria-expanded', String(!small.matches)); };
  reset(); small.addEventListener('change', reset);
  menu.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded', String(open)); nav.dataset.collapsed = String(!open); });
}
const notice = document.querySelector('#cookie-notice');
if (notice) {
  let dismissed = false;
  try { dismissed = localStorage.getItem('privacy-notice-v1') === 'dismissed'; } catch { /* armazenamento opcional */ }
  notice.hidden = dismissed;
  const syncNotice = () => document.documentElement.style.setProperty('--notice-height', `${notice.hidden ? 0 : Math.ceil(notice.getBoundingClientRect().height)}px`);
  syncNotice();
  if (typeof ResizeObserver === 'function') new ResizeObserver(syncNotice).observe(notice);
  window.addEventListener('resize', syncNotice);
  notice.querySelector('[data-dismiss]').addEventListener('click', () => { notice.hidden = true; syncNotice(); try { localStorage.setItem('privacy-notice-v1', 'dismissed'); } catch { /* sem impedir a navegação */ } });
}
const revealPrivacy = () => {
  if (location.hash === '#privacidade') {
    const policy = document.querySelector('#politica-privacidade');
    if (policy) policy.open = true;
  }
};
revealPrivacy();
window.addEventListener('hashchange', revealPrivacy);
document.querySelectorAll('a[href="/exemplos/lume/contato/#privacidade"]').forEach(link => link.addEventListener('click', () => {
  const policy = document.querySelector('#politica-privacidade');
  if (policy) policy.open = true;
}));
document.querySelector('[data-map]')?.addEventListener('click', event => {
  const button = event.currentTarget;
  const frame = document.createElement('iframe');
  frame.title = 'Localização da clínica no Google Maps';
  frame.referrerPolicy = 'no-referrer';
  frame.src = button.dataset.map;
  frame.allowFullscreen = true;
  document.querySelector('#map-frame').append(frame);
  button.hidden = true;
});

// Demonstração estática: nenhum formulário pode enviar dados.
document.querySelectorAll("form").forEach(form => form.addEventListener("submit", event => event.preventDefault()));
