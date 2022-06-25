import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import FlagFilter from './FlagFilter.js';
import Button from '@mui/material/Button'
import Timestamp from './Timestamp.js';
import FlagAddButton from './FlagAddButton.js';
import { Typography } from '@mui/material';
import FlagEndButton from './FlagEndButton.js';

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
    * "<name>,<ftype_name>,<fseverity_value>;...;<name>,<ftype_name>,<fseverity_value>"
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
        input += `&orderBy=value`
        input += `&orderDirection=asc`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setFlagSeverities(data.result);
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
            id: 'start_time', 
            label: 'Start Time',
            allowOrdering: true,
        },
        {
            id: 'end_time', 
            label: 'End Time',
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
            id: 'List_of_Components', 
            label: 'List Of Components',
            allowOrdering: false,
        },
        {
            id: 'Start_uid', 
            label: 'Start UID',
            allowOrdering: false,
        },
        {
            id: 'End_uid', 
            label: 'End UID',
            allowOrdering: false,
        },
        {
            id: 'start_comments', 
            label: 'Start comments',
            allowOrdering: false,
        },
        {
            id: 'end_comments', 
            label: 'End comments',
            allowOrdering: false,
        }
    ];

    /**
     * the rows of the table. We are only putting:
     * - the name,
     * - the start time,
     * - flag's allowed types,
     * - flag's allowed severity,
     * - the comments associated with the property type.
     */
    let tableRowContent = elements.map((e) => [
        e.end_uid 
        ?
        e.name
        :
        <Typography
        style={{
            display:'flex'
        }}>
        {e.name}
        {
        <FlagEndButton
        name = {e.name}
        toggleReload={toggleReload}
        />}
        </Typography>
        ,
       <Timestamp unixTime={e.start_time}/>,
       e.end_time !== 9223372036854776000 ? <Timestamp unixTime={e.end_time}/> : 'Ongoing',
        e.flag_type.name,
        e.flag_severity.value,
        e.flag_components != ''
        ? 
        e.flag_components.map((item,index)=>{
                return (
                    <li key={index}>{item}</li>
                )
        })
        :
        'Global',
        e.start_uid,
        e.end_uid,
        e.start_comments,
        e.end_comments,
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
                width='1200px'
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