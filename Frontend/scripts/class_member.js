document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("You are not logged in. Redirecting to login page...");
        window.location.href = "login.html";
        return;
    }

    try {
        const response = await fetch("/class/my-classes", {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const classes = await response.json();
            const classList = document.getElementById("member-classes");
            classes.forEach(classItem => {
                const div = document.createElement("div");
                div.className = "class-item";
                div.innerHTML = `
                    <h3>${classItem.class_name}</h3>
                    <p>${classItem.description}</p>
                `;
                classList.appendChild(div);
            });
        } else {
            alert("Failed to load classes.");
        }
    } catch (error) {
        console.error("Error fetching classes:", error);
        alert("An error occurred. Please try again.");
    }
});
