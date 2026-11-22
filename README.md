# Agência Mobspot

Landing estática independente, HTML/CSS/JS sem build e sem CDN. Fontes locais Nunito/Inter com licenças em `assets/fonts/`. Prints derivados dos insumos CEO; exemplos fictícios de clinicas-1.0.1, não clientes reais.

Validar: `python -m unittest discover -s tests -v`.
Prévia: `python -m http.server 8765 --bind 127.0.0.1` na raiz; abrir localhost:8765.

Branch de trabalho `landing`, base `ac48937`. CEO faz commit/push/revisão 390 e 1366, Pages e DNS. Sem publicação nesta entrega. CI `validar-site` verifica o artefato; a configuração de Pages pela branch não impõe gate automaticamente: o CEO deve verificar o CI antes da promoção à main.

`assets/og.html` é a fonte 1200×630 da imagem social; se `og.png` não estiver presente, o CEO deve renderizar e validar antes de publicar. Exemplos bloqueados no robots e noindex; formulários sem envio inclusive sem JS; WhatsApp da Jade. Nenhum segredo ou analytics.

Antes da primeira publicação: guardar baseline da main, revisar o candidato e passar CI; depois, smoke HTTPS, home, privacidade, 404, OG, exemplos e mensagens da Jade. Rollback por revert do commit de publicação e novo smoke, sem force push. Não retirar DNS como rollback improvisado.

## Pendências da entrega local

A remoção autorizada de `_insumos/` foi rejeitada pela revisão automática (blocked by policy). CEO deve remover antes do commit/publicação; a pasta está idêntica à base `ac48937`. O teste de empacotamento permanece falhando até essa limpeza. O navegador falhou com WinError 5: revisar 390/1366, console, interações e renderizar `assets/og.html` em `assets/og.png` antes de publicar.
