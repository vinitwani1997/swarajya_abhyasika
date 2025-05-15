document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('register-form');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const passwordMatchError = document.getElementById('password-match-error');
    const strengthMeter = document.getElementById('password-strength');

    // Hardcoded admin credentials (for demo only - in production this should be server-side)
    const ADMIN_CREDENTIALS = {
        email: "admin@swarajya.com",
        password: "SwarajyaAdmin@2024", // Change this in production!
        name: "System Administrator",
        role: "admin"
    };

    // Password strength indicator
    passwordInput.addEventListener('input', function() {
        const strength = checkPasswordStrength(this.value);
        updateStrengthMeter(strength);
    });

    // Confirm password validation
    confirmPasswordInput.addEventListener('input', function() {
        if (this.value !== passwordInput.value) {
            passwordMatchError.textContent = "Passwords don't match";
            this.classList.add('error');
        } else {
            passwordMatchError.textContent = "";
            this.classList.remove('error');
        }
    });

    // Form submission
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate passwords match
        if (passwordInput.value !== confirmPasswordInput.value) {
            alert("Passwords don't match");
            return;
        }

        // Create user object
        const newUser = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim().toLowerCase(),
            password: passwordInput.value, // In production, this should be hashed
            role: document.getElementById('user-role').value
        };

        // Validate email format
        if (!validateEmail(newUser.email)) {
            alert("Please enter a valid email address");
            return;
        }

        // Get existing users from localStorage
        let users = JSON.parse(localStorage.getItem('users')) || [];
        
        // Preserve admin credentials if they don't exist
        if (!users.some(u => u.role === 'admin')) {
            users.push(ADMIN_CREDENTIALS);
        }

        // Check if email already exists
        if (users.some(user => user.email === newUser.email)) {
            alert("This email is already registered");
            return;
        }

        // Add new user
        users.push(newUser);
        localStorage.setItem('users', JSON.stringify(users));
        
        alert("Registration successful! Please login.");
        window.location.href = "login.html";
    });

    // Helper functions
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function checkPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.match(/[a-z]+/)) strength++;
        if (password.match(/[A-Z]+/)) strength++;
        if (password.match(/[0-9]+/)) strength++;
        if (password.match(/[$@#&!]+/)) strength++;
        return strength;
    }

    function updateStrengthMeter(strength) {
        strengthMeter.innerHTML = '';
        const strengthText = ['Very Weak', 'Weak', 'Medium', 'Strong', 'Very Strong'];
        
        for (let i = 0; i < 5; i++) {
            const bar = document.createElement('div');
            bar.className = i < strength ? 'strength-bar active' : 'strength-bar';
            strengthMeter.appendChild(bar);
        }
        
        const text = document.createElement('span');
        text.className = 'strength-text';
        text.textContent = strengthText[strength - 1] || '';
        strengthMeter.appendChild(text);
    }
});
