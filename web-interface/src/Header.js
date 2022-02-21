import { 
    Button, AppBar, Toolbar, Typography, Stack
} from '@mui/material';
import './Header.css';

import HeaderMenuButton from './HeaderMenuButton.js';

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

            <Stack direction="row" spacing={3}>

                <HeaderMenuButton
                    name={"Lists"}
                    links={[
                        {
                            name: 'Components', 
                            link: `/list/component`
                        },
                        {
                            name: 'Component Types', 
                            link: `/list/component-types`
                        },
                        {
                            name: 'Component Revisions', 
                            link: `/list/component-revisions`
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

            </Stack>

          </Toolbar>
        </AppBar>
    )
}

export default Header;
