/**
 * PARABOX Sign — Signature Pad BIC
 * Canvas touch/mouse pour signature sur mobile
 */

(function () {
    'use strict';

    // ─── Variables globales ───────────────────────────────────────────────────
    let canvas, ctx;
    let isDrawing = false;
    let lastX = 0, lastY = 0;
    let hasSignature = false;
    let otpVerified = false;
    let gpsCoords = null;
    const TOKEN = document.getElementById('sign-token')?.value || '';

    // ─── Initialisation ───────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        canvas = document.getElementById('signature-canvas');
        if (!canvas) return;

        ctx = canvas.getContext('2d');
        _resizeCanvas();
        _initDrawing();
        _initOtp();
        _initGps();
        _initButtons();

        window.addEventListener('resize', _resizeCanvas);
    });

    // ─── Canvas signature ─────────────────────────────────────────────────────
    function _resizeCanvas() {
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);
        ctx.strokeStyle = '#1a1a1a';
        ctx.lineWidth = 2.5;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
    }

    function _getPos(e) {
        const rect = canvas.getBoundingClientRect();
        if (e.touches) {
            return {
                x: e.touches[0].clientX - rect.left,
                y: e.touches[0].clientY - rect.top
            };
        }
        return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    }

    function _startDraw(e) {
        e.preventDefault();
        isDrawing = true;
        const pos = _getPos(e);
        lastX = pos.x;
        lastY = pos.y;
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
    }

    function _draw(e) {
        if (!isDrawing) return;
        e.preventDefault();
        const pos = _getPos(e);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
        lastX = pos.x;
        lastY = pos.y;
        if (!hasSignature) {
            hasSignature = true;
            canvas.classList.add('has-signature');
            _updateSubmitButton();
        }
    }

    function _stopDraw(e) {
        if (e) e.preventDefault();
        isDrawing = false;
    }

    function _initDrawing() {
        // Touch events
        canvas.addEventListener('touchstart', _startDraw, { passive: false });
        canvas.addEventListener('touchmove', _draw, { passive: false });
        canvas.addEventListener('touchend', _stopDraw, { passive: false });
        // Mouse events
        canvas.addEventListener('mousedown', _startDraw);
        canvas.addEventListener('mousemove', _draw);
        canvas.addEventListener('mouseup', _stopDraw);
        canvas.addEventListener('mouseleave', _stopDraw);
    }

    function _clearSignature() {
        if (!canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        hasSignature = false;
        canvas.classList.remove('has-signature');
        _updateSubmitButton();
    }

    // ─── OTP ──────────────────────────────────────────────────────────────────
    function _initOtp() {
        const otpInput = document.getElementById('otp-input');
        const verifyBtn = document.getElementById('btn-verify-otp');
        if (!otpInput || !verifyBtn) return;

        otpInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').substring(0, 6);
            verifyBtn.disabled = this.value.length < 6;
        });

        verifyBtn.addEventListener('click', _verifyOtp);
        otpInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && this.value.length === 6) _verifyOtp();
        });
    }

    function _verifyOtp() {
        const otpInput = document.getElementById('otp-input');
        const otp = otpInput?.value;
        if (!otp || otp.length !== 6) return;

        const verifyBtn = document.getElementById('btn-verify-otp');
        const otpMsg = document.getElementById('otp-message');
        verifyBtn.disabled = true;
        verifyBtn.innerHTML = '<span class="spinner"></span>Vérification...';

        fetch('/parabox/sign/verify-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jsonrpc: '2.0', method: 'call', id: 1,
                params: { token: TOKEN, otp: otp } })
        })
        .then(r => r.json())
        .then(data => {
            const result = data.result;
            if (result && result.success) {
                otpVerified = true;
                otpInput.classList.add('valid');
                otpInput.classList.remove('invalid');
                otpInput.readOnly = true;
                if (otpMsg) {
                    otpMsg.className = 'msg-success';
                    otpMsg.textContent = result.message;
                    otpMsg.style.display = 'block';
                }
                // Cacher le bouton, afficher section signature
                document.getElementById('otp-section')?.classList.add('otp-done');
                document.getElementById('signature-section')?.classList.remove('hidden');
                _updateSubmitButton();
            } else {
                otpInput.classList.add('invalid');
                if (otpMsg) {
                    otpMsg.className = 'msg-error';
                    otpMsg.textContent = result?.message || 'OTP incorrect';
                    otpMsg.style.display = 'block';
                }
                verifyBtn.disabled = false;
                verifyBtn.textContent = 'Vérifier le code';
            }
        })
        .catch(() => {
            verifyBtn.disabled = false;
            verifyBtn.textContent = 'Vérifier le code';
        });
    }

    // ─── GPS ──────────────────────────────────────────────────────────────────
    function _initGps() {
        const gpsStatus = document.getElementById('gps-status');
        if (!gpsStatus || !navigator.geolocation) return;

        gpsStatus.textContent = 'Localisation en cours...';
        navigator.geolocation.getCurrentPosition(
            function (pos) {
                gpsCoords = pos.coords.latitude.toFixed(6) + ',' + pos.coords.longitude.toFixed(6);
                gpsStatus.textContent = gpsCoords;
            },
            function () {
                gpsStatus.textContent = 'GPS non disponible';
            },
            { timeout: 8000, maximumAge: 60000 }
        );
    }

    // ─── Bouton soumettre ─────────────────────────────────────────────────────
    function _initButtons() {
        const submitBtn = document.getElementById('btn-submit-signature');
        if (submitBtn) submitBtn.addEventListener('click', _submitSignature);

        const clearBtn = document.getElementById('btn-clear-signature');
        if (clearBtn) clearBtn.addEventListener('click', _clearSignature);

        const degradeBtn = document.getElementById('btn-degrade');
        if (degradeBtn) degradeBtn.addEventListener('click', _activateDegrade);

        _updateSubmitButton();
    }

    function _updateSubmitButton() {
        const submitBtn = document.getElementById('btn-submit-signature');
        if (!submitBtn) return;
        const needsOtp = document.getElementById('otp-section') &&
                         !document.getElementById('otp-section').classList.contains('otp-done');
        submitBtn.disabled = !hasSignature || (needsOtp && !otpVerified);
    }

    function _activateDegrade() {
        const warn = document.getElementById('degrade-warning');
        if (warn) {
            warn.style.display = 'block';
        }
        document.getElementById('otp-section')?.classList.add('otp-done');
        document.getElementById('signature-section')?.classList.remove('hidden');
        document.getElementById('btn-degrade')?.remove();
        otpVerified = false;
        _updateSubmitButton();
    }

    function _submitSignature() {
        if (!hasSignature) {
            alert('Veuillez signer avant de valider.');
            return;
        }

        const submitBtn = document.getElementById('btn-submit-signature');
        const msgDiv = document.getElementById('submit-message');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span>Enregistrement...';

        const signatureB64 = canvas.toDataURL('image/png');

        fetch('/parabox/sign/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jsonrpc: '2.0', method: 'call', id: 1,
                params: {
                    token: TOKEN,
                    signature_b64: signatureB64,
                    otp_verified: otpVerified,
                    gps: gpsCoords,
                }
            })
        })
        .then(r => r.json())
        .then(data => {
            const result = data.result;
            if (result && result.success) {
                // Succès — afficher page de confirmation
                document.getElementById('sign-form-container')?.classList.add('hidden');
                const successDiv = document.getElementById('sign-success');
                if (successDiv) {
                    successDiv.classList.remove('hidden');
                    if (result.pdf_url) {
                        const pdfLink = document.getElementById('pdf-download-link');
                        if (pdfLink) {
                            pdfLink.href = result.pdf_url;
                            pdfLink.style.display = 'inline-block';
                        }
                    }
                }
            } else {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Valider la signature';
                if (msgDiv) {
                    msgDiv.className = 'msg-error';
                    msgDiv.textContent = result?.message || 'Erreur lors de la soumission.';
                    msgDiv.style.display = 'block';
                }
            }
        })
        .catch(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Valider la signature';
        });
    }

})();
