# Estratégia de teste do update in-place (FEAT-111)

Como validamos a atualização in-place, dado que a feature **só existe a partir da
2.0** (não há uma versão anterior do CapivaraOS com a ferramenta para o salto real).
A saída é separar as **duas capacidades** — elas se testam de formas diferentes.

## 1. Update contínuo DENTRO da versão (caminho do dia a dia)
Receber correções/pacotes da versão corrente. É o que 99% dos usuários usam.
**Totalmente testável já, só com a 2.0** (nem depende de uma 2ª versão):
- instala a 2.0 numa VM (ou contêiner), aponta o `.repo` no canal **testing**;
- publica um pacote próprio com **EVR maior** (ex.: `capivaraos-branding` 0.45 → 0.46);
- `dnf update` / o card "Atualizar o CapivaraOS" puxa a versão nova.
- Prova: repo assinado (`gpgcheck`/`repo_gpgcheck`), o card aparecendo, e a **recusa**
  quando o metadado/pacote é adulterado.

Automação: **`tests/test-continuous-update.sh`** (contêiner Fedora, chave DESCARTÁVEL,
não toca o host) — instala v1 → publica v2 assinada → `dnf update` pega a v2 →
adultera a v2 → transação recusa. Roda AGORA, sem a chave de produção nem host.
No lançamento, o mesmo fluxo é revalidado contra o **testing publicado de verdade**
(passo 4 do `docs/repo/RUNBOOK-PUBLICACAO.md`).

## 2. Upgrade ENTRE versões (o "botão nova versão", 2.0 → 2.1)
Aqui está a galinha-e-ovo: **não existe uma 2.1 ainda** para o salto real. Testamos o
**motor** sem depender disso:
- **Alvo staged/sintético:** o `capivaraos-upgrade` é um invólucro do
  `dnf5 system-upgrade --releasever=N`. Publicamos um repo "da próxima versão" de
  mentira (um `marsh/f45` com pacotes de EVR maior, ou um esqueleto `marsh/f46`) e
  rodamos o upgrade numa VM → exercita o MESMO código: pré-voo (falha fechada se o
  repo do destino não existe), **snapshot snapper ANTES**, transação **offline** no
  reboot, boot na nova, **rollback** pelo snapshot. Já validado em contêiner por
  `tests/test-upgrade.sh` (5/5); a VM prova o boot/snapshot reais.
- **Exercício técnico F44→F45:** serve para provar o mecanismo offline+snapshot, MAS
  `1.x → 2.0` **NÃO é caminho de usuário** — a 1.x não tem a ferramenta e nunca
  mexemos na 1.x. Usuário de 1.x vai para a 2.0 **reinstalando**. Não travamos o
  lançamento nisso.

## A prova "de verdade" do salto real
Acontece quando a **2.1 sair**: uma VM 2.0 sobe para a 2.1 pelo botão. Isso é o
**critério de aceite do lançamento da 2.1**, não da 2.0.

Resumo dos gates:
- **No 2.0:** *update contínuo* (real, `test-continuous-update.sh` + VM no testing) +
  *motor de upgrade* (staged, `test-upgrade.sh` + VM com snapshot/rollback).
- **No 2.1:** *primeiro salto entre releases reais*, ponta a ponta.

## Sem contaminar usuário real
Tudo roda no canal **testing** (`enabled=0` por padrão). Quem está no **stable** nunca
vê o artefato de QA; só promovemos para stable depois que passa
(`publish-repo.sh promote`). É para isso que o split testing/stable existe.
