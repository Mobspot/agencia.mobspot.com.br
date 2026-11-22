# Insumos do CEO (22/11) para a landing da agência

- `exemplos/<slug>/`: 3 sites de clínicas FICTÍCIAS gerados pelo template `clinicas-1.0.1` (commit 5b1d38b), já reescritos para morar em `/exemplos/<slug>/` (caminhos absolutos `/_releases/<id>/` e `/` trocados por `/exemplos/<slug>/`, `noindex,nofollow` no `<head>`, sem robots/sitemap/llms próprios).
  - `patas-felizes`: veterinária (exemplo do template).
  - `sorrir-aurora`: odontologia em Moema (prontuário novo, fotos geradas por IA).
  - `lume`: dermatologia e estética na Vila Madalena (prontuário novo, fotos geradas por IA).
- `_insumos/prints-exemplos/`: telas 390 (2x) e 1366 de cada exemplo, para os cards/mockups.
- `_insumos/prontuarios/`: os 2 prontuários novos (fonte), para refazer o build se precisar (`node build/build.mjs <pasta> <saida>` no repo do template; as fotos estão no prontuário do Sam, não aqui).

Apagar `_insumos/` antes de publicar (o que for usado vai para `assets/`).
