document.querySelector("form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.querySelector(".field input[type='text']").value;
    const password = document.querySelector(".field input[type='password']").value;

    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("token", data.token);
            alert("Login successful!");
            window.location.href = "home.html";
        } else {
            const errorData = await response.json();
            alert(`Login failed: ${errorData.detail}`);
        }
    } catch (error) {
        console.error("Error during login:", error);
        alert("An error occurred. Please try again.");
    }
});
