import React, { useCallback, useEffect, useState } from 'react';
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom';
import {
    Alert, Autocomplete, Box, Button, Chip, CircularProgress, Paper, Stack,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    TextField, Typography,
} from '@mui/material';
import { getJson, postForm } from './paths.js';
import ErrorMessage from './ErrorMessage.js';
import ConfirmDialog from './ConfirmDialog.js';
import { ADMIN_GROUP, groupEditPath, sortByName } from './userAdminUtils.js';

/**
 * Edit a single user: see and change the groups they belong to, and see the
 * permissions that result. The user's name comes from the URL.
 */
function UserEditPage() {
    const { name } = useParams();
    const navigate = useNavigate();
    const [groups, setGroups] = useState([]);        // groups the user is in
    const [allGroups, setAllGroups] = useState([]);  // every group
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(null);
    const [notice, setNotice] = useState(null);
    const [toAdd, setToAdd] = useState([]);
    const [removing, setRemoving] = useState(null);  // group awaiting confirm
    const [confirmingDeactivate, setConfirmingDeactivate] = useState(false);
    const [busy, setBusy] = useState(false);

    const load = useCallback(async () => {
        try {
            const [mine, all] = await Promise.all([
                getJson(`/api/get_user_groups?username=${encodeURIComponent(name)}`),
                getJson('/api/get_user_group_list'),
            ]);
            setGroups(sortByName(mine.result));
            setAllGroups(sortByName(all.result));
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoaded(true);
        }
    }, [name]);

    useEffect(() => { load(); }, [load]);

    const memberOf = new Set(groups.map((group) => group.name));
    const joinable = allGroups.filter((group) => !memberOf.has(group.name));
    const permissions = Array.from(new Set(
        groups.flatMap((group) => group.permissions || [])
    )).sort();

    const confirmRemove = async () => {
        setBusy(true);
        setError(null);
        try {
            await postForm('/api/remove_user_group', { user: name, group: removing });
            setNotice(`Removed ${name} from ${removing}.`);
            setRemoving(null);
            await load();
        } catch (err) {
            setError(err.message);
        } finally {
            setBusy(false);
        }
    };

    const addToGroups = async () => {
        setBusy(true);
        setError(null);
        const added = [];
        const failed = [];
        for (const group of toAdd) {
            try {
                await postForm('/api/new_set_usergroup', { user: name, group: group.name });
                added.push(group.name);
            } catch (err) {
                failed.push(`${group.name} (${err.message})`);
            }
        }
        if (added.length > 0) setNotice(`Added ${name} to ${added.join(', ')}.`);
        if (failed.length > 0) setError(`Could not add to ${failed.join('; ')}`);
        setToAdd([]);
        await load();
        setBusy(false);
    };

    const confirmDeactivate = async () => {
        setBusy(true);
        setError(null);
        try {
            await postForm('/api/disable_user', { username: name });
            navigate('/manage/users');
        } catch (err) {
            setError(err.message);
            setConfirmingDeactivate(false);
            setBusy(false);
        }
    };

    return (
        <Box sx={{ width: '90%', maxWidth: 1100, mx: 'auto', my: 3 }}>
            <Button component={RouterLink} to="/manage/users" sx={{ mb: 1 }}>
                &larr; All users
            </Button>
            <Typography variant="h4" component="h1" sx={{ mb: 2 }}>
                User: {name}
            </Typography>

            <ErrorMessage errorMessage={error} />
            {notice && (
                <Alert severity="success" onClose={() => setNotice(null)} sx={{ mb: 2 }}>
                    {notice}
                </Alert>
            )}

            {!loaded ? (
                <CircularProgress />
            ) : (
                <Stack spacing={4}>
                    <Box>
                        <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
                            Groups
                        </Typography>
                        <TableContainer component={Paper}>
                            <Table size="small" aria-label="user groups">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Group</TableCell>
                                        <TableCell>Permissions</TableCell>
                                        <TableCell align="right">Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {groups.map((group) => (
                                        <TableRow key={group.name} hover>
                                            <TableCell>
                                                <RouterLink to={groupEditPath(group.name)}>
                                                    {group.name}
                                                </RouterLink>
                                            </TableCell>
                                            <TableCell>
                                                {(group.permissions || []).length === 0
                                                    ? <em>none</em>
                                                    : `${group.permissions.length} permission${group.permissions.length === 1 ? '' : 's'}`}
                                            </TableCell>
                                            <TableCell align="right">
                                                <Button
                                                    size="small"
                                                    color="error"
                                                    disabled={busy}
                                                    onClick={() => setRemoving(group.name)}
                                                >
                                                    Remove
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {groups.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={3}>
                                                <em>This user is not in any group.</em>
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Box>

                    <Box>
                        <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
                            Add to groups
                        </Typography>
                        <Stack direction="row" spacing={2} alignItems="flex-start">
                            <Autocomplete
                                multiple
                                options={joinable}
                                getOptionLabel={(group) => group.name}
                                isOptionEqualToValue={(a, b) => a.name === b.name}
                                value={toAdd}
                                onChange={(event, value) => setToAdd(value)}
                                sx={{ flexGrow: 1 }}
                                renderInput={(params) => (
                                    <TextField {...params} label="Select groups" variant="outlined" />
                                )}
                            />
                            <Button
                                variant="contained"
                                disabled={busy || toAdd.length === 0}
                                onClick={addToGroups}
                                sx={{ mt: 1 }}
                            >
                                Add
                            </Button>
                        </Stack>
                    </Box>

                    <Box>
                        <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
                            Effective permissions
                        </Typography>
                        {permissions.length === 0 ? (
                            <Typography><em>None (read-only access).</em></Typography>
                        ) : (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {permissions.map((perm) => (
                                    <Chip key={perm} label={perm} size="small" variant="outlined" />
                                ))}
                            </Box>
                        )}
                    </Box>

                    <Box>
                        <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
                            Deactivate user
                        </Typography>
                        <Typography color="text.secondary" sx={{ mb: 1 }}>
                            A deactivated user is signed out, cannot log in, and
                            loses all group memberships. They can be reactivated
                            later from the user list.
                        </Typography>
                        <Button
                            variant="outlined"
                            color="error"
                            disabled={busy}
                            onClick={() => setConfirmingDeactivate(true)}
                        >
                            Deactivate this user
                        </Button>
                    </Box>
                </Stack>
            )}

            <ConfirmDialog
                open={confirmingDeactivate}
                title="Deactivate user?"
                message={`Deactivate ${name}? They will be signed out, unable to log in, and removed from all groups until an admin reactivates them.`}
                confirmLabel="Deactivate"
                busy={busy}
                onConfirm={confirmDeactivate}
                onClose={() => setConfirmingDeactivate(false)}
            />

            <ConfirmDialog
                open={removing !== null}
                title="Remove from group?"
                message={
                    removing === ADMIN_GROUP
                        ? `Remove ${name} from the ${ADMIN_GROUP} group? They will no longer be able to manage users and groups.`
                        : `Remove ${name} from the group "${removing}"? They will lose the permissions granted by that group.`
                }
                confirmLabel="Remove"
                busy={busy}
                onConfirm={confirmRemove}
                onClose={() => setRemoving(null)}
            />
        </Box>
    );
}

export default UserEditPage;
