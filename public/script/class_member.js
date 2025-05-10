import React from 'react';

const ClassMember = () => {
    return (
        <div>
            <h1>Class Members</h1>
            <ul id="member-list">
                {/* Danh sách thành viên sẽ được hiển thị ở đây */}
            </ul>
            <Link to="/class_leader">Back to Class Leader</Link>
        </div>
    );
};

export default ClassMember.listen(5000);
