import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import PropertyTypeFilter from './PropertyTypeFilter.js';
import Button from '@mui/material/Button'
import PropertyTypeAddButton from './PropertyTypeAddButton.js';
import PropertyTypeReplaceButton from './PropertyTypeReplaceButton.js';





/**
 * A MUI component that renders a list of property types.
 */
export default function PropertyTypeList() {

    // the list of property types in objects representation
    const [elements, setElements] = useState([]);

    // the first index to show
    const [min, setMin] = useState(0);

    // how many elements there are
    const [count, setCount] = useState(0);

    // the number of elements to show
    const [range, setRange] = useState(100);

    // whether the elements are loaded or not
    const [loaded, setLoaded] = useState(false);

    // property to order the component types by
    // must be in the set {'name, units, allowed_regex, n_values'}
    const [orderBy, setOrderBy] = useState('name');

    // how to order the elements
    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

    const [componentTypes, setComponentTypes] = useState([]);

    /* filters stored as 
        [
            {
            name: <str>,
            types: <str>,
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
    * "<name>,<ctype_name>;...;<name>,<ctype_name>"
    * @returns Return a string containing all of the filter information
    */
    const createFilterString = () => {

        let strSoFar = "";

        if (filters.length > 0) {

            // create the string 
            for (let f of filters) {
                strSoFar += `${f.name},${f.type};`;
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
    * The function that updates the list of property types when the site is 
    * loaded or a change of the property types is requested 
    * (upon state change).
    */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // create the URL query string
            let input = '/api/property_type_list';
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
     * Change the property type count when filters are updated.
     */
    useEffect(() => {
        let input = `/api/property_type_count`;
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
     * Load all of the component types (so they can be used for the filter)
     * 
     * TODO: THIS IS GARBAGE, WILL BE REALLY REALLY SLOW WHEN YOU HAVE A LOT
     * OF COMPONENT TYPES. INSTEAD, MAKE A COMPONENT TYPE AUTOCOMPLETE AND
     * THEN USE THEM IN THE FILTERS INSTEAD OF THIS PILE OF TRASH.
     */
    useEffect(() => {

        let input = '/api/component_type_list'
        input += `?range=0;-1`
        input += `&orderBy=name`
        input += `&orderDirection=asc`
        input += `&nameSubstring=`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setComponentTypes(data.result);
        });
    }, []);

    // the header cells of the table with their ids, labels, and whether you
    // can order by them.
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Property Type',
            allowOrdering: true,
        },
        {
            id: 'allowed_type', 
            label: 'Allowed Types',
            allowOrdering: true,
        },
        {
            id: 'units', 
            label: 'Units',
            allowOrdering: false,
        },
        {
            id: 'allowed_regex', 
            label: 'Allowed Regex',
            allowOrdering: false,
        },
        {
            id: 'n_values', 
            label: '# of Values',
            allowOrdering: false,
        },
        {
            id: 'comments', 
            label: 'Comments',
            allowOrdering: false,
        },
        {

        }
    ];

    /**
     * the rows of the table. We are only putting:
     * - the name,
     * - a list of the property type's allowed types,
     * - the units,
     * - the allowed regex for the property type,
     * - the number of values a property must have, and
     * - the comments associated with the property type.
     * - property type replace button.
     */
    let tableRowContent = elements.map((e) => [
        e.name,
        e.allowed_types.sort().join(', '),
        e.units,
        e.allowed_regex,
        e.n_values,
        e.comments,
        <PropertyTypeReplaceButton
        key={e.name}
        name = {e.name}
        units = {e.units}
        allowed_regex = {e.allowed_regex}
        allowed_types = {e.allowed_types}
        values = {e.n_values ? e.n_values : 0}
        comments = {e.comments ? e.comments : ''}
        componentTypes={componentTypes}
        toggleReload={toggleReload}
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
                    <PropertyTypeAddButton 
                    componentTypes={componentTypes}
                    toggleReload={toggleReload}
                    />
                }
            />

            {
                filters.map(
                    (filter, index) => (
                        <PropertyTypeFilter
                            key={index}
                            width="700px"
                            addFilter={() => { }}
                            removeFilter={removeFilter}
                            changeFilter={changeFilter}
                            filter={filter}
                            index={index}
                            types={componentTypes}
                        />
                    )
                )
            }

            <ElementList
                width="800px"
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