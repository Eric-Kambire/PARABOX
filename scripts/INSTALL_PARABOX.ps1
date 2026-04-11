# ================================================================
# PARABOX - Installation modules Odoo 17 Custom
# Projet MATCH - CAP2026
#
# LANCER DANS POWERSHELL ADMINISTRATEUR :
#   Clic droit sur PowerShell → "Exécuter en tant qu'administrateur"
#   Puis taper : .\INSTALL_PARABOX.ps1
# ================================================================

$ErrorActionPreference = "Stop"

$PYTHON     = 'C:\Program Files\Odoo 17.0.20260219\python\python.exe'
$ODOO_BIN   = 'C:\Program Files\Odoo 17.0.20260219\server\odoo-bin'
$ODOO_CONF  = 'C:\Program Files\Odoo 17.0.20260219\server\odoo.conf'
$MODULES    = 'C:\Users\Danssogo\OneDrive - Ecole Centrale Casablanca\Documents\ECC_2025-2026\S8\Transfo_Digit\CAP2026_PARABOX_Markdowns\odoo_modules'
$DB         = 'parabox_db'
$LOG        = "$PSScriptRoot\install_log.txt"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  PARABOX - Installation modules Odoo 17 - Projet MATCH CAP2026" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Modules : $MODULES" -ForegroundColor Yellow
Write-Host "  Config  : $ODOO_CONF" -ForegroundColor Yellow
Write-Host "  Base DB : $DB" -ForegroundColor Yellow
Write-Host ""

# ---------------------------------------------------------------
# Vérification droits admin
# ---------------------------------------------------------------
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERREUR: Lancez PowerShell en ADMINISTRATEUR." -ForegroundColor Red
    Write-Host "Fermez et relancez PowerShell avec clic droit → Exécuter en tant qu'administrateur" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}
Write-Host "[OK] Droits administrateur confirmes" -ForegroundColor Green

# ---------------------------------------------------------------
# Vérification fichiers
# ---------------------------------------------------------------
Write-Host ""
Write-Host "[1/4] Verification des pre-requis..." -ForegroundColor Cyan

if (-not (Test-Path $PYTHON))   { Write-Host "ERREUR: Python introuvable : $PYTHON" -ForegroundColor Red; Read-Host; exit 1 }
if (-not (Test-Path $ODOO_BIN)) { Write-Host "ERREUR: odoo-bin introuvable : $ODOO_BIN" -ForegroundColor Red; Read-Host; exit 1 }
if (-not (Test-Path $ODOO_CONF)){ Write-Host "ERREUR: odoo.conf introuvable : $ODOO_CONF" -ForegroundColor Red; Read-Host; exit 1 }
if (-not (Test-Path "$MODULES\parabox_credit_control\__manifest__.py")) {
    Write-Host "ERREUR: Modules PARABOX introuvables dans : $MODULES" -ForegroundColor Red
    Read-Host; exit 1
}
Write-Host "[OK] Tous les fichiers trouves" -ForegroundColor Green

# ---------------------------------------------------------------
# Mise à jour odoo.conf
# ---------------------------------------------------------------
Write-Host ""
Write-Host "[2/4] Mise a jour de odoo.conf..." -ForegroundColor Cyan

$confContent = Get-Content $ODOO_CONF -Raw -Encoding UTF8

if ($confContent -match [regex]::Escape($MODULES)) {
    Write-Host "[OK] Chemin modules deja present dans odoo.conf" -ForegroundColor Green
} else {
    # Sauvegarde
    Copy-Item $ODOO_CONF "$ODOO_CONF.backup" -Force
    Write-Host "[OK] Sauvegarde creee : odoo.conf.backup" -ForegroundColor Green

    # Modifier la ligne addons_path
    if ($confContent -match "addons_path\s*=") {
        $newContent = $confContent -replace "(addons_path\s*=\s*)(.+)", "`$1`$2,$MODULES"
    } else {
        $newContent = $confContent.TrimEnd() + "`naddons_path = $MODULES`n"
    }

    # Écrire sans BOM
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($ODOO_CONF, $newContent, $utf8NoBom)
    Write-Host "[OK] addons_path mis a jour dans odoo.conf" -ForegroundColor Green

    # Vérification
    $check = Get-Content $ODOO_CONF -Raw
    if ($check -match [regex]::Escape($MODULES)) {
        Write-Host "[OK] Verification: chemin bien ecrit" -ForegroundColor Green
    } else {
        Write-Host "ERREUR: Ecriture dans odoo.conf echouee" -ForegroundColor Red
        Read-Host; exit 1
    }
}

# ---------------------------------------------------------------
# Reportlab
# ---------------------------------------------------------------
Write-Host ""
Write-Host "[3/4] Installation de reportlab..." -ForegroundColor Cyan
try {
    & $PYTHON -m pip install reportlab --quiet 2>$null
    Write-Host "[OK] reportlab installe" -ForegroundColor Green
} catch {
    Write-Host "[!] reportlab non installe (verifiez la connexion internet)" -ForegroundColor Yellow
}

# ---------------------------------------------------------------
# Installation des modules
# ---------------------------------------------------------------
Write-Host ""
Write-Host "[4/4] Installation des modules PARABOX..." -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Odoo doit etre ARRETE avant de continuer." -ForegroundColor Yellow
Write-Host "Fermez l'application Odoo si elle tourne." -ForegroundColor Yellow
Read-Host "Appuyez sur Entree quand Odoo est bien ferme"

function Install-Module($modules, $step) {
    Write-Host ""
    Write-Host "  Installation ($step) : $modules ..." -ForegroundColor White
    $args_list = @(
        "$ODOO_BIN",
        "-c", "$ODOO_CONF",
        "-d", $DB,
        "-i", $modules,
        "--stop-after-init",
        "--without-demo=all",
        "--log-level=warn",
        "--logfile=$LOG"
    )
    $proc = Start-Process -FilePath $PYTHON -ArgumentList $args_list -Wait -PassThru -NoNewWindow
    if ($proc.ExitCode -ne 0) {
        Write-Host "  ERREUR lors de l'installation de : $modules" -ForegroundColor Red
        Write-Host "  Consultez le log : $LOG" -ForegroundColor Red
        return $false
    }
    Write-Host "  [OK] $modules" -ForegroundColor Green
    return $true
}

"" | Out-File $LOG  # Reset log

$ok = $true
$ok = $ok -and (Install-Module "parabox_credit_control" "1/5")
$ok = $ok -and (Install-Module "parabox_logistics_tracking,parabox_litige" "2/5")
$ok = $ok -and (Install-Module "parabox_encaissement,parabox_product_alias" "3/5")
$ok = $ok -and (Install-Module "parabox_sign" "4/5")
$ok = $ok -and (Install-Module "parabox_dashboard,parabox_mobile" "5/5")

Write-Host ""
if ($ok) {
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  INSTALLATION REUSSIE - Tous les modules PARABOX sont installes" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Prochaines etapes :" -ForegroundColor Cyan
    Write-Host "  1. Demarrez Odoo normalement"
    Write-Host "  2. http://localhost:8069 - connectez-vous en admin"
    Write-Host "  3. Ventes → Configuration → Parametres"
    Write-Host "     → Politique de facturation = 'Quantites livrees'  (CRITIQUE !)"
    Write-Host "  4. Dashboard : http://localhost:8069/odoo/parabox-dashboard"
    Write-Host "  5. Mobile    : http://localhost:8069/parabox/mobile/livreur"
    Write-Host ""
    Write-Host "  Pour modifier un module plus tard : editez les fichiers dans"
    Write-Host "  $MODULES" -ForegroundColor Yellow
    Write-Host "  puis redemarrez Odoo. Aucune reinstallation necessaire." -ForegroundColor Yellow
} else {
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "  ERREUR - Consultez le log : $LOG" -ForegroundColor Red
    Write-Host "  En cas de probleme, suivez INSTALL_MANUEL_ODOO.md" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
}

Write-Host ""
Read-Host "Appuyez sur Entree pour fermer"
