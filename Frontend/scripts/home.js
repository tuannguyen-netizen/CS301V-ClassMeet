window.tailwind.config = {
    darkMode: ['class'],
    theme: {
        extend: {
            colors: {
                border: 'hsl(var(--border))',
                input: 'hsl(var(--input))',
                ring: 'hsl(var(--ring))',
                background: 'hsl(var(--background))',
                foreground: 'hsl(var(--foreground))',
                primary: {
                    DEFAULT: 'hsl(var(--primary))',
                    foreground: 'hsl(var(--primary-foreground))'
                },
                secondary: {
                    DEFAULT: 'hsl(var(--secondary))',
                    foreground: 'hsl(var(--secondary-foreground))'
                },
                destructive: {
                    DEFAULT: 'hsl(var(--destructive))',
                    foreground: 'hsl(var(--destructive-foreground))'
                },
                muted: {
                    DEFAULT: 'hsl(var(--muted))',
                    foreground: 'hsl(var(--muted-foreground))'
                },
                accent: {
                    DEFAULT: 'hsl(var(--accent))',
                    foreground: 'hsl(var(--accent-foreground))'
                },
                popover: {
                    DEFAULT: 'hsl(var(--popover))',
                    foreground: 'hsl(var(--popover-foreground))'
                },
                card: {
                    DEFAULT: 'hsl(var(--card))',
                    foreground: 'hsl(var(--card-foreground))'
                },
            },
        }
    }
}

document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("You are not logged in. Redirecting to login page...");
        window.location.href = "login.html";
        return;
    }

    try {
        // Fetch user profile
        const userResponse = await fetch("/user/me", {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (userResponse.ok) {
            const userData = await userResponse.json();
            document.getElementById("user-name").textContent = `Name: ${userData.username}`;
            document.getElementById("user-email").textContent = `Email: ${userData.email}`;
        } else {
            alert("Failed to load user data. Redirecting to login page...");
            window.location.href = "login.html";
        }

        // Fetch class list
        const classResponse = await fetch("/class/my-classes", {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (classResponse.ok) {
            const classes = await classResponse.json();
            const classList = document.getElementById("class-list");
            classList.innerHTML = ""; // Clear existing list
            classes.forEach(classItem => {
                const li = document.createElement("li");
                li.textContent = classItem.class_name;
                classList.appendChild(li);
            });
        } else {
            console.error("Failed to load classes.");
        }
    } catch (error) {
        console.error("Error fetching data:", error);
        alert("An error occurred. Please try again.");
    }

    // Logout functionality
    document.getElementById("logout-button").addEventListener("click", function () {
        localStorage.removeItem("token");
        window.location.href = "login.html";
    });

    // Redirect to create class page
    document.getElementById("create-class-button").addEventListener("click", function () {
        window.location.href = "create_class.html";
    });

    // Redirect to join class page
    document.getElementById("join-class-button").addEventListener("click", function () {
        window.location.href = "class_member.html";
    });
});
// Redirect to meeting page
document.getElementById("meeting-button").addEventListener("click", function () {
    window.location.href = "meeting.html";
});
// Redirect to profile page
document.getElementById("profile-button").addEventListener("click", function () {
    window.location.href = "profile.html";
});