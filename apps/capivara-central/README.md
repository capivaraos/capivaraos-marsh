# Central do Desenvolvedor

App de onboarding em português do **CapivaraOS Marsh** (linha 2.x). No primeiro
boot, oferece instalar em um clique os extras **opcionais** da estação de dev —
os que tiramos da ISO na Fase 1 para deixá-la enxuta (ver FEAT-89/FEAT-90).

- **UI:** QML/Kirigami (nativa do KDE Plasma).
- **Backend:** PySide6 (`backend.py`) — orquestra os installs e transmite o
  progresso ao QML linha a linha.
- **Privilégio:** as etapas que exigem root (dnf/systemctl/flatpak `--system`)
  são elevadas por `pkexec`, casando com a polkit action
  `org.capivaraos.central.setup-ai`. O app nunca roda como root.

## MVP (0.1.0)

Casca do onboarding + primeiro card funcional: **IA local** = Ollama (motor) +
Alpaca (interface, Flatpak) + extensão Continue no VSCodium.

Próximas levas: trilhas de linguagem (mise), ligar GPU (ROCm/CUDA), VS Code /
Cline / Docker CE, `gh` login + template de pre-commit.

## Rodar em desenvolvimento

Requer `python3-pyside6`, `kf6-kirigami` e `kf6-qqc2-desktop-style`:

```bash
python3 capivara-central.py
```

Em dev, os helpers são resolvidos na pasta `libexec/` ao lado; a etapa de root
só funciona de verdade no sistema instalado (caminho `/usr/libexec`).

## Build do RPM

```bash
./rpm/build-rpm.sh   # gera ~/rpmbuild/RPMS/noarch/capivara-central-*.rpm
```

## Layout

| Caminho | Papel |
|---|---|
| `capivara-central.py` | Ponto de entrada (carrega o QML, injeta o backend) |
| `backend.py` | Ponte QML↔sistema (QProcess + sinais de progresso) |
| `qml/` | Telas Kirigami (boas-vindas, catálogo, cards) |
| `libexec/setup-ai` | Orquestrador da IA local (roda como usuário) |
| `libexec/install-ai-system` | Parte root (via pkexec) |
| `data/` | `.desktop`, polkit `.policy`, ícone |
