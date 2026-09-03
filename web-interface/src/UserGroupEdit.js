import React, { useCallback, useEffect, useState } from 'react';
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom';
import {
    Alert, Autocomplete, Box, Button, CircularProgress, Paper, Stack, Table,
    TableBody, TableCell, TableContainer, TableHead, TableRow, TextField,
    Tooltip, Typography,
} from '@mui/material';
import { getJson, postForm } from './paths.js';
import ErrorMessage from './ErrorMessage.js';
import ConfirmDialog from './ConfirmDialog.js';
import { ADMIN_GROUP, sortByName, userEditPath } from './userAdminUtils.js';

/**
 * Edit a single user group: add and remove permissions, add and remove
 * members, or delete the group. The group's name comes from the URL.
 */
function UserGroupEditPage() {
    const { name } = useParams();
    const navigate = useNavigate();
    const [group, setGroup] = useState(null);
    const [members, setMembers] = useState([]);
    const [allUsers, setAllUsers] = useState([]);
    const [allPermissions, setAllPermissions] = useState([]);
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(null);
    const [notice, setNotice] = useState(null);
    const [busy, setBusy] = useState(false);
    const [permissionsToAdd, setPermissionsToAdd] = useState([]);
    const [usersToAdd, setUsersToAdd] = useState([]);
    const [removingMember, setRemovingMember] = useState(null);
    const [confirmingDelete, setConfirmingDelete] = useState(false);

    const isAdminGroup = name === ADMIN_GROUP;

    const load = useCallback(async () => {
        try {
            const [groupData, userData, permData] = await Promise.all([
                getJson('/api/get_user_group_list'),
                getJson('/api/get_user_list'),
                getJson('/api/get_all_permissions'),
            ]);
            const found = (groupData.result || []).find((g) => g.name === name) || null;
            const users = sortByName(userData.result);
            setGroup(found);
            setAllUsers(users);
            setMembers(users.filter((user) =>
                (user.groups || []).some((g) => g.name === name)));
            setAllPermissions((permData.result || []).slice().sort());
            setError(found ? null : `Group "${name}" was not found.`);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoaded(true);
        }
    }, [name]);

    useEffect(() => { load(); }, [load]);

    const currentPermissions = group ? (group.permissions || []).slice().sort() : [];
    const addablePermissions = allPermissions.filter(
        (perm) => !currentPermissions.includes(perm));
    const memberNames = new Set(members.map((user) => user.name));
    const addableUsers = allUsers.filter((user) => !memberNames.has(user.name));

    /** Save `nextPermissions` as the group's complete permission list. */
    const savePermissions = async (nextPermissions, successMessage) => {
        setBusy(true);
        setError(null);
        try {
            // Permission names contain ';', so the API takes a ','-separated
            // list here.
            await postForm('/api/set_usergroup_permissions', {
                name,
                permissions: nextPermissions.join(','),
            });
            setNotice(successMessage);
            await load();
        } catch (err) {
            setError(err.message);
        } finally {
            setBusy(false);
        }
    };

    const removePermission = (perm) => savePermissions(
        currentPermissions.filter((p) => p !== perm),
        `Removed permission ${perm} from ${name}.`);

    const addPermissions = async () => {
        await savePermissions(
            [...currentPermissions, ...permissionsToAdd],
            `Added ${permissionsToAdd.join(', ')} to ${name}.`);
        setPermissionsToAdd([]);
    };

    const confirmRemoveMember = async () => {
        setBusy(true);
        setError(null);
        try {
            await postForm('/api/remove_user_group', { user: removingMember, group: name });
            setNotice(`Removed ${removingMember} from ${name}.`);
            setRemovingMember(null);
            await load();
        } catch (err) {
            setError(err.message);
        } finally {
            setBusy(false);
        }
    };

    const addMembers = async () => {
        setBusy(true);
        setError(null);
        const added = [];
        const failed = [];
        for (const user of usersToAdd) {
            try {
                await postForm('/api/new_set_usergroup', { user: user.name, group: name });
                added.push(user.name);
            } catch (err) {
                failed.push(`${user.name} (${err.message})`);
            }
        }
        if (added.length > 0) setNotice(`Added ${added.join(', ')} to ${name}.`);
        if (failed.length > 0) setError(`Could not add ${failed.join('; ')}`);
        setUsersToAdd([]);
        await load();
        setBusy(false);
    };

    const confirmDelete = async () => {
        setBusy(true);
        setError(null);
        try {
            await postForm('/api/disable_usergroup', { name });
            navigate('/manage/users/groups');
        } catch (err) {
            setError(err.message);
            setConfirmingDelete(false);
            setBusy(false);
        }
    };

    return (
        <Box sx={{ width: '90%', maxWidth: 1100, mx: 'auto', my: 3 }}>
            <Button component={RouterLink} to="/manage/users/groups" sx={{ mb: 1 }}>
                &larr; All groups
            </Button>
            <Typography variant="h4" component="h1" sx={{ mb: 1 }}>
                Group: {name}
            </Typography>
            {group && group.comments && (
                <Typography color="text.secondary" sx={{ mb: 2 }}>
                    {group.comments}
                </Typography>
            )}
            {isAdminGroup && (
                <Alert severity="info" sx={{ mb: 2 }}>
                    Members of this group can manage users and groups regardless
                    of the permissions listed here. The group cannot be deleted
                    and its last member cannot be removed.
                </Alert>
            )}

            <ErrorMessage errorMessage={error} />
            {notice && (
                <Alert severity="success" onClose={() => setNotice(null)} sx={{ mb: 2 }}>
                    {notice}
                </Alert>
            )}

            {!loaded ? (
                <CircularProgress />
            ) : group && (
                <Stack spacing={4}>
                    <Box>
                        <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
                            Permissions
                        </Typography>
                        <TableContainer component={Paper}>
                            <Table size="small" aria-label="permissions">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Permission</TableCell>
                                        <TableCell align="right">Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {currentPermissions.map((perm) => (
                                        <TableRow key={perm} hover>
                                            <TableCell sx={{ fontFamily: 'monospace' }}>{perm}</TableCell>
                                            <TableCell align="right">
                                                <Button
                                                    size="small"
                                                    color="error"
                                                    disabled={busy}
                                                    onClick={() => removePermission(perm)}
                                                >
                                                    Remove
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {currentPermissions.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={2}>
                                                <em>This group grants no permissions.</em>
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                        <Stack direction="row" spacing={2} alignItems="flex-start" sx={{ mt: 2 }}>
                            <Autocomplete
                                multiple
                                options={addablePermissions}
                                value={permissionsToAdd}
                                onChange={(event, value) => setPermissionsToAdd(value)}
                                sx={{ flexGrow: 1 }}
                                renderInput={(params) => (
                                    <TextField {...params} label="Add permissions" variant="outlined" />
                                )}
                            />
                            <Button
                                variant="contained"
                                disabled={busy || permissionsToAdd.length === 0}
                                onClick={addPermissions}
                                sx={{ mt: 1 }}
                            >
                                Add
                            </Button>
                        </Stack>
                    </Box>

                    <Box>
                        <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
                            Members
                        </Typography>
                        <TableContainer component={Paper}>
                            <Table size="small" aria-label="members">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>User</TableCell>
                                        <TableCell align="right">Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {members.map((user) => (
                                        <TableRow key={user.name} hover>
                                            <TableCell>
                                                <RouterLink to={userEditPath(user.name)}>
                                                    {user.name}
                                                </RouterLink>
                                            </TableCell>
                                            <TableCell align="right">
                                                <Button
                                                    size="small"
                                                    color="error"
                                                    disabled={busy}
                                                    onClick={() => setRemovingMember(user.name)}
                                                >
                                                    Remove
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {members.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={2}>
                                                <em>This group has no members.</em>
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                        <Stack direction="row" spacing={2} alignItems="flex-start" sx={{ mt: 2 }}>
                            <Autocomplete
                                multiple
                                options={addableUsers}
                                getOptionLabel={(user) => user.name}
                                isOptionEqualToValue={(a, b) => a.name === b.name}
                                value={usersToAdd}
                                onChange={(event, value) => setUsersToAdd(value)}
                                sx={{ flexGrow: 1 }}
                                renderInput={(params) => (
                                    <TextField {...params} label="Add members" variant="outlined" />
                                )}
                            />
                            <Button
                                variant="contained"
                                disabled={busy || usersToAdd.length === 0}
                                onClick={addMembers}
                                sx={{ mt: 1 }}
                            >
                                Add
                            </Button>
                        </Stack>
                    </Box>

                    <Box>
                        <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
                            Delete group
                        </Typography>
                        <Tooltip title={isAdminGroup ? 'The admin group cannot be deleted.' : ''}>
                            <span>
                                <Button
                                    variant="outlined"
                                    color="error"
                                    disabled={busy || isAdminGroup}
                                    onClick={() => setConfirmingDelete(true)}
                                >
                                    Delete this group
                                </Button>
                            </span>
                        </Tooltip>
                    </Box>
                </Stack>
            )}

            <ConfirmDialog
                open={removingMember !== null}
                title="Remove member?"
                message={`Remove ${removingMember} from the group "${name}"? They will lose the permissions granted by this group.`}
                confirmLabel="Remove"
                busy={busy}
                onConfirm={confirmRemoveMember}
                onClose={() => setRemovingMember(null)}
            />
            <ConfirmDialog
                open={confirmingDelete}
                title="Delete group?"
                message={`Delete the group "${name}"? Its ${members.length} member${members.length === 1 ? '' : 's'} will lose the permissions it grants. The group is kept in the database history but can no longer be used.`}
                confirmLabel="Delete"
                busy={busy}
                onConfirm={confirmDelete}
                onClose={() => setConfirmingDelete(false)}
            />
        </Box>
    );
}

export default UserGroupEditPage;
