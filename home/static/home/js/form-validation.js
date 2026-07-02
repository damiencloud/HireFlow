/**
 * HireFlow - Client-Side Form Validation Module (Vanilla JS)
 * Handles real-time validations, state checks, and is-valid/is-invalid indicators.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Query all forms on the current page
    const forms = document.querySelectorAll("form");
    
    forms.forEach(form => {
        // Find inputs that need validation
        const inputs = form.querySelectorAll("input, textarea, select");
        
        inputs.forEach(input => {
            // Bind real-time validation on typing or focus loss
            input.addEventListener("input", () => validateField(input));
            input.addEventListener("blur", () => validateField(input));
            input.addEventListener("change", () => validateField(input));
        });

        // Intercept form submissions
        form.addEventListener("submit", (event) => {
            let isFormValid = true;

            // Validate all inputs once more on submit
            inputs.forEach(input => {
                const isValid = validateField(input);
                if (!isValid) {
                    isFormValid = false;
                }
            });

            // Specific validation check for min/max salary range in job posting form
            const minSalInput = form.querySelector('input[name="salary_min"]');
            const maxSalInput = form.querySelector('input[name="salary_max"]');
            if (minSalInput && maxSalInput) {
                const isSalaryValid = validateSalaryRange(minSalInput, maxSalInput);
                if (!isSalaryValid) {
                    isFormValid = false;
                }
            }

            // Block submission event if inputs fail
            if (!isFormValid) {
                event.preventDefault();
                event.stopPropagation();
                
                // Render a temporary global alert helper if available
                showGlobalValidationAlert(form);
            }
        });
    });

    /**
     * Core Field Validator function
     * Evaluates field constraints and updates CSS states.
     */
    function validateField(input) {
        // Skip validation for non-interactive button fields or optional unchecked fields
        if (input.type === "submit" || input.type === "button" || input.type === "reset") {
            return true;
        }

        const value = input.value.trim();
        let isValid = true;
        let errorMessage = "";

        // Check 1: Required constraint
        if (input.hasAttribute("required")) {
            if (!value || (input.type === "checkbox" && !input.checked)) {
                isValid = false;
                errorMessage = input.type === "checkbox" 
                    ? "You must accept the terms of service." 
                    : "This field is required.";
            }
        }

        // Check 2: Email format regex match
        if (isValid && input.type === "email" && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = "Please enter a valid email address (e.g. name@domain.com).";
            }
        }

        // Check 3: Password length bounds
        if (isValid && input.type === "password" && value) {
            if (value.length < 8) {
                isValid = false;
                errorMessage = "Password must be at least 8 characters long.";
            }
        }

        // Check 4: Upload file formats (Resume PDF check)
        if (isValid && input.type === "file" && input.files && input.files.length > 0) {
            const file = input.files[0];
            const isPDF = file.type === "application/pdf" || file.name.endsWith(".pdf");
            const isTooLarge = file.size > 5 * 1024 * 1024; // 5MB limit

            if (!isPDF) {
                isValid = false;
                errorMessage = "Only PDF document uploads are accepted.";
            } else if (isTooLarge) {
                isValid = false;
                errorMessage = "File size exceeds the 5MB limits.";
            }
        }

        // Update visual display indicators
        updateFieldUIState(input, isValid, errorMessage);
        return isValid;
    }

    /**
     * Salary Range Compare Validator
     * Confirms maximum compensation limit is higher than minimum threshold.
     */
    function validateSalaryRange(minInput, maxInput) {
        const minVal = parseFloat(minInput.value);
        const maxVal = parseFloat(maxInput.value);
        
        if (!isNaN(minVal) && !isNaN(maxVal)) {
            if (maxVal <= minVal) {
                updateFieldUIState(maxInput, false, "Maximum salary must be greater than minimum salary.");
                return false;
            }
        }
        return true;
    }

    /**
     * Updates Bootstrap styling borders and appends descriptive error tags
     */
    function updateFieldUIState(input, isValid, errorMessage) {
        // Remove existing state classes
        input.classList.remove("is-valid", "is-invalid");
        
        // Remove existing custom feedback nodes
        const parent = input.parentElement;
        let feedback = parent.querySelector(".invalid-feedback");
        if (feedback) {
            feedback.remove();
        }

        if (!isValid) {
            input.classList.add("is-invalid");
            
            // Create invalid feedback description block
            const errorDiv = document.createElement("div");
            errorDiv.className = "invalid-feedback d-block mt-1";
            errorDiv.style.fontSize = "0.75rem";
            errorDiv.style.fontWeight = "600";
            errorDiv.textContent = errorMessage;
            parent.appendChild(errorDiv);
        } else {
            // Only add is-valid state if field contains values
            if (input.value.trim().length > 0 || (input.type === "checkbox" && input.checked)) {
                input.classList.add("is-valid");
            }
        }
    }

    /**
     * Renders a floating modular validation warning toast if user clicks submit with invalid fields
     */
    function showGlobalValidationAlert(form) {
        // Prevent duplicate alerts
        if (form.querySelector(".validation-alert-banner")) {
            return;
        }

        const alertBanner = document.createElement("div");
        alertBanner.className = "alert alert-danger border-0 shadow-sm rounded-3 mt-3 validation-alert-banner d-flex align-items-center gap-2.5";
        alertBanner.style.fontSize = "0.85rem";
        alertBanner.style.fontWeight = "600";
        alertBanner.innerHTML = `
            <i class="bi bi-exclamation-triangle-fill fs-5"></i>
            <span>Please correct the highlighted fields before submitting.</span>
        `;
        
        form.appendChild(alertBanner);
        
        // Dismiss after 4 seconds
        setTimeout(() => {
            alertBanner.remove();
        }, 4000);
    }
});
