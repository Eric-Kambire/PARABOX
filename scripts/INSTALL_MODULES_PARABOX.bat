@echo off
chcp 65001 >nul

:: ================================================================
:: PARABOX - Installation modules Odoo 17 Custom
:: Projet MATCH - CAP2026
::
:: LANCER EN TANT QU'ADMINISTRATEUR
:: Clic droit → "Exécuter en tant qu'administrateur"
:: ================================================================

set PYTHON=C:\Program Files\Odoo 17.0.20260219\python\python.exe
set ODOO_BIN=C:\Program Files\Odoo 17.0.20260219\server\odoo-bin
set ODOO_CONF=C:\Program Files\Odoo 17.0.20260219\server\odoo.conf
set MODULES_PATH=C:\Users\Danssogo\OneDrive - Ecole Centrale Casablanca\Documents\ECC_2025-2026\S8\Transfo_Digit\CAP2026_PARABOX_Markdowns\odoo_modules
set DB_NAME=parabox_db
set LOG=%~dp0install_log.txt

echo ================================================================
echo  PARABOX - Installation modules Odoo 17 - Projet MATCH CAP2026
echo ================================================================
echo.
echo  Modules source : %MODULES_PATH%
echo  Config         : %ODOO_CONF%
echo  Base de donnees: %DB_NAME%
echo.

:: Vérification droits admin
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Lancez ce script en ADMINISTRATEUR.
    echo Clic droit sur le fichier → Executer en tant qu'administrateur
    pause & exit /b 1
)
echo [OK] Droits administrateur confirmes
echo.

:: Vérification fichiers
if not exist "%PYTHON%" ( echo ERREUR: Python introuvable & pause & exit /b 1 )
if not exist "%ODOO_BIN%" ( echo ERREUR: odoo-bin introuvable & pause & exit /b 1 )
if not exist "%ODOO_CONF%" ( echo ERREUR: odoo.conf introuvable & pause & exit /b 1 )
if not exist "%MODULES_PATH%\parabox_credit_control\__manifest__.py" (
    echo ERREUR: Modules PARABOX introuvables dans :
    echo   %MODULES_PATH%
    pause & exit /b 1
)
echo [OK] Tous les fichiers trouves
echo.

:: ---------------------------------------------------------------
:: ETAPE 1 : Modifier odoo.conf via Python (gère les espaces)
:: ---------------------------------------------------------------
echo [1/3] Mise a jour de odoo.conf...

"%PYTHON%" -c "
import sys, re, shutil

conf_path = r'C:\Program Files\Odoo 17.0.20260219\server\odoo.conf'
modules_path = r'C:\Users\Danssogo\OneDrive - Ecole Centrale Casablanca\Documents\ECC_2025-2026\S8\Transfo_Digit\CAP2026_PARABOX_Markdowns\odoo_modules'

# Lire le fichier
with open(conf_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Vérifier si déjà présent
if modules_path in content:
    print('  [OK] Chemin modules deja present dans odoo.conf')
    sys.exit(0)

# Sauvegarder
shutil.copy2(conf_path, conf_path + '.backup')
print('  [OK] Sauvegarde: odoo.conf.backup')

# Modifier la ligne addons_path
def update_addons(m):
    current = m.group(1).strip()
    if modules_path not in current:
        return 'addons_path = ' + current + ',' + modules_path
    return m.group(0)

new_content = re.sub(r'addons_path\s*=\s*(.+)', update_addons, content)

if new_content == content:
    # addons_path absent -> l'ajouter
    new_content = content.rstrip() + '\naddons_path = ' + modules_path + '\n'

with open(conf_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('  [OK] addons_path mis a jour dans odoo.conf')

# Vérification
with open(conf_path, 'r', encoding='utf-8') as f:
    check = f.read()
if modules_path in check:
    print('  [OK] Verification: chemin bien present')
else:
    print('  ERREUR: ecriture echouee')
    sys.exit(1)
"

if %ERRORLEVEL% NEQ 0 (
    echo ERREUR lors de la mise a jour de odoo.conf
    pause & exit /b 1
)
echo.

:: ---------------------------------------------------------------
:: ETAPE 2 : Installer reportlab
:: ---------------------------------------------------------------
echo [2/3] Installation de reportlab...
"%PYTHON%" -m pip install reportlab --quiet 2>nul
if %ERRORLEVEL% EQU 0 (echo   [OK] reportlab) else (echo   [!] reportlab non installe - verifiez la connexion)
echo.

:: ---------------------------------------------------------------
:: ETAPE 3 : Installation des modules (dans le bon ordre)
:: ---------------------------------------------------------------
echo [3/3] Installation des modules PARABOX dans la base %DB_NAME%...
echo.
echo IMPORTANT: Odoo doit etre ARRETE (fermez l'icone dans la barre des taches)
echo.
pause

echo.
echo  Installation 1/5 : parabox_credit_control...
"%PYTHON%" "%ODOO_BIN%" -c "%ODOO_CONF%" -d %DB_NAME% -i parabox_credit_control --stop-after-init --without-demo=all --log-level=warn --logfile="%LOG%" 2>>"%LOG%"
if %ERRORLEVEL% NEQ 0 goto :err

echo  Installation 2/5 : parabox_logistics_tracking + parabox_litige...
"%PYTHON%" "%ODOO_BIN%" -c "%ODOO_CONF%" -d %DB_NAME% -i parabox_logistics_tracking,parabox_litige --stop-after-init --without-demo=all --log-level=warn --logfile="%LOG%" 2>>"%LOG%"
if %ERRORLEVEL% NEQ 0 goto :err

echo  Installation 3/5 : parabox_encaissement + parabox_product_alias...
"%PYTHON%" "%ODOO_BIN%" -c "%ODOO_CONF%" -d %DB_NAME% -i parabox_encaissement,parabox_product_alias --stop-after-init --without-demo=all --log-level=warn --logfile="%LOG%" 2>>"%LOG%"
if %ERRORLEVEL% NEQ 0 goto :err

echo  Installation 4/5 : parabox_sign...
"%PYTHON%" "%ODOO_BIN%" -c "%ODOO_CONF%" -d %DB_NAME% -i parabox_sign --stop-after-init --without-demo=all --log-level=warn --logfile="%LOG%" 2>>"%LOG%"
if %ERRORLEVEL% NEQ 0 goto :err

echo  Installation 5/5 : parabox_dashboard + parabox_mobile...
"%PYTHON%" "%ODOO_BIN%" -c "%ODOO_CONF%" -d %DB_NAME% -i parabox_dashboard,parabox_mobile --stop-after-init --without-demo=all --log-level=warn --logfile="%LOG%" 2>>"%LOG%"
if %ERRORLEVEL% NEQ 0 goto :err

echo.
echo ================================================================
echo  INSTALLATION REUSSIE
echo ================================================================
echo.
echo  [OK] parabox_credit_control    - Controle credit + derogations
echo  [OK] parabox_logistics_tracking - Tracabilite 4 etats
echo  [OK] parabox_litige            - Kanban SLA litiges
echo  [OK] parabox_encaissement      - Plan paiement multi-modes
echo  [OK] parabox_product_alias     - Alias produits
echo  [OK] parabox_sign              - OTP + signature + SHA-256
echo  [OK] parabox_dashboard         - Dashboard 10 KPIs
echo  [OK] parabox_mobile            - Interface mobile livreur
echo.
echo  ETAPE SUIVANTE - Verifications dans Odoo :
echo  1. Demarrez Odoo normalement
echo  2. http://localhost:8069 - connectez-vous en admin
echo  3. Ventes → Configuration → Parametres
echo     → Politique de facturation = "Quantites livrees"  (CRITIQUE)
echo  4. Dashboard : http://localhost:8069/odoo/parabox-dashboard
echo  5. Mobile    : http://localhost:8069/parabox/mobile/livreur
echo.
echo  Pour toute modification de module : editez les fichiers dans
echo  %MODULES_PATH%
echo  puis redemarrez Odoo. Aucune reinstallation necessaire.
echo.
goto :fin

:err
echo.
echo ================================================================
echo  ERREUR lors de l'installation
echo ================================================================
echo  Consultez le log : %LOG%
echo  En cas de probleme, suivez INSTALL_MANUEL_ODOO.md
echo.

:fin
pause
