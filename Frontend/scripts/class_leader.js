document.getElementById('back-btn').addEventListener('click', () => {
    alert('Back button clicked!');
    // Add navigation logic here
});

document.getElementById('logout-btn').addEventListener('click', () => {
    alert('Logging out...');
    // Add logout logic here
});

document.getElementById('start-meeting-btn').addEventListener('click', () => {
    alert('Starting meeting...');
    // Add meeting start logic here
});

document.getElementById('add-member-btn').addEventListener('click', () => {
    alert('Add member clicked!');
    // Add logic to add a member here
});

document.getElementById('delete-member-btn').addEventListener('click', () => {
    alert('Delete member clicked!');
    // Add logic to delete a member here
});

document.getElementById('view-members-btn').addEventListener('click', () => {
    alert('View members clicked!');
    // Add logic to view members here
});

document.getElementById('edit-member-btn').addEventListener('click', () => {
    alert('Edit member clicked!');
    // Add logic to edit a member here
});

document.getElementById('view-meetings-btn').addEventListener('click', () => {
    alert('View meetings clicked!');
    // Add logic to view meetings here
});

document.getElementById('view-notifications-btn').addEventListener('click', () => {
    alert('View notifications clicked!');
    // Add logic to view notifications here
});

document.addEventListener('DOMContentLoaded', () => {
    const memberList = document.getElementById('member-list');
    const addMemberBtn = document.getElementById('add-member-btn');
    const editMemberBtn = document.getElementById('edit-member-btn');

    // Fetch members from the backend API
    async function fetchMembers() {
        try {
            const response = await fetch('http://backend3.example.com/api/members');
            const members = await response.json();
            populateMemberList(members);
        } catch (error) {
            console.error('Error fetching members:', error);
        }
    }

    // Populate the member list dynamically
    function populateMemberList(members) {
        memberList.innerHTML = '';
        members.forEach(member => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <span class="member-name">${member.name}</span>
                <div class="member-actions">
                    <button class="edit" onclick="editMember(${member.id})">Edit</button>
                    <button class="delete" onclick="deleteMember(${member.id})">Delete</button>
                </div>
            `;
            memberList.appendChild(listItem);
        });
    }

    // Add member functionality
    addMemberBtn.addEventListener('click', () => {
        // Logic to add a new member
        console.log('Add member button clicked');
    });

    // Edit member functionality
    editMemberBtn.addEventListener('click', () => {
        // Logic to edit a member
        console.log('Edit member button clicked');
    });

    // Edit member handler
    window.editMember = function (id) {
        // Logic to edit a specific member
        console.log('Edit member with ID:', id);
    };

    // Delete member handler
    window.deleteMember = function (id) {
        // Logic to delete a specific member
        console.log('Delete member with ID:', id);
    };

    // Initial fetch of members
    fetchMembers();
});

