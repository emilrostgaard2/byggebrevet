# Byggebrevet.dk

Statisk site. `python build.py` bygger alt til `./public/`. Push til `main` bygger og deployer automatisk til Simply via GitHub Actions.

- Ny guide: læg en `.md`-fil i `content/guides/` (kopiér en eksisterende). `topic:` skal matche en slug i `TOPICS` i `build.py`.
- `[[cta]]` indsætter en tilbudsboks. `[[cta:slug|Overskrift]]` bruger et andet emne.
- Interne links til guides, der ikke findes endnu, vises som tekst og aktiveres automatisk, når guiden oprettes.
- Konfiguration (e-mail, redaktørnavn, partner-id) står øverst i `build.py`.
