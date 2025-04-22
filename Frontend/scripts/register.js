document.getElementById("register-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, email, password }),
        });

        if (response.ok) {
            alert("Registration successful! Redirecting to login page...");
            window.location.href = "login.html"; // Chuyển hướng đến trang Login
        } else {
            const errorData = await response.json();
            alert(`Registration failed: ${errorData.detail}`);
        }
    } catch (error) {
        console.error("Error during registration:", error);
        alert("An error occurred. Please try again.");
    }
});
