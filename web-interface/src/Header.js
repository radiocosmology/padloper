import { Button, AppBar, Toolbar, Typography } from '@mui/material';
import './Header.css';
import { Link } from "react-router-dom";

function Header() {

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
              HIRAX Layout DB
            </Typography>

            <Link 
                to={`/list/component`}
                className="StyledLink"
            >
                <Button 
                    variant="outlined" 
                    color="inherit" 
                    className="StyledButton"
                >
                    Components
                </Button>
            </Link>
            
            <Link to={`/list/component-types`} className="StyledLink">
                <Button 
                    variant="outlined" 
                    color="inherit"
                    className="StyledButton"
                >
                    Component Types
                </Button>
            </Link>

            <Link to={`/list/component-revisions`} className="StyledLink">
                <Button 
                    variant="outlined" 
                    color="inherit"
                    className="StyledButton"
                >
                    Component Revisions
                </Button>
            </Link>

          </Toolbar>
        </AppBar>
    )
}

export default Header;
