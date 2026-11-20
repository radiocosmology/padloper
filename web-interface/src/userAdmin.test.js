import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import UserManagementPage from './UserManagement.js';
import UserEditPage from './UserEdit.js';
import UserGroupManagementPage from './UserGroupManagement.js';
import UserGroupEditPage from './UserGroupEdit.js';

const ADMIN = { name: 'admin', permissions: ['User;add', 'UserGroup;add'], comments: '' };
const READONLY = { name: 'readonly', permissions: [], comments: '' };
const OPS = { name: 'ops', permissions: ['Component;add', 'Component;connect'], comments: 'Operators' };
const GROUPS = [ADMIN, READONLY, OPS];
const USERS = [
    { name: 'alice', groups: [ADMIN, OPS] },
    { name: 'bob', groups: [READONLY] },
    { name: 'carol', groups: [OPS] },
];
const ALL_PERMS = ['Component;add', 'Component;connect', 'Flag;add', 'User;add', 'UserGroup;add'];

function jsonResponse(data, status = 200) {
    return Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        statusText: 'status',
        json: () => Promise.resolve(data),
    });
}

/**
 * Install a fetch mock that serves the read endpoints from the fixtures above
 * and records every POST. Returns the list of recorded posts.
 */
function mockApi({ userGroups = {}, postResult = { result: true }, postStatus = 200 } = {}) {
    const posts = [];
    global.fetch = jest.fn((url, init = {}) => {
        const u = String(url);
        if (init.method === 'POST') {
            const body = {};
            for (const [key, value] of init.body.entries()) body[key] = value;
            posts.push({ url: u, body });
            return jsonResponse(postResult, postStatus);
        }
        if (u.includes('/api/get_user_list')) return jsonResponse({ result: USERS });
        if (u.includes('/api/get_user_group_list')) return jsonResponse({ result: GROUPS });
        if (u.includes('/api/get_all_permissions')) return jsonResponse({ result: ALL_PERMS });
        if (u.includes('/api/get_user_groups')) {
            const name = decodeURIComponent(u.split('username=')[1]);
            if (!(name in userGroups)) {
                return jsonResponse({ error: `Could not find ${name} in the DB.` }, 404);
            }
            return jsonResponse({ result: userGroups[name] });
        }
        return jsonResponse({ error: `unexpected request ${u}` }, 500);
    });
    return posts;
}

function renderAt(path, routeElement) {
    return render(
        <MemoryRouter initialEntries={[path]}>
            <Routes>{routeElement}</Routes>
        </MemoryRouter>
    );
}

const dialogButton = (name) => within(screen.getByRole('dialog')).getByRole('button', { name });

describe('UserManagementPage', () => {
    test('lists users with their groups and edit links, and filters by name', async () => {
        mockApi();
        renderAt('/manage/users', <Route path="/manage/users" element={<UserManagementPage />} />);

        const alice = await screen.findByRole('link', { name: 'alice' });
        expect(alice).toHaveAttribute('href', '/manage/user/alice');
        const row = alice.closest('tr');
        expect(within(row).getByText('ops').closest('a')).toHaveAttribute('href', '/manage/group/ops');
        expect(within(row).getByText('4')).toBeInTheDocument(); // admin (2) + ops (2)
        expect(screen.getByRole('link', { name: 'bob' })).toBeInTheDocument();

        userEvent.type(screen.getByLabelText('Filter users'), 'car');
        expect(screen.queryByRole('link', { name: 'alice' })).not.toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'carol' })).toBeInTheDocument();
    });

    test('shows deactivated users on demand and reactivates after confirmation', async () => {
        const posts = mockApi();
        const disabled = { name: 'dave', active: false, uid_disabled: 'alice', groups: [] };
        const base = global.fetch;
        global.fetch = jest.fn((url, init) => {
            if (String(url).includes('include_disabled=1') && !(init && init.method === 'POST')) {
                return jsonResponse({ result: [...USERS, disabled] });
            }
            return base(url, init);
        });
        renderAt('/manage/users', <Route path="/manage/users" element={<UserManagementPage />} />);
        await screen.findByRole('link', { name: 'alice' });
        expect(screen.queryByText('dave')).not.toBeInTheDocument();

        userEvent.click(screen.getByLabelText('Show deactivated users'));
        expect(await screen.findByText('dave')).toBeInTheDocument();
        expect(screen.getByText('Deactivated by alice')).toBeInTheDocument();
        expect(screen.queryByRole('link', { name: 'dave' })).not.toBeInTheDocument();

        userEvent.click(screen.getByRole('button', { name: 'Reactivate' }));
        userEvent.click(dialogButton('Reactivate'));
        await waitFor(() => expect(posts).toHaveLength(1));
        expect(posts[0]).toEqual({ url: '/padloper/api/enable_user', body: { username: 'dave' } });
        expect(await screen.findByText(/Reactivated dave/)).toBeInTheDocument();
    });

    test('shows the API error when the list cannot be loaded', async () => {
        global.fetch = jest.fn(() => jsonResponse({ error: 'Authentication required' }, 401));
        renderAt('/manage/users', <Route path="/manage/users" element={<UserManagementPage />} />);
        expect(await screen.findByText('Authentication required')).toBeInTheDocument();
    });
});

describe('UserEditPage', () => {
    const route = <Route path="/manage/user/:name" element={<UserEditPage />} />;

    test('shows groups and effective permissions, and removes a group after confirmation', async () => {
        const posts = mockApi({ userGroups: { alice: [ADMIN, OPS] } });
        renderAt('/manage/user/alice', route);

        const opsLink = await screen.findByRole('link', { name: 'ops' });
        expect(screen.getByRole('heading', { name: 'User: alice' })).toBeInTheDocument();
        expect(screen.getByText('Component;connect')).toBeInTheDocument(); // effective permission chip

        const opsRow = opsLink.closest('tr');
        userEvent.click(within(opsRow).getByRole('button', { name: 'Remove' }));
        expect(screen.getByText('Remove from group?')).toBeInTheDocument();
        expect(posts).toHaveLength(0); // nothing sent before confirming

        userEvent.click(dialogButton('Remove'));
        await waitFor(() => expect(posts).toHaveLength(1));
        expect(posts[0]).toEqual({
            url: '/padloper/api/remove_user_group',
            body: { user: 'alice', group: 'ops' },
        });
        expect(await screen.findByText('Removed alice from ops.')).toBeInTheDocument();
    });

    test('shows the server error when a removal is refused', async () => {
        mockApi({
            userGroups: { alice: [ADMIN] },
            postResult: { error: 'Cannot remove the last member of the admin group' },
            postStatus: 400,
        });
        renderAt('/manage/user/alice', route);

        userEvent.click(await screen.findByRole('button', { name: 'Remove' }));
        userEvent.click(dialogButton('Remove'));
        expect(await screen.findByText('Cannot remove the last member of the admin group')).toBeInTheDocument();
    });

    test('deactivates a user after confirmation and returns to the list', async () => {
        const posts = mockApi({ userGroups: { alice: [OPS] } });
        render(
            <MemoryRouter initialEntries={['/manage/user/alice']}>
                <Routes>
                    {route}
                    <Route path="/manage/users" element={<div>USER LIST</div>} />
                </Routes>
            </MemoryRouter>
        );
        await screen.findByRole('link', { name: 'ops' });
        userEvent.click(screen.getByRole('button', { name: 'Deactivate this user' }));
        expect(screen.getByText('Deactivate user?')).toBeInTheDocument();
        userEvent.click(dialogButton('Deactivate'));
        await waitFor(() => expect(posts).toHaveLength(1));
        expect(posts[0]).toEqual({ url: '/padloper/api/disable_user', body: { username: 'alice' } });
        expect(await screen.findByText('USER LIST')).toBeInTheDocument();
    });

    test('reports an unknown user', async () => {
        mockApi();
        renderAt('/manage/user/nobody', route);
        expect(await screen.findByText('Could not find nobody in the DB.')).toBeInTheDocument();
    });
});

describe('UserGroupManagementPage', () => {
    const route = <Route path="/manage/users/groups" element={<UserGroupManagementPage />} />;

    test('lists groups with counts, protects admin, and deletes after confirmation', async () => {
        const posts = mockApi();
        renderAt('/manage/users/groups', route);

        const opsLink = await screen.findByRole('link', { name: 'ops' });
        expect(opsLink).toHaveAttribute('href', '/manage/group/ops');
        const opsRow = opsLink.closest('tr');
        expect(within(opsRow).getByText('2 permissions')).toBeInTheDocument();
        expect(within(opsRow).getByText('2')).toBeInTheDocument(); // alice + carol

        const adminRow = screen.getByRole('link', { name: 'admin' }).closest('tr');
        expect(within(adminRow).getByRole('button', { name: 'Delete' })).toBeDisabled();

        userEvent.click(within(opsRow).getByRole('button', { name: 'Delete' }));
        expect(screen.getByText('Delete group?')).toBeInTheDocument();
        userEvent.click(dialogButton('Delete'));
        await waitFor(() => expect(posts).toHaveLength(1));
        expect(posts[0]).toEqual({ url: '/padloper/api/disable_usergroup', body: { name: 'ops' } });
        expect(await screen.findByText('Deleted group ops.')).toBeInTheDocument();
    });

    test('creates a group, sending permissions as a comma-separated list', async () => {
        jest.setTimeout(15000);
        const posts = mockApi();
        renderAt('/manage/users/groups', route);
        await screen.findByRole('link', { name: 'ops' });

        userEvent.click(screen.getByRole('button', { name: 'Create Group' }));
        const dialog = screen.getByRole('dialog');
        userEvent.type(within(dialog).getByLabelText('Group name'), 'newgroup');
        // Pick two permissions from the autocomplete popup.
        const permissionsInput = within(dialog).getByLabelText('Permissions');
        userEvent.click(permissionsInput);
        userEvent.click(await screen.findByRole('option', { name: 'Flag;add' }));
        userEvent.click(permissionsInput);
        userEvent.click(await screen.findByRole('option', { name: 'Component;connect' }));

        userEvent.click(within(dialog).getByRole('button', { name: 'Create Group' }));
        await waitFor(() => expect(posts).toHaveLength(1));
        expect(posts[0]).toEqual({
            url: '/padloper/api/new_usergroup',
            body: { name: 'newgroup', permissions: 'Flag;add,Component;connect' },
        });
        expect(await screen.findByText('Created group newgroup.')).toBeInTheDocument();
    });

    test('refuses to create a group without a name', async () => {
        const posts = mockApi();
        renderAt('/manage/users/groups', route);
        await screen.findByRole('link', { name: 'ops' });
        userEvent.click(screen.getByRole('button', { name: 'Create Group' }));
        userEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Create Group' }));
        expect(await screen.findByText('A group name is required.')).toBeInTheDocument();
        expect(posts).toHaveLength(0);
    });
});

describe('UserGroupEditPage', () => {
    const route = <Route path="/manage/group/:name" element={<UserGroupEditPage />} />;

    test('lists permissions and members; removing a permission saves the remaining list', async () => {
        const posts = mockApi();
        renderAt('/manage/group/ops', route);

        expect(await screen.findByRole('link', { name: 'alice' })).toHaveAttribute('href', '/manage/user/alice');
        expect(screen.getByRole('heading', { name: 'Group: ops' })).toBeInTheDocument();
        expect(screen.getByText('Operators')).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'carol' })).toBeInTheDocument();
        expect(screen.queryByRole('link', { name: 'bob' })).not.toBeInTheDocument();

        const permRow = screen.getByText('Component;add').closest('tr');
        userEvent.click(within(permRow).getByRole('button', { name: 'Remove' }));
        await waitFor(() => expect(posts).toHaveLength(1));
        expect(posts[0]).toEqual({
            url: '/padloper/api/set_usergroup_permissions',
            body: { name: 'ops', permissions: 'Component;connect' },
        });
    });

    test('removing a member asks for confirmation first', async () => {
        const posts = mockApi();
        renderAt('/manage/group/ops', route);

        const carolRow = (await screen.findByRole('link', { name: 'carol' })).closest('tr');
        userEvent.click(within(carolRow).getByRole('button', { name: 'Remove' }));
        expect(screen.getByText('Remove member?')).toBeInTheDocument();
        userEvent.click(dialogButton('Cancel'));
        await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
        expect(posts).toHaveLength(0);

        userEvent.click(within(carolRow).getByRole('button', { name: 'Remove' }));
        userEvent.click(dialogButton('Remove'));
        await waitFor(() => expect(posts).toHaveLength(1));
        expect(posts[0]).toEqual({
            url: '/padloper/api/remove_user_group',
            body: { user: 'carol', group: 'ops' },
        });
    });

    test('the admin group cannot be deleted', async () => {
        mockApi();
        renderAt('/manage/group/admin', route);
        expect(await screen.findByRole('button', { name: 'Delete this group' })).toBeDisabled();
        expect(screen.getByText(/cannot be deleted/)).toBeInTheDocument();
    });

    test('reports an unknown group', async () => {
        mockApi();
        renderAt('/manage/group/nothing', route);
        expect(await screen.findByText('Group "nothing" was not found.')).toBeInTheDocument();
    });
});
