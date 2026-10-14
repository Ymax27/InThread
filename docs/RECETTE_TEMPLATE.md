# Modèle de recette

> Une **recette** est un guide **court**, **testé** et **original** qui résout **un seul problème** d'intégration.
> Objectif : un dev doit pouvoir la suivre en moins de 15 minutes et obtenir un résultat qui marche.
>
> ⚠️ **Jamais** de vraie clé API, de vrai mot de passe, de vrai numéro de client. Utiliser des valeurs fictives (`<VOTRE_CLE>`) et les numéros de test officiels de l'opérateur.
> ⚠️ Écrire avec ses propres mots et son propre code : pas de copier-coller de la doc ou d'un tuto.

Copier le bloc ci-dessous dans un fichier `content/recipes/<slug>.md` (ou le transmettre via l'issue « Nouvelle recette »).

```markdown
---
title: "Encaisser un paiement MTN MoMo (Collection) avec Python et httpx"
slug: momo-collection-python-httpx
provider: mtn_momo          # mtn_momo | orange_money | wave | sms | ussd | autre
country: CM                 # code ISO2 : CM, SN, CI, BJ, BF, ML, TG, GA, CG, CD...
stack: "Python 3.12 + httpx"
api_version: "Collection v1_0"
environment: sandbox        # sandbox | production
tested_on: 2026-10-13       # date de ton dernier test réel
author: "pseudo"
sources:
  - "https://momodeveloper.mtn.com/..."   # doc officielle utilisée
---

## Problème
<!-- 2-3 phrases : quelle situation concrète ? Qu'est-ce qui bloque d'habitude ? -->

## Prérequis
- Compte / accès nécessaire (ex. compte développeur, clé d'abonnement)
- Versions (langage, bibliothèques)
- Variables d'environnement utilisées (noms seulement, jamais les valeurs)

## Étapes
1. …
2. …
3. …

## Code
<!-- Code minimal, complet et exécutable. Les secrets sont lus depuis l'environnement. -->
~~~python
import os
# ...
~~~

## Résultat attendu
<!-- Ce que l'on doit voir si ça marche (réponse HTTP, statut, capture texte). -->

## Pièges
- <!-- ex. « La sandbox n'accepte que l'EUR comme devise » (à vérifier) -->
- <!-- ex. format du numéro : sans le « + », avec l'indicatif -->
- <!-- ex. délai avant que le statut passe à SUCCESSFUL -->

## Pour aller en production
<!-- Ce qui change entre sandbox et prod : URL, clés, validation KYC, callbacks HTTPS... -->

## Vérifier que la recette marche encore
<!-- Comment un autre dev peut la retester rapidement (commande, numéro de test). -->
```

## Checklist avant publication

- [ ] Testée moi-même, à la date indiquée dans `tested_on`
- [ ] Un seul problème, résolu de bout en bout
- [ ] Code complet (imports compris), secrets lus depuis l'environnement
- [ ] Au moins un piège réel documenté
- [ ] Sources officielles citées
- [ ] Texte et code originaux
- [ ] Relue par un autre membre de l'équipe

## Idées de recettes de départ (à répartir)

| # | Fournisseur | Sujet | Pays | Responsable |
|---|---|---|---|---|
| 1 | MTN MoMo | Obtenir un token d'accès Collection (sandbox) | CM | TODO |
| 2 | MTN MoMo | Demander un paiement (`requesttopay`) et lire son statut | CM | TODO |
| 3 | MTN MoMo | Créer l'API user et l'API key en sandbox | CM | TODO |
| 4 | MTN MoMo | Recevoir et vérifier un callback | CM | TODO |
| 5 | Orange Money | Initier un paiement web (Web Payment) | CM | TODO |
| 6 | Orange Money | Vérifier le statut d'une transaction | CM | TODO |
| 7 | Wave | Créer une session de paiement (Checkout) | SN | TODO |
| 8 | Wave | Vérifier la signature d'un webhook | SN | TODO |
| 9 | SMS | Envoyer un SMS OTP via un agrégateur local | CM | TODO |
| 10 | USSD | Construire un menu USSD simple (session, étapes) | CM | TODO |
| 11 | Autre | Normaliser et valider des numéros camerounais (+237) | CM | TODO |
| 12 | Autre | Gérer l'idempotence des paiements (éviter les doubles débits) | — | TODO |
| 13 | Autre | Afficher les montants en FCFA (XAF / XOF) correctement | — | TODO |
| 14 | MTN MoMo | Gérer les erreurs et les statuts FAILED / PENDING | CM | TODO |
| 15 | Orange Money | Passer de la sandbox à la production | CM | TODO |
