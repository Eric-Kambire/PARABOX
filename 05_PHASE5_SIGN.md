# Phase 5 — Odoo Sign Custom Sécurisé
## Dossier output : /odoo_modules/parabox_sign/

---

## Objectif
Permettre au livreur de faire signer le BL par le client sur le terrain.  
La signature doit être **non répudiable, sécurisée et non bloquante** pour le workflow.

---

## Architecture de sécurité

```text
AVANT la livraison :
  → Odoo envoie OTP (6 chiffres) par email au client
  → OTP valable 30 minutes
  → OTP stocké hashé en base

PENDANT la livraison :
  → Le livreur ouvre la page de signature
  → Le client entre l'OTP
  → Le client signe avec le doigt (canvas BIC)
  → Le système enregistre IP, user-agent, timestamp, GPS si disponible

APRÈS la signature :
  → PDF BL généré avec signature incrustée
  → Hash SHA-256 du PDF calculé et stocké
  → Si le PDF est modifié → alerte fraude
  → Email confirmation client avec PDF signé

MODE DÉGRADÉ :
  → Signature sans OTP possible
  → Marquée "Non OTP"
  → Workflow continue
  → Alerte ADV
```

---

## Fichiers à générer

```text
/odoo_modules/parabox_sign/
  __manifest__.py
  __init__.py
  models/
    sign_request.py
    sign_log.py
  views/
    sign_request_views.xml
    sign_portal_templates.xml
  controllers/
    sign_controller.py
  static/
    src/js/signature_pad.js
    src/css/sign_style.css
  security/
    ir.model.access.csv
  README.md
```

---

## Modèle `parabox.sign.request`

```python
picking_id      = Many2one('stock.picking', 'BL à signer')
client_id       = Many2one('res.partner', 'Client')
livreur_id      = Many2one('res.users', 'Livreur')
otp_hash        = Char('OTP hashé', copy=False)
otp_expiry      = Datetime('Expiration OTP')
otp_sent        = Boolean('OTP envoyé')
otp_verified    = Boolean('OTP vérifié')
signed          = Boolean('Signé')
signature_image = Binary('Image signature BIC')
sign_datetime   = Datetime('Date/heure signature')
sign_ip         = Char('IP du signataire')
sign_user_agent = Char('User-Agent')
sign_gps        = Char('Coordonnées GPS')
pdf_hash        = Char('Hash SHA-256 du PDF signé')
pdf_signed      = Binary('PDF signé')
mode            = Selection([('otp','OTP + Signature'),('degrade','Signature sans OTP')], default='otp')
statut          = Selection([('draft','En attente'),('otp_sent','OTP envoyé'),('signed','Signé'),('failed','Échec')], default='draft')
```

---

## Routes HTTP

```python
# /parabox/sign/<token>
# /parabox/sign/verify-otp
# /parabox/sign/submit
# /parabox/sign/check-integrity
```

---

## Paramètres système

```python
parabox_sign_enabled      = Boolean('Activer signature BL', default=True)
parabox_sign_otp_required = Boolean('OTP obligatoire', default=True)
parabox_sign_gps_enabled  = Boolean('Capturer GPS', default=False)
```

---

## ✅ Checklist Phase 5

- [ ] Module installé
- [ ] OTP email fonctionnel
- [ ] Page responsive testée
- [ ] Canvas BIC fonctionnel
- [ ] Hash PDF stocké
- [ ] Mode dégradé testé
- [ ] Activation/désactivation testée
- [ ] README généré
