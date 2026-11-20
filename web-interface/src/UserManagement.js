import React, { useCallback, useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
    Alert, Box, Button, Chip, CircularProgress, FormControlLabel, Paper,
    Stack, Switch, Table, TableBody, TableCell, TableContainer, TableHead,
    TableRow, TextField, Typography,
} from '@mui/material';
import { getJson, postForm } from './paths.js';
import ErrorMessage from './ErrorMessage.js';
import ConfirmDialog from './ConfirmDialog.js';
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
    const [notice, setNotice] = useState(null);
    const [filter, setFilter] = useState('');
    const [showDeactivated, setShowDeactivated] = useState(false);
    const [reactivating, setReactivating] = useState(null); // name awaiting confirm
    const [busy, setBusy] = useState(false);

    const load = useCallback(async () => {
        try {
            const data = await getJson(
                `/api/get_user_list${showDeactivated ? '?include_disabled=1' : ''}`);
            setUsers(sortByName(data.result));
            setError(null);
        } catch (err) {
            setUsers([]);
            setError(err.message);
        } finally {
            setLoaded(true);
        }
    }, [showDeactivated]);

    useEffect(() => { load(); }, [load]);

    const confirmReactivate = async () => {
        setBusy(true);
        setError(null);
        try {
            await postForm('/api/enable_user', { username: reactivating });
            setNotice(`Reactivated ${reactivating}. They are back in the readonly group.`);
            setReactivating(null);
            await load();
        } catch (err) {
            setError(err.message);
        } finally {
            setBusy(false);
        }
    };

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

            <Stack direction="row" spacing={3} alignItems="center" sx={{ mb: 2 }}>
                <TextField
                    label="Filter users"
                    variant="outlined"
                    size="small"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    sx={{ width: 320 }}
                />
                <FormControlLabel
                    control={
                        <Switch
                            checked={showDeactivated}
                            onChange={(e) => setShowDeactivated(e.target.checked)}
                        />
                    }
                    label="Show deactivated users"
                />
            </Stack>

            <ErrorMessage errorMessage={error} />
            {notice && (
                <Alert severity="success" onClose={() => setNotice(null)} sx={{ mb: 2 }}>
                    {notice}
                </Alert>
            )}

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
                            {shown.map((user) => user.active === false ? (
                                <TableRow key={user.name} hover sx={{ opacity: 0.7 }}>
                                    <TableCell>{user.name}</TableCell>
                                    <TableCell>
                                        <Chip
                                            size="small"
                                            color="warning"
                                            variant="outlined"
                                            label={`Deactivated${user.uid_disabled ? ` by ${user.uid_disabled}` : ''}`}
                                        />
                                    </TableCell>
                                    <TableCell align="right">&mdash;</TableCell>
                                    <TableCell align="right">
                                        <Button
                                            size="small"
                                            disabled={busy}
                                            onClick={() => setReactivating(user.name)}
                                        >
                                            Reactivate
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ) : (
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
            )}

            <ConfirmDialog
                open={reactivating !== null}
                title="Reactivate user?"
                message={`Reactivate ${reactivating}? They will be able to log in again and will start in the readonly group; add them back to other groups afterwards.`}
                confirmLabel="Reactivate"
                confirmColor="primary"
                busy={busy}
                onConfirm={confirmReactivate}
                onClose={() => setReactivating(null)}
            />
        </Box>
    );
}

export default UserManagementPage;
