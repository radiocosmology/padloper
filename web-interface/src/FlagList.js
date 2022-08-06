import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import FlagFilter from './FlagFilter.js';
import Button from '@mui/material/Button'
import FlagAddButton from './FlagAddButton.js';
import FlagEndButton from './FlagEndButton.js';
import FlagReplaceButton from './FlagReplaceButton.js';
import { ThemeProvider, Typography } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import styled from '@mui/material/styles/styled';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import createTheme from '@mui/material/styles/createTheme';
import Stack from '@mui/material/Stack';
import ComponentEvent from './ComponentEvent.js';
import FlagEvent from './FlagEvent.js';
import DeleteIcon from '@mui/icons-material/Delete';


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

const AccordionDetails = styled(MuiAccordionDetails)(({ theme }) => ({
    padding: theme.spacing(2),
    borderTop: '1px solid rgba(0, 0, 0, .125)',
    
}));

const EntryAccordionDetails = styled(AccordionDetails)(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .015)',
    
}));

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

/*
A MUI component representing a button for disabling a component type.
 */
const DisableButton = styled((props) => (
    <Button 
    style={{
        maxWidth: '40px', 
        maxHeight: '30px', 
        minWidth: '30px', 
        minHeight: '30px',
    }}
    {...props}
        variant="outlined">
        <DeleteIcon/>
    </Button>
))(({ theme }) => ({
    
}))


/**
 * A MUI component that renders a list of flags.
 */
export default function FlagList() {

    // the list of flag in objects representation
    const [elements, setElements] = useState([]);

    // the first index to show
    const [min, setMin] = useState(0);

    // how many elements there are
    const [count, setCount] = useState(0);

    // the number of elements to show
    const [range, setRange] = useState(100);

    // whether the elements are loaded or not
    const [loaded, setLoaded] = useState(false);

    // property to order the flag types by
    // must be in the set {'name, start_time, end_time'}
    const [orderBy, setOrderBy] = useState('name');

    // how to order the elements
    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

    const [flag_types, setFlagTypes] = useState([]);
    const [flag_severities, setFlagSeverities] = useState([]);
    const [flag_components, setComponents] = useState([{
        name : 'Global'
    }]);

    /* filters stored as 
        [
            {
            name: <str>,
            types: <str>,
            severities: <int>
            },
            ...
        ]
    */
    const [filters, setFilters] = useState([]);

    /**
     * add an empty filter to filters
     */ 
    const addFilter = () => {
        setFilters([...filters, {
            name: "",
            type: "",
            severity: ""
        }])
    }

   /**
     * Remove a filter at some index.
     * @param {int} index - index of the new filter to be removed.
     * 0 <= index < filters.length
     */
    const removeFilter = (index) => {
        if (index >= 0 && index < filters.length) {
            let newFilters = filters.filter((element, i) => index !== i);
            setFilters(newFilters);
        }
    }

    /**
     * Change the filter at index :index: to :newFilter:.
     * @param {int} index - index of the new filter to be changed
     * 0 <= index < filters.length
     **/
    const changeFilter = (index, newFilter) => {
        if (index >= 0 && index < filters.length) {
            // make a shallow copy of the filters
            let filters_copy = [...filters];

            // set the element at index to the new filter
            filters_copy[index] = newFilter;

            // update the state array
            setFilters(filters_copy);
        }
    }

   /**
    * To send the filters to the URL, create a string that contains all the
    * filter information.
    * 
    * The string is of the format
    * "<name>,<ftype_name>,<fseverity_name>;...;<name>,<ftype_name>,<fseverity_name>"
    * @returns Return a string containing all of the filter information
    */
    const createFilterString = () => {

        let strSoFar = "";

        if (filters.length > 0) {

            // create the string 
            for (let f of filters) {
                strSoFar += `${f.name},${f.type},${f.severity};`;
            }

            // remove the last semicolon.
            strSoFar = strSoFar.substring(0, strSoFar.length - 1);
        }

        return strSoFar;
    }

    const [reloadBool, setReloadBool] = useState(false);
    function toggleReload() {
        setReloadBool(!reloadBool);
    }

            /**
     * Disable a flag.
     * @param {string} name - the name of the componentType which is being disabled.
     * @returns 
     */
    async function disableFlag(name) {
        
        // build up the string to query the API
        let input = `/api/disable_flag`;
        input += `?name=${name}`;

        return new Promise((resolve, reject) => {
            fetch(input).then(
                res => res.json()
            ).then(data => {
                if (data.result) {
                    toggleReload();
                }
                resolve(data.result);
            });
        });

    }
   /**
    * The function that updates the list of flags when the site is 
    * loaded or a change of the flags is requested 
    * (upon state change).
    */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // create the URL query string
            let input = '/api/flag_list';
            input += `?range=${min};${min + range}`;
            input += `&orderBy=${orderBy}`;
            input += `&orderDirection=${orderDirection}`;
            if (filters.length > 0) {
                input += `&filters=${createFilterString()}`;
            }

            // query the URL with flask, and set the input.
            fetch(input).then(
                res => res.json()
            ).then(data => {
                setElements(data.result);
                setLoaded(true);
            });
        }
        fetchData();
    }, [
        min,
        range,
        orderBy,
        orderDirection,
        filters,
        reloadBool
    ]);

    /**
     * Change the flag count when filters are updated.
     */
    useEffect(() => {
        let input = `/api/flag_count`;
        if (filters.length > 0) {
            input += `?filters=${createFilterString()}`;
        }
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setCount(data.result);
            setMin(0);
        });
    }, [
        filters,
        reloadBool
    ]);

    /**
     * Load all of the flag types (so they can be used for the filter)
     * 
     * TODO: THIS IS GARBAGE, WILL BE REALLY REALLY SLOW WHEN YOU HAVE A LOT
     * OF FLAG TYPES. INSTEAD, MAKE A FLAG TYPE AUTOCOMPLETE AND
     * THEN USE THEM IN THE FILTERS INSTEAD OF THIS PILE OF TRASH.
     */
    useEffect(() => {

        let input = '/api/flag_type_list'
        input += `?range=0;-1`
        input += `&orderBy=name`
        input += `&orderDirection=asc`
        input += `&nameSubstring=`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setFlagTypes(data.result);
        });
    }, []);

    /**
     * Load all of the flag severities (so they can be used for the filter)
     * 
     * TODO: THIS IS GARBAGE, WILL BE REALLY REALLY SLOW WHEN YOU HAVE A LOT
     * OF FLAG SEVERITIES. INSTEAD, MAKE A FLAG SEVERITY AUTOCOMPLETE AND
     * THEN USE THEM IN THE FILTERS INSTEAD OF THIS PILE OF TRASH.
     */
    useEffect(() => {

        let input = '/api/flag_severity_list'
        input += `?range=0;-1`
        input += `&orderBy=name`
        input += `&orderDirection=asc`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setFlagSeverities(data.result);
            console.log(data.result)
        });
    }, []);

    /**
     * Load all of the components (so they can be used for the filter)
     **/
    useEffect(() => {

        let input = '/api/component_list'
        input += `?range=0;-1`
        input += `&orderBy=name`
        input += `&orderDirection=asc`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setComponents((prevState) => {
                return prevState.concat(data.result)
            });
        });
    }, []);


// the header cells of the table with their ids, labels, and whether you
// can order by them.
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Flag',
            allowOrdering: true,
        },
        {
            id: 'Type', 
            label: 'Flag Type',
            allowOrdering: false,
        },
        {
            id: 'Severity', 
            label: 'Flag Severity',
            allowOrdering: false,
        },
        {
            id: 'More Information', 
            label: '',
            allowOrdering: false,
        },
        {

        },
        {

        },
    ];

    /**
     * the rows of the table. We are only putting:
     * - the name,
     * - the start time,
     * - flag's allowed types,
     * - flag's allowed severity,
     * - the comments associated with the property type.
     */
    let tableRowContent = elements.map((flag) => [
        flag.end_uid 
        ?
        flag.name
        :
        <Typography
        style={{
            display:'flex'
        }}>
        {flag.name}
        {
        <FlagEndButton
        name = {flag.name}
        toggleReload={toggleReload}
        />}
        </Typography>
        ,
        flag.flag_type.name,
        flag.flag_severity.name,
        ,
        <ThemeProvider theme={theme}>
        <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
          >
            <Typography>
                More Information
            </Typography>
        </AccordionSummary>
        <AccordionDetails>
            <Stack spacing={1}>
          <EntryAccordion>

        <EntryAccordionDetails>
            <Stack spacing={1}>
                <Stack 
                direction='row'
                justifyContent='space-between'
                alignItems='center'
                >
                <ComponentEvent
                    name="Start"
                    time={flag.start_time}
                    uid={flag.start_uid}
                    edit_time={flag.start_edit_time}
                    comments={flag.start_comments}
                    theme={theme} />
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
                {
                    <FlagEvent
                        name="Comments"
                        parameter = {flag.comments}
                        theme={theme}
                        />
                    }
                {
                    <FlagEvent
                        name="Components"
                        parameter={
                            flag.flag_components.length != 0
                            ? 
                            flag.flag_components.map((item)=>item + ' | ')
                            :
                            'Global'
                        }
                        theme={theme}
                        />
                    }
                            </Stack>
                        </EntryAccordionDetails>
                    </EntryAccordion>
        </Stack>
        </AccordionDetails>
      </Accordion>
    </ThemeProvider>,
    <FlagReplaceButton 
    nameFlag = {flag.name}
    flag_types={flag_types} 
    flag_severities={flag_severities} 
    flag_components={flag_components}
    toggleReload={toggleReload}
    />,
     <DisableButton
        onClick={
            ()=>{
                disableFlag(flag.name)
            }
        }
        />
    ]);

    return (
        <>
            <ElementRangePanel
                width="800px"
                min={min}
                updateMin={(n) => { setMin(n) }}
                range={range}
                updateRange={(n) => { setRange(n) }}
                count={count}
                rightColumn={
                    (
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={addFilter}
                        >
                            Add Filter
                        </Button>
                    )
                }
                rightColumn2 = {
                    <FlagAddButton 
                    flag_types={flag_types} 
                    flag_severities={flag_severities} 
                    flag_components={flag_components}
                    toggleReload={toggleReload}
                    />
                }
            />
            {
                filters.map(
                    (filter, index) => (
                        <FlagFilter
                            key={index}
                            width="700px"
                            addFilter={() => { }}
                            removeFilter={removeFilter}
                            changeFilter={changeFilter}
                            filter={filter}
                            index={index}
                            types={flag_types}
                            severities = {flag_severities}
                        />
                    )
                )
            }

            <ElementList
                width='1300px'
                tableRowContent={tableRowContent}
                loaded={loaded}
                orderBy={orderBy}
                direction={orderDirection}
                setOrderBy={setOrderBy}
                setOrderDirection={setOrderDirection}
                tableHeadCells={tableHeadCells}
            />
        </>

    )
}