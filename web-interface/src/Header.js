import { Button, AppBar, Toolbar, IconButton, Typography } from '@material-ui/core';

import { makeStyles } from '@material-ui/core/styles';

import { BrowserRouter as Router, Link } from "react-router-dom";

// styling for the React elements 
const useStyles = makeStyles((theme) => ({
    title: {
      flexGrow: 1,
    },
    button: {
        marginLeft: theme.spacing(2),
        textDecoration: "none"
    },
    buttonLink: {
        textDecoration: "none",
        color: "white",
    },
}));

function Header() {

    // load the styles
    const classes = useStyles();

    return (
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" className={classes.title}>
              HIRAX Layout DB
            </Typography>

            <Link to={`/list/component`} className={classes.buttonLink}>
                <Button variant="outlined" color="inherit" className={classes.button}>
                    Components
                </Button>
            </Link>
            
            <Link to={`/list/component-types`} className={classes.buttonLink}>
                <Button variant="outlined" color="inherit" className={classes.button}>
                    Component Types
                </Button>
            </Link>

          </Toolbar>
        </AppBar>
    )
}

export default Header;
