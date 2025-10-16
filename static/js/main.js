document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing Personalised Card Generator...');
    
    // DOM elements
    const form = document.getElementById('cardForm');
    const imageInput = document.getElementById('imageInput');
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removeImageBtn = document.getElementById('removeImage');
    const generateBtn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const resultSection = document.getElementById('resultSection');
    const generatedCard = document.getElementById('generatedCard');
    const characterName = document.getElementById('characterName');
    const cardStats = document.getElementById('cardStats');
    const cardAbility = document.getElementById('cardAbility');
    const downloadBtn = document.getElementById('downloadBtn');
    const newCardBtn = document.getElementById('newCardBtn');

    // Store uploaded file globally for reliable access
    let uploadedFile = null;

    // File upload handling
    imageInput.addEventListener('change', handleImageUpload);
    imageInput.addEventListener('click', (event) => {
        // Stop propagation to prevent triggering uploadArea click
        event.stopPropagation();
    });
    uploadArea.addEventListener('click', (event) => {
        // Prevent double-triggering if clicking directly on the file input
        if (event.target === imageInput) {
            return;
        }
        console.log('Upload area clicked, triggering file input...');
        event.preventDefault();
        event.stopPropagation();
        imageInput.click();
    });
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    removeImageBtn.addEventListener('click', removeImage);

    // Form submission
    form.addEventListener('submit', handleFormSubmit);
    console.log('Event listeners attached successfully');

    // Button events
    downloadBtn.addEventListener('click', downloadCard);
    newCardBtn.addEventListener('click', resetForm);

    // Image upload functions
    function handleImageUpload(event) {
        console.log('Image upload triggered, files:', event.target.files);
        const file = event.target.files[0];
        if (file) {
            console.log('File selected:', file.name, 'Size:', file.size, 'Type:', file.type);
            uploadedFile = file; // Store globally
            processImageFile(file);
        } else {
            console.log('No file selected');
        }
    }

    function handleDragOver(event) {
        event.preventDefault();
        uploadArea.classList.add('dragover');
    }

    function handleDragLeave(event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
    }

    function handleDrop(event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        console.log('Files dropped:', files.length);
        if (files.length > 0) {
            console.log('Processing dropped file:', files[0].name);
            uploadedFile = files[0]; // Store globally
            
            // Update the file input element with the dropped file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]);
            imageInput.files = dataTransfer.files;
            
            processImageFile(files[0]);
        }
    }

    function processImageFile(file) {
        console.log('Processing image file:', file.name);
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            console.error('Invalid file type:', file.type);
            showError('Please select a valid image file.');
            return;
        }

        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            console.error('File too large:', file.size);
            showError('File size must be less than 16MB.');
            return;
        }

        console.log('File validation passed, creating preview...');
        
        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            console.log('File preview created successfully');
            previewImg.src = e.target.result;
            imagePreview.style.display = 'block';
            uploadArea.style.display = 'none';
        };
        reader.onerror = function(e) {
            console.error('Error reading file:', e);
            showError('Error reading the selected file.');
        };
        reader.readAsDataURL(file);
    }

    function removeImage() {
        console.log('Removing image...');
        imageInput.value = '';
        uploadedFile = null; // Clear stored file
        imagePreview.style.display = 'none';
        uploadArea.style.display = 'block';
    }

    // Form submission
    function handleFormSubmit(event) {
        console.log('Form submission triggered');
        event.preventDefault();

        try {
            // Validate form
            console.log('Validating form...');
            if (!validateForm()) {
                console.log('Form validation failed');
                return;
            }

            console.log('Form validation passed, preparing submission...');

            // Show loading state
            showLoading(true);

            // Prepare form data
            const formData = new FormData(form);
            
            // Ensure we have the uploaded file
            if (uploadedFile) {
                formData.set('image', uploadedFile);
                console.log('File added to FormData:', uploadedFile.name);
            } else {
                console.error('No uploaded file found!');
                showLoading(false);
                showError('No image file selected. Please upload an image.');
                return;
            }

            // Log form data contents for debugging
            console.log('FormData contents:');
            for (let [key, value] of formData.entries()) {
                if (value instanceof File) {
                    console.log(`${key}: File(${value.name}, ${value.size} bytes)`);
                } else {
                    console.log(`${key}: ${value}`);
                }
            }

            // Submit form via AJAX
            console.log('Submitting form to /generate...');
            fetch('/generate', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                console.log('Response received:', response.status, response.statusText);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                showLoading(false);
                
                if (data.success) {
                    console.log('Card generation successful!');
                    showResult(data);
                } else {
                    console.error('Card generation failed:', data.error);
                    showError(data.error || 'An error occurred while generating the card.');
                }
            })
            .catch(error => {
                console.error('Request failed:', error);
                showLoading(false);
                showError('Network error: ' + error.message);
            });
        } catch (error) {
            console.error('Form submission error:', error);
            showLoading(false);
            showError('An unexpected error occurred: ' + error.message);
        }
    }

    function validateForm() {
        console.log('Validating form...');
        
        // Check if image is selected (use stored file)
        if (!uploadedFile) {
            console.log('Validation failed: No image file');
            showError('Please select an image file.');
            return false;
        }

        // Check if all traits are filled
        for (let i = 1; i <= 5; i++) {
            const traitInput = document.getElementById(`trait${i}`);
            if (!traitInput.value.trim()) {
                console.log(`Validation failed: Trait ${i} is empty`);
                showError(`Please fill in trait ${i}.`);
                traitInput.focus();
                return false;
            }
        }

        console.log('Form validation passed');
        return true;
    }

    function showLoading(show) {
        if (show) {
            generateBtn.style.display = 'none';
            loading.style.display = 'flex';
            resultSection.style.display = 'none';
        } else {
            generateBtn.style.display = 'inline-flex';
            loading.style.display = 'none';
        }
    }

    function showResult(data) {
        // Display generated card
        generatedCard.src = `/card/${encodeURIComponent(data.filename)}`;
        generatedCard.alt = `${data.character_name} Card`;
        
        // Display character name
        characterName.textContent = data.character_name;
        
        // Display card stats
        displayCardStats(data.card_data);
        
        // Display card ability
        displayCardAbility(data.card_data);
        
        // Store filename for download
        generatedCard.dataset.filename = data.filename;
        
        // Show result section
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });
        
        // Auto-download the generated card
        setTimeout(() => {
            downloadCard(data.filename);
        }, 500); // Small delay to ensure image is loaded
    }

    function displayCardStats(cardData) {
        let stats = [];
        
        // Display personality card stats
        if (cardData.stat1_name && cardData.stat1_value) {
            stats.push({ label: cardData.stat1_name, value: cardData.stat1_value });
        }
        if (cardData.stat2_name && cardData.stat2_value) {
            stats.push({ label: cardData.stat2_name, value: cardData.stat2_value });
        }
        
        // Add personality type info with kanji
        if (cardData.custom_type && cardData.custom_type_icon) {
            stats.push({ label: 'Type', value: `${cardData.custom_type_icon} ${cardData.custom_type}` });
        } else if (cardData.custom_type) {
            stats.push({ label: 'Type', value: cardData.custom_type });
        }

        cardStats.innerHTML = stats.map(stat => `
            <div class="stat-item">
                <span class="stat-label">${stat.label}</span>
                <span class="stat-value">${stat.value}</span>
            </div>
        `).join('');
    }

    function displayCardAbility(cardData) {
        const effectDesc = cardData.effect_description || 'No effect.';
        const titleText = 'Special Ability';
        
        cardAbility.innerHTML = `
            <div class="ability-name">${titleText}</div>
            <div class="ability-description">${effectDesc}</div>
        `;
    }

    function downloadCard(filename) {
        // Get filename from the generated card's dataset
        const cardImg = document.getElementById('generatedCard');
        const filenameToDownload = cardImg && cardImg.dataset.filename ? cardImg.dataset.filename : null;
        
        if (filenameToDownload) {
            console.log('Downloading card:', filenameToDownload);
            window.open(`/download/${encodeURIComponent(filenameToDownload)}`, '_blank');
        } else {
            console.error('No filename found for download');
            showError('Unable to download card. Please try generating again.');
        }
    }

    function resetForm() {
        console.log('Resetting form...');
        
        // Reset form
        form.reset();
        
        // Reset image preview and stored file
        removeImage();
        
        // Hide result section
        resultSection.style.display = 'none';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        console.log('Form reset complete');
    }

    function showError(message) {
        console.error('Showing error:', message);
        
        // Create or update error message
        let errorDiv = document.getElementById('errorMessage');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'errorMessage';
            errorDiv.style.cssText = `
                background: #fed7d7;
                color: #c53030;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                border: 1px solid #feb2b2;
                text-align: center;
                font-weight: 500;
                position: relative;
                z-index: 1000;
            `;
            form.insertBefore(errorDiv, form.firstChild);
        }
        
        errorDiv.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                <span style="font-size: 1.2em;">⚠️</span>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.style.display='none'" 
                        style="background: none; border: none; color: #c53030; font-size: 1.2em; cursor: pointer; margin-left: 10px;">✕</button>
            </div>
        `;
        errorDiv.style.display = 'block';
        
        // Scroll to error message
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Auto-hide after 8 seconds
        setTimeout(() => {
            if (errorDiv.style.display !== 'none') {
                errorDiv.style.display = 'none';
            }
        }, 8000);
    }

    // Help modal functions
    window.showHelp = function() {
        alert('How to Use the Personalised Card Generator:\\n\\n1. Upload an Image: Choose a clear image of your character. Supported formats: PNG, JPG, JPEG, GIF, BMP (max 16MB).\\n\\n2. Enter Character Traits: Write 5 interesting, creative things about your character. Be imaginative and specific!\\n\\n3. Customize (Optional): Add a custom descriptor for your card name, or leave blank for auto-generation.\\n\\n4. Generate & Download: Click "Generate Card" and wait for AI to create your epic trading card!');
    };

    // Add some visual feedback for form interactions
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateY(-2px)';
            this.parentElement.style.boxShadow = '0 5px 15px rgba(102, 126, 234, 0.1)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateY(0)';
            this.parentElement.style.boxShadow = 'none';
        });
    });

    // Add animation to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});
