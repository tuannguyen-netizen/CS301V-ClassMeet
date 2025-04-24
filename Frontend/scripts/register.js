document.getElementById("register-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match. Please try again.");
        return;
    }

    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            alert("Registration successful! Redirecting to home page...");
            window.location.href = "home.html"; // Chuyển hướng đến trang Home
        } else {
            const errorData = await response.json();
            alert(`Registration failed: ${errorData.detail}`);
        }
    } catch (error) {
        console.error("Error during registration:", error);
        alert("An error occurred. Please try again.");
    }
});
