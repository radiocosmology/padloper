import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import ComponentFilter from './ComponentFilter.js';
import { Link } from "react-router-dom";
import Button from '@mui/material/Button';

/**
 * A MUI component that represents a list of components.
 */
function ComponentList() {

    // the list of components in objects representation
    const [components, setComponents] = useState([]);

    // the first component index to show
    const [min, setMin] = useState(0);

    // how many components there are
    const [count, setCount] = useState(0);

    // the number of components to show
    const [range, setRange] = useState(100);

    // whether the components are loaded or not
    const [loaded, setLoaded] = useState(false);

    // property to order the components by.
    // must be in the set {'name', 'type', 'version'}
    const [orderBy, setOrderBy] = useState('name');

    /*
    stores component types as
    [
        {
        'name': <str>
        'versions': [
            <version name as str>,
            ...,
            <version name as str>
        ]
        }
    ]
    */
    const [types_and_versions,
        setTypesAndVersions] = useState([]);

    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

    /* filters stored as 
    [
    {
    name: <str>,
    type: <str>,
    version: <str>
    }
    ]
    */
    const [filters, setFilters] = useState([]);

    // add an empty filter to filters
    const addFilter = () => {
        setFilters([...filters, {
            name: "",
            type: "",
            version: ""
        }])
    }

    /* 
    Remove a filter at some index.
    index is an integer s.t. 0 <= index < filters.length
    */
    const removeFilter = (index) => {
        if (index >= 0 && index < filters.length) {
            let newFilters = filters.filter((element, i) => index !== i);
            setFilters(newFilters);
        }
    }

    /* 
    Change the filter at index :index: to :newFilter:.
    index is an integer s.t. 0 <= index < filters.length
    */
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

    /*
    To send the filters to the URL, create a string that contains all the
    filter information.

    The string is of the format
    "<name>,<ctype_name>,<rev_name>;...;<name>,<ctype_name>,<rev_name>"

    */
    const createFilterString = () => {

        let strSoFar = "";

        if (filters.length > 0) {

            // create the string 
            for (let f of filters) {
                strSoFar += `${f.name},${f.type},${f.version};`;
            }

            // remove the last semicolon.
            strSoFar = strSoFar.substring(0, strSoFar.length - 1);
        }

        return strSoFar;
    }

    /*
    The function that updates the list of components when the site is loaded
    or a change of the components is requested (upon state change).
    */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // create the URL query string
            let input = '/api/component_list'
            input += `?range=${min};${min + range}`
            input += `&orderBy=${orderBy}`
            input += `&orderDirection=${orderDirection}`
            if (filters.length > 0) {
                input += `&filters=${createFilterString()}`;
            }
    
            // query the URL with flask, and set the input.
            fetch(input).then(
                res => res.json()
            ).then(data => {
                setComponents(data.result);
                setLoaded(true);
            });
        }
        fetchData();
    }, [
        min,
        range,
        orderBy,
        orderDirection,
        filters
    ]
    );

    /*
    function to change the component count when filters are updated.
    */
    useEffect(() => {

        fetch(`/api/component_count?filters=${createFilterString()}`).then(
            res => res.json()
        ).then(data => {
            setCount(data.result);

            setMin(0);
        });
    }, [filters]);

    /*
    When the site is loaded, load all of the component types and versions.
    */
    useEffect(() => {
        fetch("/api/component_types_and_versions").then(
            res => res.json()
        ).then(data => {
            setTypesAndVersions(data.result);
        });
    }, []);

    // the header cells of the table with their ids, labels, and how to align
    // them. 
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Component Name',
            allowOrdering: true,
        },
        {
            id: 'type', 
            label: 'Type',
            allowOrdering: true,
        },
        {
            id: 'version', 
            label: 'Version',
            allowOrdering: true,
        },
    ];

    // What to display in each row.
    let tableRowContent = components.map(c => [
        <Link to={`/component/${c.name}`}>
            {c.name}
        </Link>,
        c.type.name,
        c.version.name,
    ]);

    return (
        <>
            <ElementRangePanel
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
            />

            {
                filters.map(
                    (filter, index) => (
                        <ComponentFilter
                            addFilter={() => { }}
                            removeFilter={removeFilter}
                            changeFilter={changeFilter}
                            filter={filter}
                            index={index}
                            types_and_versions={types_and_versions}
                        />
                    )
                )
            }

            <ElementList
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

export default ComponentList;
