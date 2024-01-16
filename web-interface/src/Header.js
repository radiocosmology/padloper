import { 
    Button, AppBar, Toolbar, Typography, Stack
} from '@mui/material';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import GithubIcon from "mdi-react/GithubIcon";
import { useState, useEffect, useContext } from 'react';
import { OAuthContext } from './contexts/OAuthContext';

import HeaderMenuButton from './HeaderMenuButton.js';

/**
 * MUI Component that returns the header that is seen at the top of the web
 * interface, containing links to all pages.
 */
function Header() {
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);
    const [userData, setUserData] = useState({});
    const { accessToken, setAccessToken } = useContext(OAuthContext); 

    useEffect(() => {
        // TODO: remove local storage
        // if (localStorage.getItem("accessToken")) {
        if (accessToken) {
            console.log(accessToken)
            getUserData();
        }
    }, [accessToken])

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
      };
      const handleClose = () => {
        setAnchorEl(null);
      };

    async function getUserData() {
    await fetch("http://localhost:4000/getUserData", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + accessToken
        }
        }).then((response) => {
            return response.json();
        }).then((data) => {
            console.log(data);
            setUserData(data);
        });
    }

    // TODO: change to network context
    // if (localStorage.getItem("accessToken") === null) {
    if (!accessToken) {
        return <></>;
    }
    return (
        <AppBar 
            position="static"
            style={{
                marginBottom: '16px',
            }}>
          <Toolbar>
            <Typography 
            variant="h6"
            style={{
                flexGrow: 1,
            }}>
              Padloper
            </Typography>

            <Stack direction="row" spacing={3} alignItems={'center'}>

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
                        // onClick={() => { localStorage.removeItem("accessToken"); window.location.reload(false); }
                        onClick={() => { setAccessToken(''); }
                    }>
                        Sign out
                    </MenuItem>
                </Menu>

            </Stack>

          </Toolbar>
        </AppBar>
    )
}

export default Header;
