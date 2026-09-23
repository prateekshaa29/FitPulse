/**
 * Main application JavaScript for FitPulse
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Password Visibility Toggle
    const togglePasswordBtns = document.querySelectorAll('.toggle-password-btn');
    togglePasswordBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const icon = btn.querySelector('i');
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) {
                        icon.classList.remove('bi-eye');
                        icon.classList.add('bi-eye-slash');
                    }
                } else {
                    input.type = 'password';
                    if (icon) {
                        icon.classList.remove('bi-eye-slash');
                        icon.classList.add('bi-eye');
                    }
                }
            }
        });
    });

    // 2. Generic Delete Confirmation Modal Handler
    const deleteModal = document.getElementById('deleteConfirmModal');
    if (deleteModal) {
        const deleteForm = document.getElementById('deleteConfirmForm');
        const deleteItemName = document.getElementById('deleteItemName');
        const deleteButtons = document.querySelectorAll('.btn-delete-trigger');

        deleteButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const actionUrl = btn.getAttribute('data-action');
                const itemName = btn.getAttribute('data-name') || 'this item';
                
                if (deleteForm) deleteForm.action = actionUrl;
                if (deleteItemName) deleteItemName.textContent = itemName;
            });
        });
    }

    // 3. Auto-dismiss Flash Alerts after 5 seconds
    const autoDismissAlerts = document.querySelectorAll('.alert-auto-dismiss');
    autoDismissAlerts.forEach(alertEl => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // 4. Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});
