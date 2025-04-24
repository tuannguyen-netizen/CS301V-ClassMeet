document.getElementById('create-class-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const className = document.getElementById('class-name').value.trim();

    if (!className) {
        alert('Please enter a class name.');
        return;
    }

    try {
        const response = await fetch('http://backend2.example.com/api/create-class', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ class_name: className }),
        });

        if (response.ok) {
            alert('Class created successfully!');
            window.location.href = 'class_leader.html';
        } else {
            const error = await response.json();
            alert(`Error: ${error.message}`);
        }
    } catch (error) {
        console.error('Error creating class:', error);
        alert('An error occurred while creating the class. Please try again.');
    }
});

document.getElementById('back-btn').addEventListener('click', () => {
    window.location.href = 'class_leader.html';
});
document.getElementById('logout-btn').addEventListener('click', () => {
    alert('Logging out...');
    // Add logout logic here
});

document.getElementById('join-meeting-btn').addEventListener('click', () => {
    alert('Joining meeting...');
    // Add meeting start logic here)
});

document.getElementById('view-members-btn').addEventListener('click', () => {
    alert('View members clicked!');
    // Add logic to view members here
});

document.getElementById('view-meetings-btn').addEventListener('click', () => {
    alert('View meetings clicked!');
    // Add logic to view meetings here
});

document.getElementById('view-notifications-btn').addEventListener('click', () => {
    alert('View notifications clicked!');
    // Add logic to view notifications here
}
);