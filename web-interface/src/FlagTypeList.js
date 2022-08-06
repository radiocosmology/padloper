import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import { 
    TextField, 
    } 
from '@mui/material';
import FlagTypeAddButton from './FlagTypeAddButton.js';
import FlagTypeReplaceButton from './FlagTypeReplaceButton.js'
import styled from '@mui/material/styles/styled';
import DeleteIcon from '@mui/icons-material/Delete';
import Button from '@mui/material/Button';

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
 * A MUI component that renders a list of flag types.
 */
function FlagTypeList() {
    
    // the list of flag types in objects representation
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
    // must be in the set {'name'}
    const [orderBy, setOrderBy] = useState('name');

    // property to order the flag types by
    // must be in the set {'name'}
    const [nameSubstring, setNameSubstring] = useState("");
    
    // how to order the elements
    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

        
    const [reloadBool, setReloadBool] = useState(false);
    function toggleReload() {
        setReloadBool(!reloadBool);
    }

            /**
     * Disable a component Type.
     * @param {string} name - the name of the componentType which is being disabled.
     * @returns 
     */
    async function disableFlagType(name) {
        
        // build up the string to query the API
        let input = `/api/disable_flag_type`;
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


    /*
    The function that updates the list of flag types when the site is 
    loaded or a change of the flag types is requested (upon state change).
    */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // create the URL query string
            let input = '/api/flag_type_list'
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
        }
        fetchData();
    }, [
        min,
        range,
        orderBy,
        orderDirection,
        nameSubstring,
        reloadBool
    ]);

    /**
     * function to change the flag count when filters are updated.
     */
    useEffect(() => {

        fetch(`/api/flag_type_count?nameSubstring=${nameSubstring}`).then(
            res => res.json()
        ).then(data => {
            setCount(data.result);

            setMin(0);
        });
    }, [
        nameSubstring,
        reloadBool
    ]);

    /**
     * The header cells of the table with their ids, labels, and whether you
     * can order by them.
     */
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Flag Type',
            allowOrdering: true,
        },
        {
            id: 'comments', 
            label: 'Comments',
            allowOrdering: false,
        },
        {

        },
        {

        },
    ];
    /**
     * the rows of the table. We are only putting the name and the comments.
     */
    let tableRowContent = elements.map((e) => [
        e.name,
        e.comments,
        <FlagTypeReplaceButton
        nameFlagType = {e.name}
        toggleReload={toggleReload}
        />,
        <DisableButton
        onClick={
            ()=>{
                disableFlagType(e.name)
            }
        }
        />
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
                rightColumn2= {
                    <FlagTypeAddButton
                    toggleReload={toggleReload}
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

export default FlagTypeList;