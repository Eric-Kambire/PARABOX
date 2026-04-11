# Phase 10 — Interfaces Web Mobile
## Dossier output : /odoo_modules/parabox_mobile/

---

## Contexte & Décision technique

### Pourquoi web mobile et pas app native ?
- App native (iOS/Android) = semaines de développement + store + certificats
- Notre contrainte : démo fonctionnelle, zéro budget, délai court
- Solution : interfaces web responsive accessibles via ngrok sur mobile
- Fonctionne sur tout téléphone avec Chrome/Safari → zéro installation
- Communique nativement avec Odoo via les mêmes routes HTTP/RPC

### Ce qu'on construit
2 interfaces web mobile distinctes :

```text
Interface 1 : Espace Livreur
  URL : http://[ngrok-url]/parabox/mobile/livreur
  Utilisateur : livreur@parabox.ma
  Rôle : voir ses BL du jour, valider livraison, déclencher OTP

Interface 2 : Page Signature Client
  URL : http://[ngrok-url]/parabox/sign/<token>
  Utilisateur : client (aucun compte Odoo requis)
  Rôle : entrer OTP, signer avec le doigt, confirmer
```

---

## Fichiers à générer

```text
/odoo_modules/parabox_mobile/
  __manifest__.py
  __init__.py
  controllers/
    mobile_controller.py
  views/
    mobile_templates.xml
  static/
    src/
      css/mobile.css
      js/mobile_livreur.js
      js/signature_pad.js
  security/
    ir.model.access.csv
  README.md
```

---

## Interface 1 — Espace Livreur

### Routes HTTP
```python
# GET  /parabox/mobile/livreur
# GET  /parabox/mobile/livreur/bl/<int:picking_id>
# POST /parabox/mobile/livreur/bl/<int:picking_id>/send-otp
# POST /parabox/mobile/livreur/bl/<int:picking_id>/validate
```

### Logique métier
```python
# stock.picking WHERE
#   state IN ('assigned', 'ready')
#   AND scheduled_date = today
#   AND user_id = uid_livreur
# ORDER BY scheduled_date ASC
```

### Design UI (mobile-first)
```text
PARABOX — Livreur
Mes livraisons du jour
- BL-PARA-2026-00001 / PARFUMERIE ATLAS / EN COURS
- BL-PARA-2026-00002 / PARAPHARMACIE GUÉLIZ / EN ATTENTE
```

---

## Interface 2 — Page Signature Client

### Route HTTP
```python
# GET /parabox/sign/<token>
# POST /parabox/sign/<token>/verify-otp
# POST /parabox/sign/<token>/submit
```

### Design UI
```text
Étape 1 : OTP
Étape 2 : Signature canvas
Étape 3 : Confirmation + hash + email
```

---

## CSS Mobile-First (points clés)

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Inter', sans-serif;
  background: #f8f9fa;
  font-size: 16px;
  line-height: 1.5;
}
.btn-mobile {
  width: 100%;
  padding: 16px;
  font-size: 1.1rem;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  margin: 8px 0;
}
.btn-primary  { background: #3498db; color: white; }
.btn-success  { background: #2ecc71; color: white; }
.btn-danger   { background: #e74c3c; color: white; }
.bl-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin: 10px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-left: 4px solid #3498db;
}
#signature-canvas {
  width: 100%;
  height: 200px;
  border: 2px dashed #bdc3c7;
  border-radius: 8px;
  background: white;
  touch-action: none;
}
.otp-input {
  width: 45px; height: 55px;
  font-size: 1.5rem;
  text-align: center;
  border: 2px solid #bdc3c7;
  border-radius: 8px;
  margin: 4px;
}
.otp-input:focus { border-color: #3498db; outline: none; }
```

---

## Communication avec Odoo

### Depuis l'interface livreur
```javascript
async function getBLduJour() {
  const result = await fetch('/web/dataset/call_kw', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      jsonrpc: '2.0', method: 'call', id: 1,
      params: {
        model: 'stock.picking',
        method: 'search_read',
        args: [[['state', 'in', ['assigned', 'ready']]]],
        kwargs: {fields: ['name', 'partner_id', 'scheduled_date', 'move_ids'], limit: 20}
      }
    })
  });
  return await result.json();
}
```

### Depuis la page signature
```javascript
async function verifierOTP(token, otp) {
  const result = await fetch(`/parabox/sign/${token}/verify-otp`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({otp: otp})
  });
  return await result.json();
}

async function soumettreSignature(token, signatureBase64) {
  const gps = await getGPS().catch(() => null);
  const result = await fetch(`/parabox/sign/${token}/submit`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      signature: signatureBase64,
      gps: gps
    })
  });
  return await result.json();
}
```

---

## Test sur mobile pendant la démo

### Setup démo
```text
1. Odoo lancé sur PC : localhost:8069
2. ngrok actif : ngrok http 8069 → https://abc123.ngrok.io
3. Livreur ouvre : https://abc123.ngrok.io/parabox/mobile/livreur
4. Se connecte avec livreur@parabox.ma / Parabox2026!
5. Voit ses BL du jour
6. Client ouvre le lien OTP reçu par email
7. Signe → confirmation → PDF généré côté serveur
```

### QR Code pour la démo
```python
import qrcode
url = "https://abc123.ngrok.io/parabox/mobile/livreur"
img = qrcode.make(url)
img.save("demo/qr_livreur.png")
```

---

## ✅ Checklist Phase 10

- [ ] Module parabox_mobile installé
- [ ] Interface livreur accessible via ngrok
- [ ] Liste BL du jour affichée
- [ ] Bouton "Envoyer OTP" fonctionnel
- [ ] Page signature accessible
- [ ] OTP vérifié correctement
- [ ] Canvas BIC fonctionnel
- [ ] GPS capturé si autorisé
- [ ] PDF signé généré et envoyé
- [ ] Hash SHA-256 stocké
- [ ] QR code démo généré
- [ ] Testé sur Chrome mobile Android
- [ ] Testé sur Safari mobile iOS
- [ ] Mode dégradé testé
- [ ] README.md dans /odoo_modules/parabox_mobile/

---

## README.md pour parabox_mobile

```markdown
# parabox_mobile — Interfaces Web Mobile PARABOX

## Rôle
Ce module fournit 2 interfaces web responsive pour les utilisateurs terrain.
Aucune app native. Fonctionne sur tout téléphone via navigateur Chrome/Safari.

## Interfaces
1. /parabox/mobile/livreur → espace livreur (login requis)
2. /parabox/sign/<token>   → signature client (public, token signé)

## Installation
1. Copier le dossier dans /odoo/addons/
2. Settings > Apps > Update Apps List
3. Installer "PARABOX Mobile"

## Configuration
Settings > Technical > System Parameters :
- parabox.ngrok.url → https://abc123.ngrok.io
- parabox.sign.enabled → True
- parabox.sign.otp.required → True

## Démo
1. Lancer ngrok : ngrok http 8069
2. Mettre à jour parabox.ngrok.url avec la nouvelle URL
3. Scanner qr_livreur.png avec un téléphone
4. Se connecter : livreur@parabox.ma / Parabox2026!

## Dépendances
- parabox_sign (Phase 5) — obligatoire
- stock (Inventory) — obligatoire
- Librairie JS : signature_pad.js (MIT, incluse dans /static/)
```
