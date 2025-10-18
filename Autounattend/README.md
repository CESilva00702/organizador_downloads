# Autounattend templates

Este diretório contém quatro templates de `Autounattend.xml` para uso em instalações Windows não assistidas.

Arquivos:

- `Autounattend_Basic.xml` — template básico, bom ponto de partida. Não contém senhas; substitua placeholders antes de usar.
- `Autounattend_Offline.xml` — projetado para instalações sem conectividade de rede; evita telas de conta online.
- `Autounattend_Personal.xml` — configuração orientada para máquinas pessoais; inclui timezone e placeholder para autologon.
- `Autounattend_Speedrun.xml` — otimizado para instalação mais rápida (partições agressivas, UI suprimida). Use com cautela.

Como usar

1. Copie o template desejado como `Autounattend.xml` para a raiz do seu mídia de instalação (pendrive com arquivos de instalação do Windows).
2. Substitua placeholders (por exemplo campos `<Value></Value>` para senhas ou `ProductKey`) de forma segura. Não inclua secrets em repositórios públicos.
3. Insira a mídia no PC alvo e inicialize a partir dela. A instalação deverá seguir as instruções do `Autounattend.xml` automaticamente.

Notas importantes

- Estes templates são exemplos e destinam-se a facilitar automação, não garantem compatibilidade com todas as imagens Windows.
- Teste em ambientes virtuais (Hyper-V, VirtualBox) antes de usar em hardware real.
- Não coloque senhas em texto sem proteção. Para automação segura, use mecanismos de provisioning pós-instalação ou gerencie senhas com ferramentas seguras.

Se quiser, posso:

- Gerar versões com placeholders para uso com `PowerShell` que criptografem a senha localmente.
- Criar um script `prepare_media.ps1` para copiar automaticamente um template e injetar valores seguros.
