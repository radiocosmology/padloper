import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import { 
    TextField, 
    } 
from '@mui/material';

function ComponentTypeList() {
    
    // the list of component types in objects representation
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
    // must be in the set {'name'}
    const [orderBy, setOrderBy] = useState('name');

    // property to order the component types by
    // must be in the set {'name'}
    const [nameSubstring, setNameSubstring] = useState("");
    
    // how to order the elements
    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

    /*
    The function that updates the list of component types when the site is 
    loaded or a change of the component types is requested (upon state change).
    */
    useEffect(async () => {

        setLoaded(false);

        // create the URL query string
        let input = '/api/component_type_list'
        input += `?range=${min};${min + range}`
        input += `&orderBy=${orderBy}`
        input += `&orderDirection=${orderDirection}`
        input += `&nameSubstring=${nameSubstring}`

        // query the URL with flask, and set the input.
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setElements(data.result);
            setLoaded(true);
        });
    }, [
        min,
        range,
        orderBy,
        orderDirection,
        nameSubstring
    ]);

    /*
    function to change the component count when filters are updated.
    */
    useEffect(() => {

        fetch(`/api/component_type_count?nameSubstring=${nameSubstring}`).then(
            res => res.json()
        ).then(data => {
            setCount(data.result);

            setMin(0);
        });
    }, [
        nameSubstring
    ]);

    // the header cells of the table with their ids, labels, and whether you
    // can order by them.
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Component Type',
            allowOrdering: true,
        },
        {
            id: 'comments', 
            label: 'Comments',
            allowOrdering: false,
        },
    ];

    let tableRowContent = elements.map((e) => [
        e.name,
        e.comments,
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
                    <TextField 
                        label="Filter by name" 
                        variant="outlined" 
                        onChange={
                            (event) => {
                                setNameSubstring(event.target.value)
                            }
                        }
                    />
                }
            />

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

export default ComponentTypeList;