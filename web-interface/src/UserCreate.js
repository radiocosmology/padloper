import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';

// TODO:
// MAKE THIS PAGE ONLY VISIBLE TO AN ADMIN / SPECIFIED INDIVIDUAL
function UserCreatePage() {
    const [userName, setUserName] = useState('');
    const [institution, setInstitution] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    const handleUserNameChange = (event) => {
        setUserName(event.target.value);
    };

    const handleInstitutionChange = (event) => {
        setInstitution(event.target.value);
    };

    const handleAddUser = () => {
        // Clear previous messages
        setSuccessMessage('');
        setErrorMessage('');
        
        // Make API call to create user
        let input = '/api/new_user'
        const formData = new FormData();
        formData.append('username', userName);
        formData.append('institution', institution);
        const requestOptions = {
            method: 'POST', 
            body: formData
        };
        fetch(input, requestOptions)
          .then(res => res.json())
          .then(data => {
            setUserName('');
            setInstitution('');
            setSuccessMessage('User created successfully.');
          })
          .catch(error => {
            // Show error message if request fails
            setErrorMessage(`Error: ${error.response.data.message}`);
          })

        // axios.post('/api/create_user', { userName, institution })
        //     .then(response => {
        //         // Reset fields if successful and show success message
        //         setUserName('');
        //         setInstitution('');
        //         setSuccessMessage('User created successfully.');
        //     })
        //     .catch(error => {
        //         // Show error message if request fails
        //         setErrorMessage(`Error: ${error.response.data.message}`);
        //     });
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '80%', margin: '0 auto' }}>
            <h1>Create User</h1>
            <TextField
                label="User Name"
                variant="outlined"
                value={userName}
                onChange={handleUserNameChange}
                style={{ marginBottom: '20px', width: '100%' }}
            />
            <TextField
                label="Institution"
                variant="outlined"
                value={institution}
                onChange={handleInstitutionChange}
                style={{ marginBottom: '20px', width: '100%' }}
            />
            <div style={{ marginBottom: '20px', width: '100%' }}>
                <Button variant="contained" color="primary" onClick={handleAddUser}>
                    Add User
                </Button>
            </div>
            {successMessage && (
                <p style={{ color: 'green' }}>{successMessage}</p>
            )}
            {errorMessage && (
                <p style={{ color: 'red' }}>{errorMessage}</p>
            )}
        </div>
    );
}

export default UserCreatePage;
