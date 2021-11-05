import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import ElementFilter from './ElementFilter.js';
import { Link } from "react-router-dom";

import { 
    Button, 
    } 
    from '@material-ui/core';

function ComponentList() {

    // the list of components in objects representation
    const [components, setComponents] = useState([]);

    // the first component index to show
    const [component_min, setComponentMin] = useState(0);

    // how many components there are
    const [component_count, setComponentCount] = useState(0);

    // the number of components to show
    const [component_range, setComponentRange] = useState(100);

    // whether the components are loaded or not
    const [components_loaded, setComponentsLoaded] = useState(false);

    // property to order the components by.
    // must be in the set {'name', 'component_type', 'revision'}
    const [components_orderBy, setComponentsOrderBy] = useState('name');

    /*
    stores component types as
    [
        {
        'name': <str>
        'revisions': [
            <revision name as str>,
            ...,
            <revision name as str>
        ]
        }
    ]
    */
    const [component_types_and_revisions,
        setComponentTypesAndRevisions] = useState([]);

    // 'asc' or 'desc'
    const [components_orderDirection,
        setComponentsOrderDirection] = useState('asc');

    /* filters stored as 
    [
    {
    name: <str>,
    component_type: <str>,
    revision: <str>
    }
    ]
    */
    const [filters, setFilters] = useState([]);

    // add an empty filter to filters
    const addFilter = () => {
        setFilters([...filters, {
            name: "",
            component_type: "",
            revision: ""
        }])
    }

    /* 
    Remove a filter at some index.
    index is an integer s.t. 0 <= index < filters.length
    */
    const removeFilter = (index) => {
        if (index >= 0 && index < filters.length) {
            let newFilters = filters.filter((element, i) => index != i);
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
                strSoFar += `${f.name},${f.component_type},${f.revision};`;
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
    useEffect(async () => {

        setComponentsLoaded(false);

        // create the URL query string
        let input = '/api/component_list'
        input += `?range=${component_min};${component_min + component_range}`
        input += `&orderBy=${components_orderBy}`
        input += `&orderDirection=${components_orderDirection}`
        if (filters.length > 0) {
            input += `&filters=${createFilterString()}`;
        }

        // query the URL with flask, and set the input.
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setComponents(data.result);

            setComponentsLoaded(true);
        });
    }, [
        component_min,
        component_range,
        components_orderBy,
        components_orderDirection,
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
            setComponentCount(data.result);

            setComponentMin(0);
        });
    }, [filters]);

    /*
    When the site is loaded, load all of the component types and revisions.
    */
    useEffect(() => {
        fetch("/api/component_types_and_revisions").then(
            res => res.json()
        ).then(data => {
            setComponentTypesAndRevisions(data.result);
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
            id: 'component_type', 
            label: 'Type',
            allowOrdering: true,
        },
        {
            id: 'revision', 
            label: 'Revision',
            allowOrdering: true,
        },
    ];

    // 
    let tableRowContent = components.map((c) => [
        <Link to={`/component/${c.name}`}>
            {c.name}
        </Link>,
        c.component_type.name,
        c.revision.name,
    ]);

    return (
        <>
            <ElementRangePanel
                min={component_min}
                updateMin={(n) => { setComponentMin(n) }}
                range={component_range}
                updateRange={(n) => { setComponentRange(n) }}
                count={component_count}
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
                        <ElementFilter
                            addFilter={() => { }}
                            removeFilter={removeFilter}
                            changeFilter={changeFilter}
                            filter={filter}
                            index={index}
                            types_and_revisions={component_types_and_revisions}
                        />
                    )
                )
            }

            <ElementList
                tableRowContent={tableRowContent}
                loaded={components_loaded}
                orderBy={components_orderBy}
                direction={components_orderDirection}
                setOrderBy={setComponentsOrderBy}
                setOrderDirection={setComponentsOrderDirection}
                tableHeadCells={tableHeadCells}
            />
        </>

    )
}

export default ComponentList;