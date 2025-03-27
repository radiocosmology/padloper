import React, { useState, useEffect } from 'react';

import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import FlagIcon from '@mui/icons-material/Flag';
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
import ComponentPropertyReplacePanel from './ComponentPropertyReplacePanel'
import ComponentConnectionAddPanel from './ComponentConnectionAddPanel.js';
import ComponentConnectionEndPanel from './ComponentConnectionEndPanel'
import ComponentSubcomponentAddPanel from './ComponentSubcomponentAddPanel.js';
import ComponentConnectionReplacePanel from './ComponentConnectionReplacePanel.js';
import ComponentPropertyDisableButton from './ComponentPropertyDisableButton'
import ComponentConnectionDisableButton from './ComponentConnectionDisableButton'
import ComponentSubcomponentDisableButton from './ComponentSubcomponentDisableButton'
import SettingsInputComponentIcon from '@mui/icons-material/SettingsInputComponent';
import ReportIcon from '@mui/icons-material/Report';
import EastIcon from '@mui/icons-material/East';
import KeyboardBackspaceIcon from '@mui/icons-material/KeyboardBackspace';
import axios from 'axios'

import { Link } from "react-router-dom";

import {
    useParams
} from "react-router-dom";
import { Typography } from '@mui/material';
import Authenticator from './components/Authenticator.js';

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
                onClick={props.expandonClick}
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

/**
 * A styled MUI AccordionSummary component
 */
const AccordionSummarySubcomponents = styled((props) => (
    <MuiAccordionSummary
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

const EntryAccordionSummarySubcomponent = styled(AccordionSummarySubcomponents)(({ theme }) => ({
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
A MUI component representing a button for replacing a component's property or connection.
 */
const ReplaceButton = styled((props) => (
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

    // Stores the name of the other component with which the connection exists.
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

    // Opens/Closes a panel to edit an existing property.
    const [
        open_properties_replace_panel, setOpenPropertiesReplacePanel
    ] = useState(false);

    // Opens/Closes a panel to add a new connection.
    const [
        open_connections_add_panel, setOpenConnectionsAddPanel
    ] = useState(false);

    // Opens/Closes a panel to replace a new connection.
    const [
        open_connections_replace_panel, setOpenConnectionsReplacePanel
    ] = useState(false);

    // Opens/Closes a panel to end an existing connection.
    const [
        open_connections_end_panel, setOpenConnectionsEndPanel
    ] = useState(false);

    // Opens/Closes a panel to a add new subcomponents.
    const [
        open_subcomponents_add_panel,setOpenSubcomponentsAddPanel
    ] = useState(false);

    // To keep track of which connection from the list of connections is the
    // user ending and open the relevant panel.
    const [activeIndexConnectionEnd,setActiveIndexConnectionEnd] = useState(null)

    // To keep track of which property from the list of properties is the
    // user ending and open the relevant panel.
    const [activeIndexPropertyEnd,setActiveIndexPropertyEnd] = useState(null)

    // To keep track of which property from the list of properties is the
    // user replacing and open the relevant panel.
    const [activeindexpropertyReplace,setactiveindexpropertyReplace] = useState(null)

    // To keep track of which connection from the list of connections is the
    // user replacing and open the relevant panel.
    const [activeIndexConnectionReplace,setActiveIndexConnectionReplace] = useState(null)


    // toggle the properties accordion.
    const toggleOpenPropertiesAccordion = () => {
        setOpenPropertiesAccordion(!open_properties_accordion);
    }

    // toggle the connections accordion.
    const toggleOpenConnectionsAccordion = () => {
        setOpenConnectionsAccordion(!open_connections_accordion);
    }

    // toggle the components_names accordion.
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

    /*Contains the message when there is an error while adding a new subcomponent connection */
    const [errorSubcomponentMessage,setErrorSubcomponentMessage] = useState(null)

    /*Contains the message when there is an error while adding a new property */
    const [errorPropertyMessage,setErrorPropertyMessage] = useState(null)

    /*Contains the message when there is an error while ending a property */
    const [errorEndPropertyMessage, seterrorEndPropertyMessage] = useState(null)

    /*Contains the message when there is an error while replacing a property */
    const [errorReplacePropertyMessage, setErrorReplacePropertyMessage] = useState(null)

    /*Contains the message when there is an error while adding a new connection */
    const [errorConnectionMessage,setErrorConnectionMessage] = useState(null)

    /*Contains the message when there is an error while ending a connection */
    const [errorEndConnectionMessage, setErrorEndConnectionMessage] = useState(null)

    /*Contains the message when there is an error while replacing a connection */
    const [errorReplaceConnectionMessage, setErrorReplaceConnectionMessage] = useState(null);

    const [userData, setUserData] = useState({});

    const [uid, setUid] = useState('');

    // load user data when the page loads
    useEffect(() => {
        getUserData();
    }, [])


    // set user id
    useEffect(() => {
        if (userData) {
            setUid(userData.login);
        }
    }, [userData])

    /**
     * Get the user data via GitHub
     */
    async function getUserData() {
        await fetch(`${process.env.OAUTH_URL || "http://localhost"}:4000/getUserData`, {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem('accessToken')
            }
            }).then((response) => {
                return response.json();
            }).then((data) => {
                setUserData(data);
            });
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

        axios.post(input).then(
            (response) => {
                if (response.data.result){
                    setOpenPropertiesAddPanel(false);
                    setErrorPropertyMessage(null);
                    toggleReload();
                } else {
                    setErrorPropertyMessage(JSON.parse(response.data.error));
                }
            }
        )
    }

    /**
     * End a property for the component.
     * @param {int} time - the time at which to end the property 
     * @param {string} uid - the ID of the user that is ending the property
     * @param {string} comments - the comments associated with ending the property 
     */
    async function endProperty(time, uid, comments) {

        // build up the string to query the API
        let input = `/api/component_end_property`;
        input += `?name=${name}`;
        input += `&propertyType=${propType}`;
        input += `&time=${time}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;

        fetch(input).then(
            (res) => res.json()
        ).then((data) => {
            if (data.result) {
                setOpenPropertiesEndPanel(false);
                seterrorEndPropertyMessage(null);
                toggleReload();
            }
            else {
                console.log(data.error);
                seterrorEndPropertyMessage(JSON.parse(data.error));
            }
        });
    }

    /**
     * Replace a property for the component.
     * @param {string} propertyType - the property type to replace 
     * @param {int} time - the time at which to add the property 
     * @param {string} uid - the ID of the user that is adding the property
     * @param {string} comments - the comments associated with the property 
     * @param {Array} values - an array connecting the values of the property. 
     */
    async function replaceProperty(propertyType,time, uid, comments, values) {

        // build up the string to query the API
        let input = `/api/component_replace_property`;
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
            if (data.result) {
                setOpenPropertiesReplacePanel(false);
                toggleReload();
            }
            else {
                setErrorReplacePropertyMessage(JSON.parse(data.error));
            }
        });
    }


    /**
     * Add a connection to another component.
     * @param {string} otherName - the name of the other component 
     * for the connection
     * @param {int} time - the time to make the connection at 
     * @param {string} uid - the ID of the user that is making the connection 
     * @param {string} comments - the comments associated with the connection 
     */
    async function addConnection(otherName, time, uid, comments) {
        
        // build up the string to query the API
        let input = `/api/component_add_connection`;
        input += `?name1=${name}`;
        input += `&name2=${otherName}`;
        input += `&time=${time}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;

        axios.post(input).then(
                (response) => {
                    if(response.data.result) {
                    setOpenConnectionsAddPanel(false);
                    setErrorConnectionMessage(null)
                    toggleReload();
                } else {
                    setErrorConnectionMessage(JSON.parse(response.data.error))
                }
            });
    }

    /**
     * End the connection to another component.
     * @param {int} time - the time to end the connection at 
     * @param {string} uid - the ID of the user that is ending the connection 
     * @param {string} comments - the comments associated with ending the connection 
     */
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
                else {
                    console.log(data.error);
                    setErrorEndConnectionMessage(JSON.parse(data.error));
                }
                resolve(data.result);
            });
        });

    }

    /**
     * Replace the connection to another component.
     * @param {int} startTime - the time to make the connection at 
     * @param {int} endTime - the time to end the connection at
     * @param {string} uid - the ID of the user that is making the connection 
     * @param {string} comments - the comments associated with making the connection 
     * @param {int} oldStartTime - the start time of the old connection that will be replaced
     * @param {bool} hasEnd - whether the connection has already ended, i.e., whether the 
     *                      "endTime" value is actually valid
     */
    async function replaceConnection(startTime, endTime, uid, comments, oldStartTime, hasEnd) {
        
        // build up the string to query the API
        let input = `/api/component_add_connection`;
        input += `?name1=${name}`;
        input += `&name2=${otherName}`;
        input += `&time=${startTime}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;
        input += `&replace_time=${oldStartTime}`;

        if (hasEnd) {       // need to include ending time of new connection
            input += `&end_time=${endTime}`;
        }

        console.log("hasend", hasEnd);
        console.log("endTime", endTime);

        return new Promise((resolve, reject) => {
            fetch(input, {method: 'POST'}).then(
                res => res.json()
            ).then(data => {
                if (data.result) {
                    setOpenConnectionsReplacePanel(false);
                    toggleReload();
                }
                else {
                    setErrorReplaceConnectionMessage(JSON.parse(data.error));
                }
                resolve(data.result);
            });
        });
    }

    /**
     * Add a subcomponent.
     * @param {string} otherName - the name of the other component, which is a subcomponent.
     */
    async function addSubcomponent(otherName) {
        
        // build up the string to query the API
        let input = `/api/component_add_subcomponent`;
        input += `?name1=${name}`;
        input += `&name2=${otherName}`;

        axios.post(input).then(
                (response) => {
                if (response.data.result) {
                    setOpenSubcomponentsAddPanel(false);
                    setErrorSubcomponentMessage(null)
                    toggleReload();
                } else {
                    setErrorSubcomponentMessage(JSON.parse(response.data.error));
                }
            })
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
            console.log("RESULT", data.result)
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
                onClose={() => {setOpenPropertiesAddPanel(false);
                                setErrorPropertyMessage(null)}}
                onSet={setProperty}
                errorPropertyMessage={errorPropertyMessage}
            />
        ) : <></>;
        
        let properties_end_panel_content = (open_properties_end_panel) ? (
            <ComponentPropertyEndPanel 
                theme={theme} 
                onClose={() => setOpenPropertiesEndPanel(false)}
                onSet={endProperty}
                errorMessage={errorEndPropertyMessage}
            />
        ) : <></>;

        let properties_edit_panel_content = (open_properties_replace_panel) ? (
            <ComponentPropertyReplacePanel 
                theme={theme} 
                onClose={() => setOpenPropertiesReplacePanel(false)}
                onSet={replaceProperty}
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
                                <Timestamp unixTime={prop.start.time} />
                                {prop.end.time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>-</div> 
                                        <Timestamp unixTime={prop.end.time} />
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
                                    time={prop.start.time}
                                    uid={prop.start.uid}
                                    edit_time={prop.start.edit_time}
                                    comments={prop.start.comments}
                                    theme={theme} />
                                    <Stack direction='row'>
                        {
                        prop.end.uid
                        ?
                        ""
                        :
                        <>
                        <EndButton 
                            onClick={
                                () => 
                                {
                                    setOpenPropertiesEndPanel(true)
                                    setPropType(prop.type.name)
                                    setActiveIndexPropertyEnd(index)
                                }
                            }
                            />
                        <ReplaceButton 
                            onClick={
                                () => 
                                {
                                    setOpenPropertiesReplacePanel(true)
                                    setactiveindexpropertyReplace(index)
                                }
                            }
                            />
                            <ComponentPropertyDisableButton
                            name={name}
                            propertyType={prop.type.name}
                            propertyValue = {prop.values}
                            propertyUnit = {prop.type.units}
                            toggleReload={toggleReload}
                            />
                            </>
    }
                                    </Stack>
                            </Stack>
                               {
                                    prop.end.time <= 
                                    Number.MAX_SAFE_INTEGER ?
                                    <ComponentEvent
                                        name="End"
                                        time={prop.end.time}
                                        uid={prop.end.uid}
                                        edit_time={prop.end.edit_time}
                                        comments={prop.end.comments}
                                        theme={theme} />
                                    : ""
                                }
                            </Stack>
                        </EntryAccordionDetails>
                        {activeIndexPropertyEnd === index 
                        ?
                         properties_end_panel_content
                        :
                        ''}
                        {activeindexpropertyReplace === index 
                        ?

                        (open_properties_replace_panel) ? (
                            <ComponentPropertyReplacePanel 
                                theme={theme} 
                                onClose={() => {
                                    setErrorReplacePropertyMessage(null); 
                                    setOpenPropertiesReplacePanel(false)
                                }}
                                onSet={replaceProperty}
                                selected={prop.type}
                                oldTextFieldValues={prop.values}
                                oldComments={prop.start. comments}
                                errorReplacePropertyMessage={errorReplacePropertyMessage}
                            />
                        ) : <></>
                        :
                        ''}
                    </EntryAccordion>
                ))}
            </Stack>
        )

        let connections_add_panel_content = (open_connections_add_panel) ? (
            <ComponentConnectionAddPanel 
                theme={theme} 
                onClose={() => {setOpenConnectionsAddPanel(false); setErrorConnectionMessage(null) }}
                onSet={addConnection}
                name={name}
                errorConnectionMessage = {errorConnectionMessage}
            />
        ) : <></>;

        let connections_end_panel_content = (open_connections_end_panel) ? (
            <ComponentConnectionEndPanel 
                theme={theme} 
                onClose={() => {
                    setOpenConnectionsEndPanel(false);
                    setErrorEndConnectionMessage(null);
                }}
                onSet={endConnection}
                name={name}
                uid={uid}
                errorMessage={errorEndConnectionMessage}
            />
        ) : <></>;

        // let connections_replace_panel_content = (open_connections_replace_panel) ? (
        //     <ComponentConnectionReplacePanel 
        //         theme={theme} 
        //         onClose={() => setOpenConnectionsReplacePanel(false)}
        //         onSet={replaceConnection}
        //         uid={uid}
        //         time={}
        //     />
        // ) : <></>;

        let connections_content = (
            <Stack spacing={1}>
                {component.connections.map((conn,index) => (
                    <EntryAccordion key={index}>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <EventIcon fontSize="small" />
                                <Timestamp unixTime={conn.start.time} />
                                {conn.end.time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>—</div> 
                                        <Timestamp unixTime={conn.end.time} />
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
                                    time={conn.start.time}
                                    uid={conn.start.uid}
                                    edit_time={conn.start.edit_time}
                                    comments={conn.start.comments}
                                    theme={theme} />
                                <Stack direction='row'>
                                    {
                                        conn.end.uid
                                        ?
                                        ""
                                        :
                                        <EndButton
                                        onClick={
                                            ()=>{
                                                setOpenConnectionsEndPanel(true)
                                                setOtherName(conn.name)
                                                setActiveIndexConnectionEnd(index)
                                            }
                                        }
                                        />
                                    }
                                    
                        <>
                        <ReplaceButton 
                        onClick={
                                () => 
                                {
                                    setOtherName(conn.name)
                                    setOpenConnectionsReplacePanel(true)
                                    setActiveIndexConnectionReplace(index)
                                    setErrorReplaceConnectionMessage(null)
                                }
                            }
                        />
                        <ComponentConnectionDisableButton
                        name={name}
                        otherComponentName={conn.name}
                        time={conn.start.time}
                        toggleReload={toggleReload}
                        />
                        
                            </>
                            
                            </Stack>
                            </Stack>
                                {
                                    conn.end.time <= 
                                    Number.MAX_SAFE_INTEGER ?
                                    <ComponentEvent
                                        name="End"
                                        time={conn.end.time}
                                        uid={conn.end.uid}
                                        edit_time={conn.end.edit_time}
                                        comments={conn.end.comments}
                                        theme={theme} />
                                    : ""
                                }
                            </Stack>
                        </EntryAccordionDetails>
                        {activeIndexConnectionEnd === index 
                        ? 
                        connections_end_panel_content 
                        :
                        ''}
                         {activeIndexConnectionReplace === index 
                        ?
                        //  connections_replace_panel_content
                        (open_connections_replace_panel) ? (
                            <ComponentConnectionReplacePanel 
                                theme={theme} 
                                onClose={() => setOpenConnectionsReplacePanel(false)}
                                onSet={replaceConnection}
                                uid={uid}
                                conn={conn}
                                errorMessage={errorReplaceConnectionMessage}
                            />
                        ) : <></>
                        :
                        ''}
                    </EntryAccordion>
                ))}
            </Stack>
        )

    let subcomponent_add_panel_content = (open_subcomponents_add_panel) ? (
    <ComponentSubcomponentAddPanel 
        theme={theme} 
        onClose={() => {setOpenSubcomponentsAddPanel(false); setErrorSubcomponentMessage(null)}}
        onSet={addSubcomponent}
        name={name}
        errorSubcomponentMessage = {errorSubcomponentMessage}
    />
        ) : <></>;

    let flags_content = (
            <Stack spacing={1}>
                {component.flags.map((flag,index) => (
                    <EntryAccordion key={index}>
                        <EntryAccordionSummary >
                            <Stack spacing={1} direction="row"
                            >
                                <EventIcon fontSize="small" />
                                <Timestamp unixTime={flag.start.time} />
                                {flag.end.time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>-</div> 
                                        <Timestamp unixTime={flag.end.time} />
                                    </>
                                ) : ''}
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4),
                                        display:'flex'
                                    }}
                                >
                                    <FlagIcon
                                    fontSize='small'/>
                                    {flag.name}
                                </Typography>
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4),
                                        display:'flex'
                                    }}
                                >
                                    Flag Type: {flag.type.name}
                                </Typography>
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4),
                                        display:'flex'
                                    }}
                                >
                                   <ReportIcon fontSize='small'/> {flag.severity.name}
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
                                    time={flag.start.time}
                                    uid={flag.start.uid}
                                    edit_time={flag.start.edit_time}
                                    comments={flag.notes}
                                    theme={theme} />
                                    <Stack direction='row'>
                            </Stack>
                            </Stack>
                               {
                                    flag.end_time <= 
                                    Number.MAX_SAFE_INTEGER ?
                                    <ComponentEvent
                                        name="End"
                                        time={flag.end_time}
                                        uid={flag.end_uid}
                                        edit_time={flag.end_edit_time}
                                        comments={flag.end_comments}
                                        theme={theme} />
                                    : ""
                                }
                            </Stack>
                        </EntryAccordionDetails>
                    </EntryAccordion>
                ))}
            </Stack>
        )


        let subcomponents_content = (
            <Stack spacing={1}>
                {component.subcomps.map((subcomponent,index) => (
                    <EntryAccordion key={index}>
                        <EntryAccordionSummarySubcomponent>
                            <Stack 
                            spacing={2} 
                            direction="row"
                            >
                                <SettingsInputComponentIcon/>
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4),
                                        display:'flex',
                                        alignItems:'center'                              
                                    }}
                                >
                                    <Stack>
                                    {
                                        <Link to={`/component/${subcomponent.name}`}>
                                            {subcomponent.name} 
                                    </Link>
    }                               
                                    </Stack>
                                    <Stack style={{
                                        marginLeft: theme.spacing(2),
                                        marginRight: theme.spacing(2)
                                    }}>
                                <EastIcon/> 
                                    </Stack>
                                    <Stack>
                                {name}
                                    </Stack>

                                </Typography>
                            </Stack>
                            <Stack style={{
                                        marginLeft: theme.spacing(2)
                                    }}
                            > 
                            <ComponentSubcomponentDisableButton
                            name={name}
                            subComponentName={subcomponent.name}
                            toggleReload={toggleReload}
                            />
                            </Stack>
                        </EntryAccordionSummarySubcomponent>
                    </EntryAccordion>
                ))}
                {component.supercomps.map((subcomponent,index) => (
                    <EntryAccordion key={index}>
                        <EntryAccordionSummarySubcomponent>
                            <Stack spacing={2} direction="row">
                                <SettingsInputComponentIcon/>
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4),
                                        display:'flex',
                                        alignItems:'center'                              
                                    }}
                                >
                                    <Stack>
                                    {
                                        <Link to={`/component/${subcomponent.name}`}>
                                            {subcomponent.name} 
                                    </Link>
    }                               
                                    </Stack>
                                    <Stack style={{
                                        marginLeft: theme.spacing(2),
                                        marginRight: theme.spacing(2)
                                    }}>
                                <KeyboardBackspaceIcon/> 
                        
                                    </Stack>
                                    <Stack>
                                {name}
                                    </Stack>
                                </Typography>
                            </Stack>
                        </EntryAccordionSummarySubcomponent>
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
                                    Component version
                                </Typography>
                                <Typography variant="h5">
                                    {component.version ?
                                        component.version.name : "N/A"}
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
                        expandonClick={toggleOpenPropertiesAccordion}
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
                        expandonClick={toggleOpenConnectionsAccordion}
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
                        expandonClick={toggleOpenSubcomponentsAccordion}
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
                        expandonClick={toggleOpenFlagsAccordion}
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
        <>
        <Authenticator />
        <Root>
            {content}
        </Root>
        </>
    )
}

export default ComponentPage;
