# organizador_downloads

Organizador de Downloads — script Python para organizar arquivos na pasta de downloads por extensão e por nome de programa.

![CI](https://github.com/CESilva00702/organizador_downloads/actions/workflows/ci-pytest.yml/badge.svg)
[![Coverage Status](https://codecov.io/gh/CESilva00702/organizador_downloads/branch/main/graph/badge.svg)](https://codecov.io/gh/CESilva00702/organizador_downloads)

Como rodar localmente

```powershell
py -3 organizador_downloads.py --path "D:\\Downloads" --dry-run --verbose
```

Testes

```powershell
py -3 -m pytest -q tests
```

Nota: o workflow envia relatórios de cobertura para o Codecov usando o segredo `CODECOV_TOKEN`. Defina esse segredo nas configurações do repositório (`Settings -> Secrets`) para habilitar o upload de cobertura.
