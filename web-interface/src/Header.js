import { 
    Button, AppBar, Toolbar, Typography, Stack
} from '@mui/material';

import HeaderMenuButton from './HeaderMenuButton.js';

/**
 * MUI Component that returns the header that is seen at the top of the web
 * interface, containing links to all pages.
 */
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
              Padloper
            </Typography>

            <Stack direction="row" spacing={3}>

                {/*Pass in the names of the links along with their paths*/}
                
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
                            name: 'Component Versions', 
                            link: `/list/component-versions`
                        },
                        {
                            name: 'Property Types', 
                            link: `/list/property-types`
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
