document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("You are not logged in. Redirecting to login page...");
        window.location.href = "login.html";
        return;
    }

    try {
        const response = await fetch("/user/me", {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const userData = await response.json();
            document.getElementById("user-name").textContent = `Name: ${userData.username}`;
            document.getElementById("user-email").textContent = `Email: ${userData.email}`;
        } else {
            alert("Failed to load user data. Redirecting to login page...");
            window.location.href = "login.html";
        }
    } catch (error) {
        console.error("Error fetching user data:", error);
        alert("An error occurred. Please try again.");
    }

    try {
        const classResponse = await fetch("/class/my-classes", {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (classResponse.ok) {
            const classes = await classResponse.json();
            const classList = document.getElementById("class-list");
            classes.forEach(classItem => {
                const li = document.createElement("li");
                li.textContent = classItem.class_name;
                classList.appendChild(li);
            });
        } else {
            console.error("Failed to load classes.");
        }
    } catch (error) {
        console.error("Error fetching classes:", error);
    }

    document.getElementById("logout-button").addEventListener("click", function () {
        localStorage.removeItem("token");
        window.location.href = "login.html";
    });
});
