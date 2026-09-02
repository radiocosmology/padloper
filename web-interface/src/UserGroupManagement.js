import React, { useCallback, useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
    Alert, Autocomplete, Box, Button, Chip, CircularProgress, Dialog,
    DialogActions, DialogContent, DialogTitle, Paper, Stack, Table, TableBody,
    TableCell, TableContainer, TableHead, TableRow, TextField, Tooltip,
    Typography,
} from '@mui/material';
import { getJson, postForm } from './paths.js';
import ErrorMessage from './ErrorMessage.js';
import ConfirmDialog from './ConfirmDialog.js';
import { ADMIN_GROUP, groupEditPath, sortByName } from './userAdminUtils.js';

/**
 * Lists every user group with links to edit each one (permissions and
 * members), lets an admin delete groups, and create new ones.
 */
function UserGroupManagementPage() {
    const [groups, setGroups] = useState([]);
    const [users, setUsers] = useState([]);
    const [allPermissions, setAllPermissions] = useState([]);
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(null);
    const [notice, setNotice] = useState(null);
    const [filter, setFilter] = useState('');
    const [deleting, setDeleting] = useState(null);  // group awaiting confirm
    const [busy, setBusy] = useState(false);

    // "Create group" dialog state.
    const [createOpen, setCreateOpen] = useState(false);
    const [newName, setNewName] = useState('');
    const [newPermissions, setNewPermissions] = useState([]);
    const [createError, setCreateError] = useState(null);

    const load = useCallback(async () => {
        try {
            const [groupData, userData, permData] = await Promise.all([
                getJson('/api/get_user_group_list'),
                getJson('/api/get_user_list'),
                getJson('/api/get_all_permissions'),
            ]);
            setGroups(sortByName(groupData.result));
            setUsers(userData.result || []);
            setAllPermissions((permData.result || []).slice().sort());
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoaded(true);
        }
    }, []);

    useEffect(() => { load(); }, [load]);

    const memberCount = (groupName) => users.filter((user) =>
        (user.groups || []).some((group) => group.name === groupName)).length;

    const needle = filter.trim().toLowerCase();
    const shown = groups.filter((group) =>
        group.name.toLowerCase().includes(needle));

    const confirmDelete = async () => {
        setBusy(true);
        setError(null);
        try {
            await postForm('/api/disable_usergroup', { name: deleting });
            setNotice(`Deleted group ${deleting}.`);
            setDeleting(null);
            await load();
        } catch (err) {
            setError(err.message);
        } finally {
            setBusy(false);
        }
    };

    const openCreate = () => {
        setNewName('');
        setNewPermissions([]);
        setCreateError(null);
        setCreateOpen(true);
    };

    const createGroup = async () => {
        const groupName = newName.trim();
        if (!groupName) {
            setCreateError('A group name is required.');
            return;
        }
        setBusy(true);
        try {
            // Permission names contain ';', so the API takes a ','-separated
            // list here.
            await postForm('/api/new_usergroup', {
                name: groupName,
                permissions: newPermissions.join(','),
            });
            setNotice(`Created group ${groupName}.`);
            setCreateOpen(false);
            await load();
        } catch (err) {
            setCreateError(err.message);
        } finally {
            setBusy(false);
        }
    };

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
                    User Group Management
                </Typography>
                <Stack direction="row" spacing={1}>
                    <Button component={RouterLink} to="/manage/users" variant="outlined">
                        Users
                    </Button>
                    <Button variant="contained" onClick={openCreate}>
                        Create Group
                    </Button>
                </Stack>
            </Stack>

            <TextField
                label="Filter groups"
                variant="outlined"
                size="small"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                sx={{ mb: 2, width: 320 }}
            />

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
                    <Table size="small" aria-label="user groups">
                        <TableHead>
                            <TableRow>
                                <TableCell>Group</TableCell>
                                <TableCell>Permissions</TableCell>
                                <TableCell align="right">Members</TableCell>
                                <TableCell align="right">Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {shown.map((group) => {
                                const perms = (group.permissions || []).slice().sort();
                                const isAdmin = group.name === ADMIN_GROUP;
                                return (
                                    <TableRow key={group.name} hover>
                                        <TableCell>
                                            <RouterLink to={groupEditPath(group.name)}>
                                                {group.name}
                                            </RouterLink>
                                        </TableCell>
                                        <TableCell>
                                            {perms.length === 0 ? (
                                                <em>none</em>
                                            ) : (
                                                <Tooltip title={perms.join(', ')} arrow>
                                                    <Chip
                                                        size="small"
                                                        variant="outlined"
                                                        label={`${perms.length} permission${perms.length === 1 ? '' : 's'}`}
                                                    />
                                                </Tooltip>
                                            )}
                                        </TableCell>
                                        <TableCell align="right">
                                            {memberCount(group.name)}
                                        </TableCell>
                                        <TableCell align="right">
                                            <Button
                                                size="small"
                                                component={RouterLink}
                                                to={groupEditPath(group.name)}
                                            >
                                                Edit
                                            </Button>
                                            <Tooltip
                                                title={isAdmin ? 'The admin group cannot be deleted.' : ''}
                                            >
                                                <span>
                                                    <Button
                                                        size="small"
                                                        color="error"
                                                        disabled={busy || isAdmin}
                                                        onClick={() => setDeleting(group.name)}
                                                    >
                                                        Delete
                                                    </Button>
                                                </span>
                                            </Tooltip>
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                            {shown.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={4}>
                                        <em>
                                            {groups.length === 0
                                                ? 'No groups found.'
                                                : 'No groups match the filter.'}
                                        </em>
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}

            <ConfirmDialog
                open={deleting !== null}
                title="Delete group?"
                message={`Delete the group "${deleting}"? Its ${memberCount(deleting)} member${memberCount(deleting) === 1 ? '' : 's'} will lose the permissions it grants. The group is kept in the database history but can no longer be used.`}
                confirmLabel="Delete"
                busy={busy}
                onConfirm={confirmDelete}
                onClose={() => setDeleting(null)}
            />

            <Dialog
                open={createOpen}
                onClose={busy ? undefined : () => setCreateOpen(false)}
                fullWidth
                maxWidth="sm"
            >
                <DialogTitle>Create New User Group</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{ mt: 1 }}>
                        <TextField
                            label="Group name"
                            variant="outlined"
                            value={newName}
                            onChange={(e) => setNewName(e.target.value)}
                            autoFocus
                            fullWidth
                        />
                        <Autocomplete
                            multiple
                            options={allPermissions}
                            value={newPermissions}
                            onChange={(event, value) => setNewPermissions(value)}
                            renderInput={(params) => (
                                <TextField {...params} label="Permissions" variant="outlined" />
                            )}
                        />
                        <ErrorMessage errorMessage={createError} />
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCreateOpen(false)} disabled={busy}>
                        Cancel
                    </Button>
                    <Button variant="contained" onClick={createGroup} disabled={busy}>
                        Create Group
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

export default UserGroupManagementPage;
