document.getElementById("create-class-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const token = localStorage.getItem("token");
    const className = document.getElementById("class-name").value;
    const description = document.getElementById("class-description").value;

    try {
        const response = await fetch("/class/create", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ class_name: className, description }),
        });

        if (response.ok) {
            alert("Class created successfully!");
            window.location.href = "home.html";
        } else {
            const errorData = await response.json();
            alert(`Failed to create class: ${errorData.detail}`);
        }
    } catch (error) {
        console.error("Error creating class:", error);
        alert("An error occurred. Please try again.");
    }
});
