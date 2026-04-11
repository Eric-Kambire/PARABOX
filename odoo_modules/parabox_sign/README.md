# parabox_sign — Signature BL Sécurisée

## Architecture de sécurité

```
AVANT livraison : OTP 6 chiffres → email client → hashé SHA-256 en base
PENDANT : livreur ouvre /parabox/sign/<token> → client entre OTP + signe au doigt
APRÈS : PDF généré (reportlab) + hash SHA-256 stocké → détection fraude
MODE DÉGRADÉ : signature sans OTP → alerte ADV automatique
```

## Installation

```bash
pip install reportlab   # Requis pour la génération PDF
# Copier parabox_sign dans le dossier addons Odoo 17
# Installer APRÈS parabox_logistics_tracking
```

## Routes HTTP

| Route | Auth | Description |
|-------|------|-------------|
| GET /parabox/sign/<token> | public | Page de signature client |
| POST /parabox/sign/verify-otp | public (JSON) | Vérification OTP |
| POST /parabox/sign/submit | public (JSON) | Enregistrement signature |
| GET /parabox/sign/pdf/<token> | public | Téléchargement PDF signé |
| POST /parabox/sign/check-integrity | user (JSON) | Vérification anti-fraude |

## Paramètre système

```
web.base.url = http://localhost:8069  (ou URL ngrok pour la démo)
```

## Dépendances Python

- `reportlab` : génération PDF (pip install reportlab)
- `hashlib`, `random`, `base64` : stdlib Python

## Utilisation

1. Ouvrir le BL sortant validé
2. Cliquer "✍️ Signer BL" → créer la demande
3. Cliquer "📧 Envoyer OTP" → OTP envoyé par email
4. Livreur ouvre l'URL sur son téléphone (via ngrok)
5. Client entre OTP + signe
6. PDF généré + hashé automatiquement
