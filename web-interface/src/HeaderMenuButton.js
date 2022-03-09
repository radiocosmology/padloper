import React, { useState } from 'react';
import { 
    Button, Menu, MenuItem 
} from '@mui/material';
import { Link } from "react-router-dom";

import './Header.css';

// pretty much ripped from https://mui.com/components/menus/

export default function HeaderMenuButton({name, links}) {
    // links is of the form
    // [{name: ..., link: ...}, ...]
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
                className="StyledButton"
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
                            className="StyledLink"
                            style={{
                                color: 'black',
                                margin: 0,
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