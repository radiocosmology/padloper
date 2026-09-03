import {
    Button, AppBar, Toolbar, Typography, Stack, Drawer, List, ListItemButton, ListItemText, useMediaQuery, useTheme, Alert
} from '@mui/material';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import MenuIcon from '@mui/icons-material/Menu';
import GithubIcon from "mdi-react/GithubIcon";
import axios from 'axios'
import { useState, useEffect, useContext } from 'react';
import { OAuthContext } from './contexts/OAuthContext';
import { withBase, authHeaders, requireOkJson } from './paths.js';

import HeaderMenuButton from './HeaderMenuButton.js';
import { useNavigate, Link } from 'react-router-dom';

/**
 * MUI Component that returns the header that is seen at the top of the web
 * interface, containing links to all pages.
 */
function Header() {
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);
    const [userData, setUserData] = useState({});
    const { accessToken, setAccessToken } = useContext(OAuthContext);
    const navigate = useNavigate();
    let login_ok = true;
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const [mobileOpen, setMobileOpen] = useState(false);

    useEffect(() => {
        // TODO: remove local storage
        if (localStorage.getItem("accessToken"))
            getUserData();
    }, []
    // [accessToken]
    )

    // login to backend
    useEffect(() => {
        if (userData.login) {
            axios.post(withBase("/api/login"), {
                username: userData.login,
                accessToken: localStorage.getItem("accessToken")
            })
            .then(res => {
                console.log(res.data)
            })
            .catch(err => {
                const msg = err?.response?.data?.error || 'Login failed';
                console.error(msg);
            })
        }
    }, [userData])

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
      };
      const handleClose = () => {
        setAnchorEl(null);
      };

    // Detect read-only (no permissions) to show a banner.
    const [isReadOnly, setIsReadOnly] = useState(false);
    useEffect(() => {
        async function checkPerms(login) {
            try {
                const res = await fetch(withBase(`/api/get_permissions?username=${encodeURIComponent(login)}`));
                if (!res.ok) return setIsReadOnly(false);
                const data = await res.json();
                const perms = data && data.result ? data.result : [];
                setIsReadOnly(!(perms && perms.length > 0));
            } catch (e) {
                setIsReadOnly(false);
            }
        }
        if (userData && userData.login) {
            checkPerms(userData.login);
        }
    }, [userData]);

    // TODO: export function to use elsewhere
    async function getUserData() {
      await fetch(withBase(`/oauth/getUserData`), {
        method: "GET",
        headers: { ...authHeaders() }
      })
      .then(requireOkJson)
      .then((data) => {
        setUserData(data);
      })
      .catch((err) => {
        console.error('Failed to load user data:', err);
        setUserData({});
      });
    }

    // TODO: change to network context
    if (localStorage.getItem("accessToken") === null) {
        return <></>;
    }
    return (
        <>
        <AppBar
            position="static"
            style={{
                marginBottom: '16px',
            }}
            sx={{ width: '100%' }}>
          <Toolbar sx={{ flexWrap: 'wrap' }}>
            <Typography
            variant="h6"
            style={{
                flexGrow: 1,
            }}>
              Padloper
            </Typography>

            {/* Mobile hamburger menu button */}
            <IconButton
                color="inherit"
                edge="start"
                onClick={() => setMobileOpen(true)}
                sx={{ display: { xs: 'flex', md: 'none' }, mr: 1 }}
                aria-label="open navigation menu"
            >
                <MenuIcon />
            </IconButton>

            {/* Desktop navigation */}
            <Stack direction="row" spacing={3} alignItems={'center'}
                   sx={{ flexWrap: 'wrap', rowGap: 1, columnGap: 2, display: { xs: 'none', md: 'flex' } }}>

                {/*Pass in the names of the links along with their paths*/}

                <HeaderMenuButton
                    name={"Components"}
                    links={[
                        {
                            name: 'Component List',
                            link: `/list/component`
                        },
                        {
                            name: 'Component Types',
                            link: `/list/component-types`
                        },
                        {
                            name: 'Component Versions',
                            link: `/list/component-versions`
                        },
                        {
                            name: 'Component Sequences',
                            link: `/list/component-sequences`,
                        },
                    ]}
                />

                <HeaderMenuButton
                    name={"Properties"}
                    links={[
                        {
                            name: 'Property Types',
                            link: `/list/property-types`
                        }
                    ]}
                />

                <HeaderMenuButton
                    name={"Flags"}
                    links={[
                        {
                            name: 'Flag Types',
                            link: `/list/flag-types`
                        },
                        {
                            name: 'Flags',
                            link: `/list/flag`
                        },
                    ]}
                />

                <HeaderMenuButton
                    name={"Visualizations"}
                    links={[
                        {
                            name: 'Component Connections',
                            link: `/component-connections`
                        },
                        {
                            name: 'System Diagram',
                            link: `/system-diagram`
                        },
                        {
                            name: 'Legacy Visualizer',
                            link: `/legacy-visualizer`
                        },
                    ]}
                />

                {/* <Button
                    component={Link}
                    to="/barcode"
                    color="inherit"
                >
                    Barcode
                </Button> */}

                <Button
                    component={Link}
                    to="/bulk-input"
                    color="inherit"
                >
                    Bulk Input
                </Button>

                <HeaderMenuButton
                    name={"Manage Users"}
                    links={[
                        {
                            name: 'User Management',
                            link: `/manage/users`
                        },
                        {
                            name: 'User Group Management',
                            link: `/manage/users/groups`
                        },
                        {
                            name: 'Add Users',
                            link: `/users`
                        }
                    ]}
                />

                {/* <a onClick={() => console.log('clicked!')}> */}
                {/* </a> */}

                <IconButton
                onClick={handleClick}
                size="small"
                sx={{ ml: 2 }}
                // aria-controls={open ? 'account-menu' : undefined}
                // aria-haspopup="true"
                // aria-expanded={open ? 'true' : undefined}
                >
                    <Avatar alt="user" src={userData ? userData.avatar_url : ''} />
                </IconButton>
                <Menu
                    anchorEl={anchorEl}
                    id="account-menu"
                    open={open}
                    onClose={handleClose}
                    onClick={handleClose}
                >
                    <MenuItem>
                    {/*
                    avatar: https://mui.com/material-ui/react-avatar/
                    menu: https://mui.com/material-ui/react-menu/
                    */}
                        <a href={userData? userData.html_url : ''} style={{ display: 'flex', alignItems: 'center', 'textDecoration': 'none', 'color': 'black'}}>
                            <GithubIcon style={{ marginRight: '5px' }} /> {userData ? userData.login : ''}
                        </a>
                    </MenuItem>
                    <MenuItem
                        // remove local storage
                        onClick={() => {
                            localStorage.removeItem("accessToken");
                            axios.post(withBase("/api/logout"))
                            .then(res => {
                                console.log(res.data)
                            })
                            .catch(err => {
                                console.error('Error:', err);
                            })
                            window.location.reload(false);
                        }
                        // onClick={() => { setAccessToken(''); }
                    }>
                        Sign out
                    </MenuItem>
                </Menu>

            </Stack>

            {/* Mobile navigation drawer */}
            <Drawer
                anchor="left"
                open={mobileOpen}
                onClose={() => setMobileOpen(false)}
            >
                <List sx={{ width: 280 }}>
                    <ListItemText
                        primary="Components"
                        sx={{ px: 2, pt: 2, pb: 0 }}
                        primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                    <ListItemButton component={Link} to={'/list/component'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="Component List" />
                    </ListItemButton>
                    <ListItemButton component={Link} to={'/list/component-types'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="Component Types" />
                    </ListItemButton>
                    <ListItemButton component={Link} to={'/list/component-versions'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="Component Versions" />
                    </ListItemButton>

                    <ListItemText
                        primary="Properties"
                        sx={{ px: 2, pt: 2, pb: 0 }}
                        primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                    <ListItemButton component={Link} to={'/list/property-types'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="Property Types" />
                    </ListItemButton>

                    <ListItemText
                        primary="Flags"
                        sx={{ px: 2, pt: 2, pb: 0 }}
                        primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                    <ListItemButton component={Link} to={'/list/flag-types'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="Flag Types" />
                    </ListItemButton>
                    <ListItemButton component={Link} to={'/list/flag'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="Flags" />
                    </ListItemButton>

                    <ListItemText
                        primary="Visualizations"
                        sx={{ px: 2, pt: 2, pb: 0 }}
                        primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                    <ListItemButton component={Link} to={'/component-connections'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="Component Connections" />
                    </ListItemButton>
                    <ListItemButton component={Link} to={'/system-diagram'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="System Diagram" />
                    </ListItemButton>

                    <ListItemText
                        primary="Manage Users"
                        sx={{ px: 2, pt: 2, pb: 0 }}
                        primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                    <ListItemButton component={Link} to={'/manage/users'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="User Management" />
                    </ListItemButton>
                    <ListItemButton component={Link} to={'/manage/users/groups'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="User Group Management" />
                    </ListItemButton>
                    <ListItemButton component={Link} to={'/users'} onClick={() => setMobileOpen(false)}>
                        <ListItemText primary="Add Users" />
                    </ListItemButton>

                    {userData && userData.login && (
                        <>
                            <ListItemText
                                primary="Account"
                                sx={{ px: 2, pt: 2, pb: 0 }}
                                primaryTypographyProps={{ fontWeight: 'bold' }}
                            />
                            <ListItemButton component={'a'} href={userData.html_url} target="_blank" rel="noopener noreferrer" onClick={() => setMobileOpen(false)}>
                                <ListItemText primary="GitHub Profile" />
                            </ListItemButton>
                            <ListItemButton onClick={() => {
                                localStorage.removeItem("accessToken");
                                axios.post(withBase("/api/logout"))
                                    .then(res => { console.log(res.data); })
                                    .catch(err => { console.error('Error:', err); })
                                    .finally(() => { window.location.reload(false); });
                            }}>
                                <ListItemText primary="Sign out" />
                            </ListItemButton>
                        </>
                    )}
                </List>
            </Drawer>

          </Toolbar>
        </AppBar>
        {isReadOnly && (
            <Alert severity="info" sx={{ borderRadius: 0 }}>
                You are in read-only mode and have no write permissions.
            </Alert>
        )}
        </>
    )
}

export default Header;
