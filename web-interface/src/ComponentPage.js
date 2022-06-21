import React, { useState, useEffect } from 'react';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import FlagIcon from '@mui/icons-material/Flag';
import CommentIcon from '@mui/icons-material/Comment';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EventIcon from '@mui/icons-material/Event';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import createTheme from '@mui/material/styles/createTheme';
import styled from '@mui/material/styles/styled';

import Timestamp from './Timestamp.js';
import ComponentEvent from './ComponentEvent.js';
import ComponentPropertyAddPanel from './ComponentPropertyAddPanel.js';
import ComponentPropertyEndPanel from './ComponentPropertyEndPanel.js';
import ComponentConnectionAddPanel from './ComponentConnectionAddPanel.js';
import ComponentConnectionEndPanel from './ComponentConnectionEndPanel'
import ComponentSubcomponentAddPanel from './ComponentSubcomponentAddPanel.js';
import SettingsInputComponentIcon from '@mui/icons-material/SettingsInputComponent';
import ReportIcon from '@mui/icons-material/Report';



import { Link } from "react-router-dom";

import {
    useParams
} from "react-router-dom";
import { Typography } from '@mui/material';

/**
 * A styled Paper component that represents the root for the component page.
 */
const Root = styled(Paper)(({ theme }) => ({
    marginTop: theme.spacing(1),
    padding: theme.spacing(1),
    width: '1000px',
    maxWidth: '100%',
    marginLeft: 'auto',
    marginRight: 'auto',
    textAlign: 'center',
}));

/**
 * A styled Paper component that wraps around the cool big name 
 * of the component.
 */
const ComponentNameWrapper = styled((props) => (
    <Paper
        elevation={1} 
        {...props}
    />
))(({ theme }) => ({
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.common.white,
    margin: 'auto',
    marginLeft: 0,
    marginRight: theme.spacing(1),
    marginBottom: theme.spacing(1),
    width: '450px',
    height: '200px',
    fontSize: '300%',
    lineHeight: '200px',
}));

/**
 * A styling for an MUI Accordion component.
 */
const Accordion = styled((props) => (
    <MuiAccordion 
        disableGutters 
        elevation={0} 
        defaultExpanded
        {...props} 
    />
))(({ theme }) => ({
    borderBottom: `1px solid ${theme.palette.divider}`,
    
}));

/**
 * An even more styled Accordion component.
 */
const EntryAccordion = styled((props) => (
    <Accordion 
        defaultExpanded={false}
        {...props}
    />
))(({ theme }) => ({
    borderBottom: `0`,
    
}));

/**
 * A styled MUI AccordionSummary component
 */
const AccordionSummary = styled((props) => (
    <MuiAccordionSummary
        expandIcon={
            <ExpandMoreIcon 
                sx={{
                    color: "rgba(0,0,0, 0.4)",
                    padding: "4px",
                }}
                onClick={props.expandOnClick}
            />
        }
      {...props}
    />
))(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .06)',
    flexDirection: 'row-reverse',
    '& .MuiAccordionSummary-content': {
      marginLeft: theme.spacing(1),
    },
    lineHeight: '100%',
}));

const EntryAccordionSummary = styled(AccordionSummary)(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .04)',
    flexDirection: 'row',
    '& .MuiAccordionSummary-content': {
      marginLeft: theme.spacing(1),
    },
    
}));

const AccordionDetails = styled(MuiAccordionDetails)(({ theme }) => ({
    padding: theme.spacing(2),
    borderTop: '1px solid rgba(0, 0, 0, .125)',
    
}));

const EntryAccordionDetails = styled(AccordionDetails)(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .015)',
    
}));

/**
 * A MUI component representing a button for adding a component's property or connection.
 */
const AddButton = styled((props) => (
    <Button 
        variant="outlined"
        size="small"
        style={{
            margin: '-4px',
        }}
        {...props}
    >
        <AddIcon />
    </Button>
))(({ theme }) => ({
    marginTop: -2 * theme.spacing(2),
}));
/**
 * A MUI component representing a button for ending a component's property or connection.
 */
const EndButton = styled((props) => (
    <Button 
    style={{
        maxWidth: '40px', 
        maxHeight: '30px', 
        minWidth: '30px', 
        minHeight: '30px',
        marginRight:'5px'
    }}
    {...props}
        variant="outlined">
        End
    </Button>
))(({ theme }) => ({
    
}))

/*
A MUI component representing a button for editing a component's property or connection.
 */
const EditButton = styled((props) => (
    <Button 
    style={{
        maxWidth: '40px', 
        maxHeight: '30px', 
        minWidth: '30px', 
        minHeight: '30px',
    }}
    {...props}
        variant="outlined">
        <EditIcon/>
    </Button>
))(({ theme }) => ({
    
}))

/**
 * Custom MUI theme, see 
 * https://mui.com/customization/theming/#theme-configuration-variables
 */
const theme = createTheme({
    typography: {
        body2: {
            fontWeight: 800,
            fontSize: 16,
        },
    }
});

/**
 * A MUI component representing a component page.
 */
function ComponentPage() {
    // the name of the component to look at, which is fed through the URL
    let { name } = useParams();

    // the list of components in objects representation
    const [component, setComponent] = useState(undefined);

    // Stores the property type selected by the user when adding a new property.
    const [propType,setPropType] = useState('')

    // Stores the name of the other component with which the connection is being made.
    const [otherName,setOtherName] = useState('')

    // Opens the property accordion.
    const [
        open_properties_accordion, setOpenPropertiesAccordion
    ] = useState(true);

    // Opens the connections accordion.
    const [
        open_connections_accordion, setOpenConnectionsAccordion
    ] = useState(true);

    // Opens the flags accordion.
    const [open_flags_accordion, setOpenFlagsAccordion] = useState(true);

    // Opens the subcomponents accordion.
    const [open_subcomponents_accordion, setOpenSubcomponentsAccordion] = useState(true);

    // Opens/Closes a panel to add a new property.
    const [
        open_properties_add_panel, setOpenPropertiesAddPanel
    ] = useState(false) ;

    // Opens/Closes a panel to end an existing property.
    const [
        open_properties_end_panel, setOpenPropertiesEndPanel
    ] = useState(false);

    // Opens/Closes a panel to add a new connection.
    const [
        open_connections_add_panel, setOpenConnectionsAddPanel
    ] = useState(false);

    // Opens/Closes a panel to end an existing connection.
    const [
        open_connections_end_panel, setOpenConnectionsEndPanel
    ] = useState(false);

    // Opens/Closes a panel to a add new subcomponents.
    const [
        open_subcomponents_add_panel,setOpenSubcomponentsAddPanel
    ] = useState(false);

    const [activeIndexConnection,setActiveIndexConnection] = useState(null)

    const [activeIndexProperty,setActiveIndexProperty] = useState(null)


    // toggle the properties accordion.
    const toggleOpenPropertiesAccordion = () => {
        setOpenPropertiesAccordion(!open_properties_accordion);
    }

    // toggle the connections accordion.
    const toggleOpenConnectionsAccordion = () => {
        setOpenConnectionsAccordion(!open_connections_accordion);
    }

    // toggle the flags accordion.
    const toggleOpenFlagsAccordion = () => {
        setOpenFlagsAccordion(!open_flags_accordion);
    }
    // toggle the subcomponents accordion.
    const toggleOpenSubcomponentsAccordion = () => {
        setOpenSubcomponentsAccordion(!open_subcomponents_accordion);
    }

    /**
     * variable and toggle for reloading the page. 
     * When toggled, reload everything
     */
    const [reloadBool, setReloadBool] = useState(false);
    function toggleReload() {
        setReloadBool(!reloadBool);
    }

    /**
     * Set a property for the component.
     * @param {string} propertyType - the name of the property tyoe
     * @param {int} time - the time at which to add the property 
     * @param {string} uid - the ID of the user that is adding the property
     * @param {string} comments - the comments associated with the property 
     * @param {Array} values - an array connecting the values of the property. 
     */
    async function setProperty(propertyType, time, uid, comments, values) {

        // build up the string to query the API
        let input = `/api/component_set_property`;
        input += `?name=${name}`;
        input += `&propertyType=${propertyType}`;
        input += `&time=${time}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;
        input += `&valueCount=${values.length}`;
        input += `&values=`;
        for (let val of values) {
            input += `${val};`;
        }
        input = input.substring(0, input.length - 1);

        fetch(input).then(
            res => res.json()
        ).then(data => {
            setOpenPropertiesAddPanel(false);
            toggleReload();
        });
    }

    async function endProperty(time, uid, comments) {

        // build up the string to query the API
        let input = `/api/component_end_property`;
        input += `?name=${name}`;
        input += `&propertyType=${propType}`;
        input += `&time=${time}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;

        fetch(input).then(
            res => res.json()
        ).then(data => {
            setOpenPropertiesEndPanel(false);
            toggleReload();
        });
    }

    /**
     * Add a connection to another component.
     * @param {string} otherName - the name of the other component 
     * for the connection
     * @param {int} time - the time to make the connection at 
     * @param {string} uid - the ID of the user that is making the connection 
     * @param {string} comments - the comments associated with the connection 
     * @returns 
     */
    async function addConnection(otherName, time, uid, comments) {
        
        // build up the string to query the API
        let input = `/api/component_add_connection`;
        input += `?name1=${name}`;
        input += `&name2=${otherName}`;
        input += `&time=${time}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;

        return new Promise((resolve, reject) => {
            fetch(input).then(
                res => res.json()
            ).then(data => {
                if (data.result) {
                    setOpenConnectionsAddPanel(false);
                    toggleReload();
                }
                resolve(data.result);
            });
        });

    }

    async function endConnection(time, uid, comments) {
        
        // build up the string to query the API
        let input = `/api/component_end_connection`;
        input += `?name1=${name}`;
        input += `&name2=${otherName}`;
        input += `&time=${time}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;

        return new Promise((resolve, reject) => {
            fetch(input).then(
                res => res.json()
            ).then(data => {
                if (data.result) {
                    setOpenConnectionsEndPanel(false);
                    toggleReload();
                }
                resolve(data.result);
            });
        });

    }

        /**
     * Add a subcomponent.
     * @param {string} otherName - the name of the other component, which is a subcomponent.
     * @returns 
     */
    async function addSubcomponent(otherName) {
        
        // build up the string to query the API
        let input = `/api/component_add_subcomponent`;
        input += `?name1=${name}`;
        input += `&name2=${otherName}`;

        return new Promise((resolve, reject) => {
            fetch(input).then(
                res => res.json()
            ).then(data => {
                if (data.result) {
                    setOpenSubcomponentsAddPanel(false);
                    toggleReload();
                }
                resolve(data.result);
            });
        });

    }


    /**
     * When the name of the component is changed or the page is to be reloaded,
     * reload the page, query the API to query the component again,
     * and sort all the properties and connections by their start time.
     */
    useEffect(() => {
        fetch(`/api/components_name/${name}`).then(
            res => res.json()
        ).then(data => {
            data.result.properties.sort(
                (a, b) => parseFloat(a.start_time) - parseFloat(b.start_time)
            );
            data.result.connections.sort(
                (a, b) => parseFloat(a.start_time) - parseFloat(b.start_time)
            );
            setComponent(data.result);
        });
    }, [name, reloadBool]);

    /**
     * Default value for the content.
     */
    let content = (
        <>
            Loading...
        </>
    )

    /**
     * When the component is loaded, create the properties and connections
     * accordions.
     */
    if (component) {

        let properties_add_panel_content = (open_properties_add_panel) ? (
            <ComponentPropertyAddPanel 
                theme={theme} 
                onClose={() => setOpenPropertiesAddPanel(false)}
                onSet={setProperty}
            />
        ) : <></>;
        
        let properties_end_panel_content = (open_properties_end_panel) ? (
            <ComponentPropertyEndPanel 
                theme={theme} 
                onClose={() => setOpenPropertiesEndPanel(false)}
                onSet={endProperty}
            />
        ) : <></>;

        let properties_content = (
            <Stack spacing={1}>
                {component.properties.map((prop,index) => (
                    <EntryAccordion key={index}>
                        <EntryAccordionSummary >
                            <Stack spacing={1} direction="row"
                            >
                                <EventIcon fontSize="small" />
                                <Timestamp unixTime={prop.start_time} />
                                {prop.end_time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>-</div> 
                                        <Timestamp unixTime={prop.end_time} />
                                    </>
                                ) : ''}
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4)
                                    }}
                                >
                                    {prop.type.name} = { '[ ' +
                                        prop.values.map(
                                            el => el + ` ${
                                            (prop.type.units === undefined) ? 
                                                '' : prop.type.units
                                            }`
                                        ).join(", ") + ' ]'
                                    }
                                </Typography>
                            </Stack>
                        </EntryAccordionSummary>

                        <EntryAccordionDetails>
                            <Stack spacing={1}>
                                <Stack 
                                direction='row'
                                justifyContent='space-between'
                                alignItems='center'
                                >
                                <ComponentEvent
                                    name="Start"
                                    time={prop.start_time}
                                    uid={prop.start_uid}
                                    edit_time={prop.start_edit_time}
                                    comments={prop.start_comments}
                                    theme={theme} />
                                    <Stack direction='row'>
                        {prop.end_uid
                        ?
                        ""
                        :
                        <EndButton 
                            onClick={
                                () => 
                                {
                                    setOpenPropertiesEndPanel(true)
                                    setPropType(prop.type.name)
                                    setActiveIndexProperty(index)
                                }
                            }
                            />}
                        {prop.end_uid
                        ?
                        ""
                        :
                        <EditButton 
                            />}
                                    </Stack>
                            </Stack>
                               {
                                    prop.end_time <= 
                                    Number.MAX_SAFE_INTEGER ?
                                    <ComponentEvent
                                        name="End"
                                        time={prop.end_time}
                                        uid={prop.end_uid}
                                        edit_time={prop.end_edit_time}
                                        comments={prop.end_comments}
                                        theme={theme} />
                                    : ""
                                }
                            </Stack>
                        </EntryAccordionDetails>
                        {activeIndexProperty === index 
                        ?
                         properties_end_panel_content
                        :
                        ''}
                    </EntryAccordion>
                ))}
            </Stack>
        )

        let connections_add_panel_content = (open_connections_add_panel) ? (
            <ComponentConnectionAddPanel 
                theme={theme} 
                onClose={() => setOpenConnectionsAddPanel(false)}
                onSet={addConnection}
                name={name}
            />
        ) : <></>;

        let connections_end_panel_content = (open_connections_end_panel) ? (
            <ComponentConnectionEndPanel 
                theme={theme} 
                onClose={() => setOpenConnectionsEndPanel(false)}
                onSet={endConnection}
                name={name}
            />
        ) : <></>;

        let connections_content = (
            <Stack spacing={1}>
                {component.connections.map((conn,index) => (
                    <EntryAccordion key={index}>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <EventIcon fontSize="small" />
                                <Timestamp unixTime={conn.start_time} />
                                {conn.end_time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>—</div> 
                                        <Timestamp unixTime={conn.end_time} />
                                    </>
                                ) : ''}
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4)
                                    }}
                                >
                                    {
                                        <Link to={`/component/${name}`}>
                                            {name}
                                        </Link>
                                    } - {
                                        <Link to={`/component/${conn.name}`}>
                                        {conn.name}
                                    </Link>}
                                </Typography>
                                
                            </Stack>
                        
                        </EntryAccordionSummary>
                        <EntryAccordionDetails>
                            <Stack spacing={1}>
                                <Stack
                                direction = 'row'
                                justifyContent='space-between'
                                alignItems='center'>
                                <ComponentEvent
                                    name="Start"
                                    time={conn.start_time}
                                    uid={conn.start_uid}
                                    edit_time={conn.start_edit_time}
                                    comments={conn.start_comments}
                                    theme={theme} />
                                <Stack direction='row'>
                                    {
                                        conn.end_uid
                                        ?
                                        ""
                                        :
                                        <EndButton
                                        onClick={
                                            ()=>{
                                                setOpenConnectionsEndPanel(true)
                                                setOtherName(conn.name)
                                                setActiveIndexConnection(index)
                                            }
                                        }
                                        />
                                    }
                                    {conn.end_uid
                        ?
                        ""
                        :
                        <EditButton 
                            />}
                            </Stack>
                            </Stack>
                                {
                                    conn.end_time <= 
                                    Number.MAX_SAFE_INTEGER ?
                                    <ComponentEvent
                                        name="End"
                                        time={conn.end_time}
                                        uid={conn.end_uid}
                                        edit_time={conn.end_edit_time}
                                        comments={conn.end_comments}
                                        theme={theme} />
                                    : ""
                                }
                            </Stack>
                        </EntryAccordionDetails>
                        {activeIndexConnection === index 
                        ? 
                        connections_end_panel_content 
                        :
                        ''}
                    </EntryAccordion>
                ))}
            </Stack>
        )

    let subcomponent_add_panel_content = (open_subcomponents_add_panel) ? (
    <ComponentSubcomponentAddPanel 
        theme={theme} 
        onClose={() => setOpenSubcomponentsAddPanel(false)}
        onSet={addSubcomponent}
        name={name}
    />
        ) : <></>;

        let flags_content = (
            <Stack spacing={1}>
                {component.flags.map((flag,index) => (
                    <EntryAccordion key={index}>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <EventIcon fontSize="small" />
                                <Timestamp unixTime={flag.start_time} />
                                {flag.end_time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>—</div> 
                                        <Timestamp unixTime={flag.end_time} />
                                    </>
                                ) : ''}
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4)
                                    }}
                                >
                                    <FlagIcon/>
                                </Typography>
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4)
                                    }}
                                >
                                    
                                    {flag.name}
                                </Typography>
                            </Stack>
                        </EntryAccordionSummary>
                        <EntryAccordionDetails>
                            <Stack spacing={1}>
                                <Stack
                                direction = 'row'
                                justifyContent='space-between'
                                alignItems='center'>
                                    <Stack direction='row'>

                                    <ReportIcon
                                     fontSize="small"
                                     style={{
                                         marginRight:theme.spacing(1),
                                        }}
                                        /> {flag.severity.value}
                                        </Stack>
                                    <p>
                                    Flag Type: {flag.type.name}
                                    </p>
                                    
                                    <Stack
                                    direction='row'
                                    >
                                    <CommentIcon 
                    fontSize="small"
                    style={{
                        marginRight:theme.spacing(1),
                    }}
                />
                {flag.comments}
                                    </Stack>
                                    
                            </Stack>
                                
                            </Stack>
                        </EntryAccordionDetails>
                    </EntryAccordion>
                ))}
            </Stack>
        )

        let subcomponents_content = (
            <Stack spacing={1}>
                {component.subcomponents.map((subcomponent,index) => (
                    <EntryAccordion key={index}>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <SettingsInputComponentIcon/>
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4)
                                    }}
                                >
                                    
                                    {
                                        <Link to={`/component/${subcomponent.name}`}>
                                            {subcomponent.name}
                                    </Link>
    }
                                </Typography>
                            </Stack>
                        </EntryAccordionSummary>
                    </EntryAccordion>
                ))}
            </Stack>
        )

        content = (
            <ThemeProvider theme={theme}>
                <Stack direction="row" spacing={2}>
                    <ComponentNameWrapper>
                        {component.name}
                    </ComponentNameWrapper>
                    <Grid container spacing={2} justifyContent="space-around">
                        <Grid item>
                            <Stack spacing={-0.1}>
                                <Typography color={'rgb(128,128,128)'}>
                                    Component type
                                </Typography>
                                <Typography variant="h5">
                                    {component.type.name}
                                </Typography>
                            </Stack>
                        </Grid>
                        <Grid item>
                            <Stack spacing={-0.1}>
                                <Typography color={'rgb(128,128,128)'}>
                                    Component revision
                                </Typography>
                                <Typography variant="h5">
                                    {component.revision.name}
                                </Typography>
                            </Stack>
                        </Grid>
                        <Grid item>
                            <Stack spacing={-0.1}>
                                <Typography color={'rgb(128,128,128)'}>
                                    Date added
                                </Typography>
                                <Timestamp 
                                    unixTime={component.time_added} 
                                    variant="h5"
                                />
                            </Stack>
                        </Grid>
                    </Grid>
                </Stack>

                <Accordion
                    style={{
                        marginTop: theme.spacing(1)
                    }}
                    expanded={open_properties_accordion}
                >
                    <AccordionSummary
                        expandOnClick={toggleOpenPropertiesAccordion}
                    >
                        
                        <Typography style={{ flex: 1 }} align='left'>
                            Properties
                        </Typography>
                           

                        <AddButton 
                            onClick={
                                () => {setOpenPropertiesAddPanel(true)}
                            }
                        />

                    </AccordionSummary>
                    <AccordionDetails>
                        {properties_add_panel_content}
                        
                        {properties_content}
                        
                    </AccordionDetails>
                </Accordion>

                <Accordion
                    style={{
                        marginTop: theme.spacing(1)
                    }}
                    expanded={open_connections_accordion}
                >
                    <AccordionSummary
                        expandOnClick={toggleOpenConnectionsAccordion}
                    >
                        <Typography style={{ flex: 1 }} align='left'>
                            Connections
                        </Typography>

                        <AddButton 
                            onClick={
                                () => {setOpenConnectionsAddPanel(true)}
                            }
                        />
                    
                    </AccordionSummary>
                    
                    <AccordionDetails>
                        {connections_add_panel_content}

                        {connections_content}

                    </AccordionDetails>
                </Accordion>


                    <Accordion
                    style={{
                        marginTop: theme.spacing(1)
                    }}
                    expanded={open_subcomponents_accordion}
                >
                    <AccordionSummary
                        expandOnClick={toggleOpenSubcomponentsAccordion}
                    >
                           <Typography style={{ flex: 1 }} align='left'>
                            Subcomponents
                        </Typography>
                        <AddButton 
                            onClick={
                                () => {setOpenSubcomponentsAddPanel(true)}
                            }
                        />
                    </AccordionSummary>
                        <AccordionDetails>
                        {subcomponent_add_panel_content}

                        {subcomponents_content}

                    </AccordionDetails>       
                </Accordion>

                    <Accordion
                    style={{
                        marginTop: theme.spacing(1)
                    }}
                    expanded={open_flags_accordion}
                >
                    <AccordionSummary
                        expandOnClick={toggleOpenFlagsAccordion}
                    >
                           <Typography style={{ flex: 1 }} align='left'>
                            Flags
                        </Typography>
                    </AccordionSummary>
                        <AccordionDetails>
                        {flags_content}

                    </AccordionDetails>       
                </Accordion>
            </ThemeProvider>
        )
    }

    // return all the good stuff
    return (
        <Root>
            {content}
        </Root>
    )
}

export default ComponentPage;