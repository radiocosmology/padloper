import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
    Box, Button, Chip, CircularProgress, Paper, Stack, Table, TableBody,
    TableCell, TableContainer, TableHead, TableRow, TextField, Typography,
} from '@mui/material';
import { getJson } from './paths.js';
import ErrorMessage from './ErrorMessage.js';
import {
    effectivePermissions, groupEditPath, sortByName, userEditPath,
} from './userAdminUtils.js';

/**
 * Lists every user with their groups, and links to a page where an admin can
 * edit an individual user's group memberships.
 */
function UserManagementPage() {
    const [users, setUsers] = useState([]);
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('');

    useEffect(() => {
        let cancelled = false;
        getJson('/api/get_user_list')
            .then((data) => {
                if (cancelled) return;
                setUsers(sortByName(data.result));
                setError(null);
            })
            .catch((err) => {
                if (cancelled) return;
                setUsers([]);
                setError(err.message);
            })
            .finally(() => {
                if (!cancelled) setLoaded(true);
            });
        return () => { cancelled = true; };
    }, []);

    const needle = filter.trim().toLowerCase();
    const shown = users.filter((user) =>
        user.name.toLowerCase().includes(needle));

    return (
        <Box sx={{ width: '90%', maxWidth: 1100, mx: 'auto', my: 3 }}>
            <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                flexWrap="wrap"
                sx={{ mb: 2, gap: 1 }}
            >
                <Typography variant="h4" component="h1">
                    User Management
                </Typography>
                <Stack direction="row" spacing={1}>
                    <Button
                        component={RouterLink}
                        to="/manage/users/groups"
                        variant="outlined"
                    >
                        User Groups
                    </Button>
                    <Button
                        component={RouterLink}
                        to="/users"
                        variant="contained"
                    >
                        Add User
                    </Button>
                </Stack>
            </Stack>

            <TextField
                label="Filter users"
                variant="outlined"
                size="small"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                sx={{ mb: 2, width: 320 }}
            />

            <ErrorMessage errorMessage={error} />

            {!loaded ? (
                <CircularProgress />
            ) : (
                <TableContainer component={Paper}>
                    <Table size="small" aria-label="users">
                        <TableHead>
                            <TableRow>
                                <TableCell>User</TableCell>
                                <TableCell>Groups</TableCell>
                                <TableCell align="right">Permissions</TableCell>
                                <TableCell align="right">Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {shown.map((user) => (
                                <TableRow key={user.name} hover>
                                    <TableCell>
                                        <RouterLink to={userEditPath(user.name)}>
                                            {user.name}
                                        </RouterLink>
                                    </TableCell>
                                    <TableCell>
                                        {(user.groups || []).length === 0 ? (
                                            <em>none</em>
                                        ) : (
                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                                {sortByName(user.groups).map((group) => (
                                                    <Chip
                                                        key={group.name}
                                                        label={group.name}
                                                        size="small"
                                                        component={RouterLink}
                                                        to={groupEditPath(group.name)}
                                                        clickable
                                                    />
                                                ))}
                                            </Box>
                                        )}
                                    </TableCell>
                                    <TableCell align="right">
                                        {effectivePermissions(user).length}
                                    </TableCell>
                                    <TableCell align="right">
                                        <Button
                                            size="small"
                                            component={RouterLink}
                                            to={userEditPath(user.name)}
                                        >
                                            Edit
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {shown.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={4}>
                                        <em>
                                            {users.length === 0
                                                ? 'No users found.'
                                                : 'No users match the filter.'}
                                        </em>
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}        </Box>
    );
}

export default UserManagementPage;
