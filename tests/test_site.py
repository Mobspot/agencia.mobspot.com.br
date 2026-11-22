from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, unquote
import json
import hashlib
import re
import struct
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = 'https://agencia.mobspot.com.br'
SLUGS = {'lume': 'Lume', 'patas-felizes': 'Patas Felizes', 'sorrir-aurora': 'Sorrir Aurora'}
MESSAGES = {
    'Quero meu site': 'Olá, Jade! Vim pelo site da agência e quero meu site para a minha clínica.',
    'Quero o agente': 'Olá, Jade! Quero saber do agente de IA de atendimento para a minha clínica.',
    'Falar com a Jade': 'Olá, Jade! Tenho um projeto sob medida para a minha clínica.',
}

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.tags, self.ids = path, [], set()
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.tags.append((tag, d))
        if 'id' in d:
            self.ids.add(d['id'])

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = [Page(p) for p in ROOT.rglob('*.html') if '_insumos' not in p.parts]
        cls.home = (ROOT/'index.html').read_text(encoding='utf-8')

    def test_all_local_links_assets_and_anchors_resolve(self):
        for page in self.pages:
            for tag, a in page.tags:
                refs = [a[k] for k in ('href', 'src') if a.get(k)]
                if a.get('srcset'):
                    refs += [entry.strip().split()[0] for entry in a['srcset'].split(',')]
                for ref in refs:
                    url = urlsplit(ref)
                    if url.scheme or url.netloc:
                        continue
                    target = ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/') else page.path.parent / unquote(url.path)
                    if not url.path:
                        target = page.path
                    if target.is_dir():
                        target /= 'index.html'
                    with self.subTest(page=page.path, ref=ref):
                        self.assertTrue(target.is_file(), str(target))
                        if url.fragment and target.suffix == '.html':
                            self.assertIn(unquote(url.fragment), Page(target).ids)

    def test_exact_sales_messages(self):
        for label, expected in MESSAGES.items():
            links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>'+label+r'</a>', self.home)
            self.assertTrue(links, label)
            for link in links:
                u = urlsplit(link)
                self.assertEqual((u.netloc, u.path), ('wa.me', '/5511995391545'))
                self.assertEqual(parse_qs(u.query)['text'], [expected])
                self.assertNotIn(' ', link)

    def test_all_whatsapp_destinations_and_example_messages(self):
        for page in self.pages:
            for tag, a in page.tags:
                url = urlsplit(a.get('href', ''))
                if url.netloc == 'wa.me':
                    self.assertEqual(url.path, '/5511995391545')
                    message = parse_qs(url.query).get('text', [])
                    self.assertTrue(message)
                    if 'exemplos' in page.path.parts:
                        slug = page.path.relative_to(ROOT).parts[1]
                        self.assertEqual(message, [f'Olá, Jade! Vi o exemplo {SLUGS[slug]} e quero um site assim para a minha clínica.'])

    def test_prices_and_plan_contents(self):
        for text in ['R$ 297', 'R$ 49/mês', 'R$ 600', 'R$ 1.200', 'Até 2 alterações por mês', 'Avaliações do Google', 'Formulário de contato', 'Agendamento pelo WhatsApp', 'Área de laudos']:
            self.assertIn(text, self.home)
        self.assertEqual(self.home.count('class="plan featured"'), 1)
        self.assertEqual(self.home.count('<details>'), 5)

    def test_seo_and_structured_offer_terms(self):
        for rel in ['index.html', 'privacidade/index.html', '404.html']:
            s = (ROOT/rel).read_text(encoding='utf-8')
            self.assertIn('lang="pt-BR"', s)
            self.assertLessEqual(len(re.search(r'<title>(.*?)</title>', s)[1]), 60)
            self.assertIn('name="description"', s)
            self.assertIn('rel="canonical"', s)
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.home, re.S)[1])
        self.assertEqual(data['@type'], 'ProfessionalService')
        offers = data['hasOfferCatalog']['itemListElement']
        self.assertEqual([o.get('price') for o in offers[:2]], ['297.00', '49.00'])
        self.assertEqual(offers[2]['priceSpecification']['minPrice'], '600.00')
        self.assertEqual(offers[3]['priceSpecification']['minPrice'], '1200.00')
        self.assertEqual(offers[2]['priceSpecification']['unitText'], 'mês')

    def test_host_and_discovery(self):
        self.assertEqual((ROOT/'CNAME').read_text().strip(), 'agencia.mobspot.com.br')
        self.assertTrue((ROOT/'.nojekyll').is_file())
        self.assertIn('Disallow: /exemplos/', (ROOT/'robots.txt').read_text())
        tree = ET.parse(ROOT/'sitemap.xml')
        urls = [e.text for e in tree.findall('.//{*}loc')]
        self.assertEqual(set(urls), {HOST+'/', HOST+'/privacidade/'})
        self.assertIn('fictícias', (ROOT/'llms.txt').read_text(encoding='utf-8'))
        self.assertIn('noindex', (ROOT/'404.html').read_text())

    def test_open_graph_png_or_authorized_html_fallback(self):
        self.assertIn('content="1200"', self.home)
        self.assertIn('content="630"', self.home)
        self.assertIn('summary_large_image', self.home)
        self.assertIn(HOST+'/assets/og.png', self.home)
        png = ROOT/'assets/og.png'
        if png.exists():
            raw = png.read_bytes()
            self.assertEqual(raw[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II', raw[16:24]), (1200, 630))
        else:
            source = (ROOT/'assets/og.html').read_text(encoding='utf-8')
            self.assertIn('width:1200px;height:630px', source)
            self.assertIn('noindex', source)

    def test_examples_are_safe_static_demonstrations(self):
        for slug in SLUGS:
            for p in (ROOT/'exemplos'/slug).rglob('*.html'):
                s = p.read_text(encoding='utf-8')
                with self.subTest(page=p):
                    self.assertIn('noindex', s)
                    if p.name != '404.html':
                        self.assertIn('Clínica fictícia', s)
                    for forbidden in ['wa.me/55119000000', '/_releases/', '/api/', 'href="tel:', 'href="mailto:']:
                        self.assertNotIn(forbidden, s)
            contact = (ROOT/'exemplos'/slug/'contato/index.html').read_text(encoding='utf-8')
            self.assertIn('Exemplo: o formulário não envia. Fale com a Jade pelo WhatsApp.', contact)
            self.assertIn('<fieldset disabled>', contact)
            self.assertNotIn('type="submit"', contact)
            self.assertNotIn('por até 30 dias', contact)
            for script in (ROOT/'exemplos'/slug/'assets').glob('*.js'):
                s = script.read_text(encoding='utf-8')
                self.assertNotIn('/api/', s)
                self.assertNotIn('fetch(', s)

    def test_no_third_party_auto_resources(self):
        for page in self.pages:
            for tag, a in page.tags:
                if tag in ('script', 'img', 'iframe'):
                    self.assertFalse(a.get('src', '').startswith(('http:', 'https:', '//')), (page.path, a))
                if tag == 'link' and a.get('rel') == 'stylesheet':
                    self.assertFalse(a.get('href', '').startswith(('http:', 'https:', '//')))
        for css in ROOT.rglob('*.css'):
            self.assertNotRegex(css.read_text(encoding='utf-8'), r'url\([\s\x22\x27]*(?:https?:|//)')

    def test_alt_and_responsive_late_images(self):
        for page in self.pages:
            for tag, a in page.tags:
                if tag == 'img':
                    self.assertIn('alt', a, page.path)
        home = Page(ROOT/'index.html')
        images = [a for t,a in home.tags if t == 'img']
        self.assertEqual(len(images), 5)
        for a in images:
            self.assertIn('srcset', a)
            self.assertIn('width', a)
            self.assertIn('height', a)
        for a in images[2:]:
            self.assertEqual(a.get('loading'), 'lazy')

    def test_home_budget_and_licenses(self):
        assets = ['index.html','assets/site.css','assets/site.js','assets/favicon.svg','assets/fonts/Nunito.ttf','assets/fonts/Inter.ttf']
        total = sum((ROOT/p).stat().st_size for p in assets)
        self.assertLessEqual(total, 300_000)
        for name in ['OFL-Inter.txt','OFL-Nunito.txt']:
            self.assertIn('SIL OPEN FONT LICENSE', (ROOT/'assets/fonts'/name).read_text())

    def test_privacy_and_safe_storage(self):
        s = (ROOT/'privacidade/index.html').read_text(encoding='utf-8')
        self.assertIn('localStorage', s)
        self.assertIn('registros técnicos', s)
        js = (ROOT/'assets/site.js').read_text(encoding='utf-8')
        self.assertIn('try {', js)
        self.assertIn('catch', js)
        self.assertIn('localStorage.setItem', js)
        css = (ROOT/'assets/site.css').read_text(encoding='utf-8')
        self.assertIn('body.notice-open .floating{display:none}', css)

    def test_no_inputs_shipped_and_no_encoding_damage(self):
        self.assertFalse((ROOT/'_insumos').exists())
        for page in self.pages:
            self.assertNotIn('\ufffd', page.path.read_text(encoding='utf-8'))

    def test_ci_and_documentation(self):
        workflow = (ROOT/'.github/workflows/validate.yml').read_text()
        self.assertIn('name: validar-site', workflow)
        self.assertIn('python -m unittest discover -s tests -v', workflow)
        for name in ['README.md','AGENTS.md','CHANGELOG.md']:
            self.assertTrue((ROOT/name).is_file())

    def test_adapted_example_manifest_hashes(self):
        for slug in SLUGS:
            base = ROOT/'exemplos'/slug
            data = json.loads((base/'manifest.json').read_text(encoding='utf-8'))
            self.assertTrue(data['teste'])
            self.assertEqual(data['tipo'], 'demonstracao-estatica-adaptada')
            for rel, expected in data['arquivos'].items():
                raw = (base/rel).read_bytes()
                self.assertEqual(expected['sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(expected['bytes'], len(raw))

if __name__ == '__main__':
    unittest.main()
