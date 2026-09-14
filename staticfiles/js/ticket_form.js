/**
 * JK Paper Mill - Multi-Step Ticket Wizard & Dynamic Category Fetching
 */

document.addEventListener('DOMContentLoaded', () => {
    let currentStep = 1;
    const totalSteps = 4;

    const btnNext = document.getElementById('btn-wizard-next');
    const btnPrev = document.getElementById('btn-wizard-prev');
    const btnSubmit = document.getElementById('btn-wizard-submit');
    const deptSelect = document.getElementById('id_department');
    const catSelect = document.getElementById('id_category');

    // 1. Dynamic Category Fetching
    if (deptSelect && catSelect) {
        deptSelect.addEventListener('change', function() {
            const deptId = this.value;
            if (!deptId) {
                catSelect.innerHTML = '<option value="">-- Select Category --</option>';
                return;
            }

            catSelect.innerHTML = '<option value="">Loading categories...</option>';
            fetch(`/departments/api/${deptId}/categories/`)
                .then(res => res.json())
                .then(data => {
                    catSelect.innerHTML = '<option value="">-- Select Category --</option>';
                    data.forEach(cat => {
                        const opt = document.createElement('option');
                        opt.value = cat.id;
                        opt.textContent = cat.name;
                        catSelect.appendChild(opt);
                    });
                })
                .catch(err => {
                    console.error("Failed to load categories:", err);
                    catSelect.innerHTML = '<option value="">General Issue</option>';
                });
        });
    }

    // 2. Wizard Navigation
    function showStep(step) {
        document.querySelectorAll('.wizard-section').forEach((el, index) => {
            el.style.display = (index + 1 === step) ? 'block' : 'none';
        });

        document.querySelectorAll('.wizard-step').forEach((el, index) => {
            if (index + 1 < step) {
                el.classList.add('completed');
                el.classList.remove('active');
            } else if (index + 1 === step) {
                el.classList.add('active');
                el.classList.remove('completed');
            } else {
                el.classList.remove('active', 'completed');
            }
        });

        if (btnPrev) btnPrev.style.display = (step > 1) ? 'inline-flex' : 'none';
        if (btnNext) btnNext.style.display = (step < totalSteps) ? 'inline-flex' : 'none';
        if (btnSubmit) btnSubmit.style.display = (step === totalSteps) ? 'inline-flex' : 'none';
    }

    if (btnNext) {
        btnNext.addEventListener('click', () => {
            if (validateCurrentStep(currentStep)) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    showStep(currentStep);
                }
            }
        });
    }

    if (btnPrev) {
        btnPrev.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                showStep(currentStep);
            }
        });
    }

    function validateCurrentStep(step) {
        if (step === 1) {
            const title = document.getElementById('id_title');
            const desc = document.getElementById('id_description');
            const dept = document.getElementById('id_department');

            if (!title || !title.value.trim()) {
                alert("Please provide an issue title before proceeding.");
                title.focus();
                return false;
            }
            if (!desc || !desc.value.trim()) {
                alert("Please provide an issue description.");
                desc.focus();
                return false;
            }
            if (!dept || !dept.value) {
                alert("Please select the target department.");
                dept.focus();
                return false;
            }
        }
        return true;
    }

    // 3. Drag and Drop File Upload & Image Preview
    const dropzone = document.getElementById('file-dropzone');
    const fileInput = document.getElementById('ticket-file-input');
    const previewContainer = document.getElementById('file-preview-container');

    if (dropzone && fileInput) {
        dropzone.addEventListener('click', () => fileInput.click());

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFilePreview(fileInput.files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                handleFilePreview(fileInput.files[0]);
            }
        });
    }

    function handleFilePreview(file) {
        if (!previewContainer) return;
        previewContainer.innerHTML = '';

        if (file.size > 10 * 1024 * 1024) {
            alert("File is too large! Maximum limit is 10MB.");
            fileInput.value = '';
            return;
        }

        const infoBox = document.createElement('div');
        infoBox.className = 'card-box';
        infoBox.style.padding = '12px 16px';
        infoBox.style.marginTop = '12px';
        infoBox.style.display = 'flex';
        infoBox.style.alignItems = 'center';
        infoBox.style.gap = '12px';

        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.className = 'file-preview-thumb';
            const reader = new FileReader();
            reader.onload = (e) => img.src = e.target.result;
            reader.readAsDataURL(file);
            infoBox.appendChild(img);
        } else {
            const icon = document.createElement('i');
            icon.className = 'bi bi-file-earmark-pdf text-danger';
            icon.style.fontSize = '32px';
            infoBox.appendChild(icon);
        }

        const details = document.createElement('div');
        details.innerHTML = `<strong>${file.name}</strong><br><small class="text-muted">${(file.size / 1024 / 1024).toFixed(2)} MB</small>`;
        infoBox.appendChild(details);

        previewContainer.appendChild(infoBox);
    }
});
