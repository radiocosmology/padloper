import React, { useState, useEffect } from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableRow from '@mui/material/TableRow';
import axios from 'axios';

function UserManagementPage() {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [userGroups, setUserGroups] = useState([]);
    const [selectedUserGroups, setSelectedUserGroups] = useState([]);
    const [userGroupAssociations, setUserGroupAssociations] = useState([]);

    useEffect(() => {
        // Fetch users from API and set them in state
        fetchUsers();
        // Fetch user groups from API and set them in state
        fetchUserGroups();
    }, []);

    useEffect(() => {
        if (selectedUser) {
            // Fetch user group associations for the selected user
            fetchUserGroupAssociations(selectedUser.id);
        }
    }, [selectedUser]);

    const fetchUsers = () => {
       
        let input = '/api/get_user_list'
        fetch(input).then(
            res => res.json()
            ).then(data => {
                console.log(data)
                setUsers(data.result);
            })
    };

    const fetchUserGroups = () => {
        // Mocking user groups data for demonstration
       
        let input = '/api/get_user_group_list'
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setUserGroups(data.result);
        })
    };

    const handleUserSelect = (event, value) => {
        // Update selected user when user is selected from autocomplete
        setSelectedUser(value);
        // Reset selected user groups
        setSelectedUserGroups([]);
    };

    const fetchUserGroupAssociations = (userId) => {
        // Mocking user group associations data for demonstration
        const mockUserGroupAssociations = [
            { id: 1, name: 'Group 1', permissions: ['Permission 1', 'Permission 2'] },
            { id: 2, name: 'Group 2', permissions: ['Permission 2', 'Permission 3'] },
            // Add more user group associations as needed
        ];
        let input = '/api/get_user_groups';
        input += `?username=${selectedUser.name}`

        fetch(input).then(
            res => res.json()
        ).then(data => {
            console.log(data);
            setUserGroupAssociations(data.result);
        })

    };

    const handleUserGroupSelect = (event, values) => {
        // Update selected user groups
        setSelectedUserGroups(values);
    };

    const handleAddToGroups = () => {
        // Add selected user to selected user groups
        if (selectedUser && selectedUserGroups.length > 0) {

            let input = '/api/new_set_usergroup'
            const formData = new FormData();
            formData.append('user', selectedUser.name);
            formData.append('group', selectedUserGroups.map(obj => obj.name).join(";"));
            console.log(formData)
             const requestOptions = {
                method: 'POST', 
                body: formData
              };
            fetch(input, requestOptions)
              .then(res => res.json())
              .then(data => {
                console.log("res", data);
              })
              .catch(err => {
                console.error("Err:", err);
              })


            console.log(`Adding user ${selectedUser.name} to groups:`, selectedUserGroups);
            // Clear selected user and user groups after adding
            setSelectedUser(null);
            setSelectedUserGroups([]);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '80%', margin: '0 auto' }}>
            <h1>User Management</h1>
            <div style={{ marginBottom: '20px', width: '100%' }}>
                <Autocomplete
                    options={users}
                    getOptionLabel={(user) => user.name}
                    onChange={handleUserSelect}
                    renderInput={(params) => <TextField {...params} label="Search Users" variant="outlined" />}
                />
            </div>
            {selectedUser && (
                <div style={{ marginBottom: '20px', width: '100%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                        <p style={{ marginRight: '10px', fontSize: '1.2rem' }}>User ID:</p>
                        <p style={{ fontSize: '1.2rem' }}>{selectedUser.name}</p>
                        <p style={{ marginLeft: '20px', marginRight: '10px', fontSize: '1.2rem' }}>Institution:</p>
                        <p style={{ fontSize: '1.2rem' }}>{selectedUser.institution}</p>
                    </div>
                    <h2>User Groups</h2>
                    <TableContainer>
                        <Table>
                            <TableBody>
                                {userGroupAssociations.map((group) => (
                                    <TableRow key={group.id}>
                                        <TableCell>
                                            <a href="#">{group.name}</a>
                                        </TableCell>
                                        <TableCell>
                                            {group.permissions.join(', ')}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <div style={{ marginBottom: '10px', marginTop: '10px', width: '100%' }}>
                        <Autocomplete
                            multiple
                            options={userGroups}
                            getOptionLabel={(group) => group.name}
                            onChange={handleUserGroupSelect}
                            renderInput={(params) => <TextField {...params} label="Select User Groups" variant="outlined" />}
                        />
                    </div>
                    <Button variant="contained" color="primary" onClick={handleAddToGroups}>
                        Add to User Groups
                    </Button>
                </div>
            )}
        </div>
    );
}

export default UserManagementPage;
