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
document.querySelectorAll('a[href="/exemplos/sorrir-aurora/contato/#privacidade"]').forEach(link => link.addEventListener('click', () => {
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
const dialog = document.querySelector('#retorno-dialog');
if (dialog && typeof dialog.showModal === 'function') {
  let opener;
  document.querySelectorAll('[data-retorno]').forEach(button => button.addEventListener('click', event => {
    event.preventDefault(); opener = button;
    dialog.showModal(); document.body.classList.add('modal-open');
    dialog.querySelector('[name=telefone]').focus();
  }));
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { document.body.classList.remove('modal-open'); opener?.focus(); });
  // showModal torna o documento externo inerte; ciclo explícito também cobre teclados legados.
  dialog.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); dialog.close(); return; }
    if (event.key !== 'Tab') return;
    const focusable = [...dialog.querySelectorAll('a[href],button:not(:disabled),input:not([tabindex="-1"])')].filter(e => !e.hidden);
    const first = focusable[0], last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  const form = dialog.querySelector('form'), status = dialog.querySelector('[role=status]');
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    let digits = form.elements.telefone.value.replace(/\D/g, '');
    if (digits.length === 10 || digits.length === 11) digits = '55' + digits;
    if (!/^55[1-9]{2}\d{8,9}$/.test(digits)) { status.textContent = 'Informe um telefone válido com DDD.'; form.elements.telefone.focus(); return; }
    const button = form.querySelector('[type=submit]'); button.disabled = true;
    status.textContent = 'Enviando seu pedido…';
    try {
      const response = await fetch('/api/retorno', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ telefone: '+' + digits, nome: form.elements.nome.value.trim(), website: form.elements.website.value }), signal: AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error(response.status === 429 ? 'Muitos pedidos. Aguarde um minuto e tente novamente.' : 'Não foi possível enviar. Tente novamente ou use o e-mail da clínica.');
      status.textContent = 'Pedido recebido. Nossa equipe retornará o contato.'; form.reset();
    } catch (error) { status.textContent = error.name === 'Error' ? error.message : 'Não foi possível conectar. Tente novamente ou use o e-mail da clínica.'; }
    finally { button.disabled = false; }
  });
}
