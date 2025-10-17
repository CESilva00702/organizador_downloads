# PR: Organizador - CLI, logging, safe-move, backup/rollback e testes

## Resumo
- Adiciona suporte completo de CLI ao script `organizador_downloads.py` (flags para path, dry-run, verbose, backup e logging).
- Implementa renomeação segura (`safe_move`) com modos de sufixo `counter` e `timestamp`.
- Registra operações em JSON (linha por linha) quando `--backup-dir` é fornecido.
- Adiciona ferramenta `tools/rollback.py` para reverter operações registradas (suporta `--dry-run`, `--log-file`).
- Converte saída para `logging` (console + opcional `--log-file`) para melhor controle e diagnóstico.
- Adiciona testes unitários com pytest + pyfakefs e um `requirements-dev.txt`.

## Arquivos principais alterados / adicionados
- modificados:
  - `organizador_downloads.py`
  - `.github/copilot-instructions.md`
- adicionados:
  - `tools/rollback.py`
  - `requirements-dev.txt`
  - `tests/test_organizador.py`
  - `tests/test_rollback.py`

## Como testar localmente
1) Instalar dependências dev:

```powershell
py -3 -m pip install -r requirements-dev.txt
```

2) Executar os testes unitários:

```powershell
py -3 -m pytest -q tests/test_organizador.py tests/test_rollback.py
```

3) Teste manual do organizador (dry-run):

```powershell
python .\organizador_downloads.py --path D:\Downloads\test_organizer --dry-run --verbose --log-file D:\Downloads\organizer.log
```

4) Simular rollback (dry-run):

```powershell
python .\tools\rollback.py --operations-log D:\Downloads\test_organizer\backup\operations.log --dry-run --verbose --log-file D:\Downloads\rollback.log
```

## Checklist para revisão
- [ ] Rodar os testes locais (comando acima) — todos devem passar.
- [ ] Rodar `organizador_downloads.py` em `--dry-run` e confirmar saídas/logs.
- [ ] Verificar se `operations.log` tem linhas JSON válidas quando `--backup-dir` é usado.
- [ ] Executar `tools/rollback.py --dry-run` sobre o mesmo `operations.log` e validar ações previstas.
- [ ] Revisar mensagens de logger (console e arquivo) para clareza.
- [ ] Revisar `.github/copilot-instructions.md` para precisão da documentação.

## Notas
- Não há breaking change; flags são opcionais.
- `operations.log` é append de entradas JSON lines.

## Sugestões de follow-up
- Adicionar CI (GitHub Actions) para rodar os testes automaticamente.
- Fazer a migração para um package/CLI se necessário.
- Tornar rollback mais robusto (retries/locks).

## Integração Codecov (opcional)

O workflow inclui um passo opcional para enviar relatórios de cobertura para o Codecov. Isso é útil para visualizar a cobertura de testes em um serviço dedicado, mas não é obrigatório para o funcionamento do CI.

Como habilitar o upload para o Codecov:

1. Crie uma conta no Codecov (https://codecov.io/) e adicione o repositório `CESilva00702/organizador_downloads`.
2. Gere um token de upload (Codecov upload token) nas configurações do seu repositório no Codecov.
3. No GitHub, vá em `Settings -> Secrets -> Actions` do repositório `organizador_downloads` e crie um segredo chamado `CODECOV_TOKEN` com o valor do token gerado.
4. Depois do push, o workflow irá executar e, se o segredo estiver definido, o passo de upload será executado automaticamente e você verá os relatórios no painel do Codecov.

Observações:
- O workflow foi escrito para não falhar caso o segredo `CODECOV_TOKEN` não exista (o step de upload é condicional). Isso facilita execução em forks e ambientes sem token.
- Se preferir não usar Codecov, não é necessário definir o segredo — os testes e a geração de coverage ainda rodam.
