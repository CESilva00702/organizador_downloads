# Instruções rápidas para agentes de código (Copilot / agentes)

Resumo: repositório minimalista com um único script Python principal, `organizador_downloads.py`, que organiza a pasta de Downloads agrupando arquivos por extensão e por um "nome de programa" extraído do nome do arquivo.

Principais pontos (big picture)
- Estrutura: projeto é um script autônomo no nível raiz (`organizador_downloads.py`). Não há pacotes, build system, testes ou dependências externas.
- Responsabilidade: ler o diretório de downloads (variável `PASTA_DOWNLOADS`), classificar cada arquivo por extensão (cria pasta com a extensão em maiúsculas) e por um nome gerado por `extrair_nome_programa`, e mover o arquivo para a subpasta correspondente.
- Fluxo de dados: listdir(pasta) -> para cada arquivo: extrai extensão -> cria pasta de extensão (ex: `PDF`) -> chama `extrair_nome_programa(nome_arquivo)` -> cria subpasta (ex: `PDF/Adobe`) -> shutil.move(origem, destino).

Arquivos-chave
- `organizador_downloads.py` — único ponto de verdade. Leia esse arquivo antes de modificar a lógica; contém as funções:
  - `extrair_nome_programa(nome_arquivo)` (padrões de limpeza de nomes, ver regex abaixo)
  - `organizar_downloads(pasta_alvo)` (iteração e moves)

Padrões e convenções específicos do projeto
- Pasta de extensão: criada com o nome da extensão em UPPERCASE (ex: `PDF`, `EXE`, `Sem_Extensao`).
- Arquivos sem extensão usam a pasta `Sem_Extensao`.
- Extração de nome do programa: a função remove versões e tokens comuns antes de pegar o primeiro token como nome. Exemplos de regex/padrões usados:
  - Versões: r"[\s._-]?v?\d+(\.\d+)*" (remove `-1.2.3`, `_v2`, etc.)
  - Tokens: r"[\s._-]?(x86|x64|win32|win64|setup|installer)" (remove sinais de arquitetura e palavras comuns de instalador)
  - Substituições: `_` e `-` transformados em espaço; depois pega `nome_limpo.split()[0].capitalize()` como pasta do programa.
- O script pula diretórios e também evita mover ele mesmo (comparando `nome_arquivo` com `os.path.basename(__file__)`).

Como executar / fluxos de desenvolvedor
- Não há build. Execute diretamente com Python 3 instalado. Exemplos em PowerShell (Windows):

```powershell
# usa o python associado ao PATH
python .\organizador_downloads.py

# ou, se houver múltiplas versões Python
py -3 .\organizador_downloads.py
```

- Configuração rápida: altere a variável `PASTA_DOWNLOADS` no topo de `organizador_downloads.py` para apontar para a pasta desejada (ex: `"D:\Downloads"`). Não há parâmetros de linha de comando atualmente.

Padrões de erro e limitações observadas no código atual
- Movimentação: usa `shutil.move` sem renomeação automática em caso de conflito; se o arquivo destino já existir, o move falhará e o erro será impresso (`except Exception as e: print(...)`).
- Logging: saída via `print()` para informar criação de pastas, moves e erros.
- Internacionalização / nomes: a extração de nome toma a primeira palavra capitalizada — pode gerar pastas curtas (ex: `Usb`, `Readme`) para nomes compostos.

Integrações externas e dependências
- Nenhuma dependência externa: somente stdlib (`os`, `shutil`, `re`).
- Nenhuma integração com serviços externos/API detectada.

Diretrizes práticas para agentes
- Antes de alterar, leia `organizador_downloads.py` por completo e preserve a lógica de detecção de extensões (`extensao = extensao[1:].lower() if extensao else 'Sem_Extensao'`) se você modificar saída de pastas para manter compatibilidade com pastas já criadas.
- Ao adicionar mudanças que alterem formatos de pasta (por ex. trocar `Sem_Extensao` por `NO_EXT`), atualize o README e explique a migração/compatibilidade.
- Quando for implementar novas features (CLI, dry-run, logging), mantenha prints compatíveis e adicione uma flag `--dry-run` em vez de executar moves por padrão.
- Tratamento de conflitos: implementar renomeação segura (ex: adicionando sufixo incremental) é recomendado se for modificar `shutil.move`.

Exemplos concretos (trechos relevantes)
- Regex de versões: `[\s._-]?v?\d+(\.\d+)*` — usado por `extrair_nome_programa`.
- Token arquitetural removido: `(x86|x64|win32|win64|setup|installer)`.

O que NÃO está no repositório (e não deve ser presumido)
- Não há testes automatizados nem CI configurado.
- Não há arquivos de licença ou CONTRIBUTING no repositório raiz (procure em subpastas se necessário).

Próximos passos sugeridos (para humanos, rápido):
- Adicionar um README pequeno explicando o propósito e como mudar `PASTA_DOWNLOADS`.
- O script agora inclui flags CLI, dry-run e logging de operações (veja abaixo).

### Novas flags e comportamento

- `--path/-p <path>`: pasta alvo a ser organizada (default: `PASTA_DOWNLOADS`).
- `--dry-run`: simula as ações sem mover arquivos (útil para validação antes de rodar).
- `--verbose`: mostra mensagens detalhadas (criação de pastas, moves, erros).
- `--backup-dir <path>`: diretório onde será gravado `operations.log` (JSON lines) para possível rollback.
- `--suffix-mode <counter|timestamp>`: controla o comportamento quando há conflito de nomes. `counter` gera `name (1).ext`; `timestamp` gera `name_YYYYMMDDTHHMMSS.ext`.

### Exemplos de uso

Dry-run com saída verbosa:

```powershell
python .\organizador_downloads.py --path D:\Downloads --dry-run --verbose
```

Executar e gravar backup das operações (para rollback):

```powershell
python .\organizador_downloads.py --path D:\Downloads --backup-dir D:\Downloads\organizer_backup --suffix-mode timestamp
```

Rodar testes locais (instalar dependências dev primeiro):

```powershell
py -3 -m pip install -r requirements-dev.txt
py -3 -m pytest -q tests/test_organizador.py
```

Rollback básico (manual):

- O log `operations.log` no `--backup-dir` contém linhas JSON com os campos `src`, `dst`, `moved_at` e `dry_run`.
- Para reverter manualmente, leia cada entrada e mova `dst` de volta para `src` (atenção com permissões e conflitos).

Se quiser, eu também posso:
1) implementar um script `tools/rollback.py` que aplica reverter operações registradas em `operations.log`, ou
2) migrar prints para `logging` com níveis (INFO/DEBUG) e configurar um `--log-file`.

---
Por favor, diga qual próximo passo prefere: implementar rollback automático, migrar para logging ou finalizar e commitar as alterações.                                                     