import React, { useState } from 'react';
import { 
    Button, Menu, MenuItem 
} from '@mui/material';
import { Link } from "react-router-dom";

// 

/**
 * A MUI Button that, when clicked, displays a dropdown of links that function 
 * as a menu.
 * @param {string} name - The label of the menu, displayed on the button
 * @param {Array[object]} links - an array containing the links in the menu
 * dropdown, of the format
 * {
 *      name: <string>,
 *      link: <string>
 * }
 * 
 * pretty much ripped from https://mui.com/components/menus/
 */
export default function HeaderMenuButton({name, links}) {

    // links is of the form
    // [{name: ..., link: ...}, ...]


    // See https://mui.com/components/menus/
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };

    return (
        <div>
            <Button
                id="basic-button"
                aria-controls={open ? 'basic-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={open ? 'true' : undefined}
                onClick={handleClick}
                variant="outlined" 
                color="inherit" 
            >
                {name}
            </Button>
            <Menu
                id="basic-menu"
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
                MenuListProps={{
                'aria-labelledby': 'basic-button',
                }}
            >
                {
                    links.map((el) => (
                        <Link 
                            to={el.link}
                            style={{
                                color: 'black',
                                margin: 0,
                                textDecoration: 'none',
                            }}
                        >
                            <MenuItem onClick={handleClose}>
                                    {el.name}
                            </MenuItem>
                        </Link>
                    ))
                }
            </Menu>
        </div>
      );
}