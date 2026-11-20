import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

import { Button, FormControl, MenuItem, TextField, Select, Switch } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';

import { withBase, requireOkJson } from './paths.js';
import Authenticator from './components/Authenticator.js';
import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import ErrorMessage from './ErrorMessage.js';
import ComponentSequenceAddButton from './ComponentSequenceAddButton.js';

/**
 * A MUI component that represents a list of component sequences
 */
function ComponentSequenceList() {
    // the list of component sequences
    const [sequences, setSequences] = useState([]);

    // the first sequence index to show
    const [min, setMin] = useState(0);

    // how many sequences there are
    const [count, setCount] = useState(0);

    // the number of sequences to show
    const [range, setRange] = useState(100);

    // whether the sequences are loaded or not
    const [loaded, setLoaded] = useState(false);

    // property to order the sequences by
    // must be in the set {'name', 'component_type', 'format'}
    const [orderBy, setOrderBy] = useState('name');

    // error data to display, if any
    const [errorData, setErrorData] = useState(null);

    // ordering direction, 'asc' or 'desc'
    const [orderDirection, setOrderDirection] = useState('asc');

    // filters stored as list of objects
    const [filters, setFilters] = useState([]);

    // store the available component types as list of objects (future-proof)
    const [componentTypes, setComponentTypes] = useState([])

    // Update the state after a new component is added
    const [reloadBool, setReloadBool] = useState(false);
    function toggleReload() {
        setReloadBool(!reloadBool);
    }

    /**
     * Load the data when the site is loaded or when filter state changes.
     * Also reload the data when reload specifically requested by reloadBool.
     */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // set up query url
            let path = '/api/component_sequence_list';
            path += `?range=${min};${min+range}`;
            path += `&orderBy=${orderBy}`;
            path += `&orderDirection=${orderDirection}`;
            // implement filters later

            // query the URL and set the inputs
            fetch(withBase(path)).then(requireOkJson).then((data) => {
                if (data.result && typeof(data.result) === 'object') {
                    setErrorData(null);
                    setSequences(data.result);
                    setCount(data.result.length);
                    setLoaded(true);
                } else {
                    setSequences([]);
                    setCount(0);
                    setErrorData(JSON.parse(data.error));
                    setLoaded(true);
                }
            }).catch((err) => {
                console.error('Failed to load sequence list:', err);
                setSequences([]);
                setCount(0);
                setErrorData(err.message);
                setLoaded(true);
            });
        }
        fetchData();
    }, [min, range, orderBy, orderDirection, reloadBool]);

    /**
     * Function to load component types
     */
    useEffect(() => {
        // set the query url
        let path = "/api/component_type_list";
        path += `?range=0;100   `;
        path += `&orderBy=name`;
        path += `&orderDirection=asc`;
        path += `&nameSubstring=`;

        fetch(withBase(path)).then(requireOkJson).then((data) => {
            if (data.result && typeof(data.result) === 'object') {
                setComponentTypes(data.result);
            } else {
                setErrorData(data.error);
            }
        }).catch((err) => {
            console.error('Failed to load component types:', err);
            setComponentTypes([]);
            setErrorData(err.message);
        });
    }, []);

    // state variables for add/edit mode
    const [editMode, setEditMode] = useState(false); // (de)activate edit mode
    const [editSeq, setEditSeq] = useState(''); // name of sequence to edit
    const [name, setName] = useState('');
    const [componentType, setComponentType] = useState({});
    const [format, setFormat] = useState('');
    const [increment, setIncrement] = useState(false);
    const [nextSeq, setNextSeq] = useState(0);

    const handleEdit = (seqName) => {
        setEditSeq(seqName);

        // load all the temporary data
        let seq = sequences.find((s) => s.name === seqName);
        setName(seq.name);
        setComponentType(seq.component_type.name);
        setFormat(seq.format);
        setIncrement(seq.increment);
        setNextSeq(seq.next_seq);

        // everything loaded so activate edit mode
        setEditMode(true);
    };

    const handleDelete = (seqName) => {
        // post to flask server to delete the node
        let path = `/api/delete_sequence/${seqName}`;
        axios.post(withBase(path)).then((res) => {
            if (res?.data?.result) {
                toggleReload();
            } else {
                setErrorData(JSON.parse(res?.data?.error));
            }
        });
    };

    const handleSave = () => {
        // post to flask server to update data server-side
        let path = `/api/update_sequence/${editSeq}`;
        path += `?name=${name}`;
        path += `&component_type=${componentType}`;
        path += `&format=${format}`;
        path += `&increment=${increment}`;
        path += `&next_seq=${nextSeq}`;

        axios.post(withBase(path)).then((res) => {
            if (res?.data?.result) {
                toggleReload();
                // after data is saved, deactivate edit mode
                setEditSeq('');
                setEditMode(false);
            } else {
                setErrorData(JSON.parse(res?.data?.error));
            }
        });
    };

    const handleCancel = () => {
        setEditSeq('');
        setEditMode(false);
    };

    // header cells of the table
    const tableHeadCells = [
        {id: 'name', label: 'Sequence Name', allowOrdering: true},
        {id: 'component_type', label: 'Component Type', allowOrdering: true},
        {id: 'format', label: 'Format', allowOrdering: true},
        {id: 'increment', label: 'Increment', allowOrdering: true},
        {id: 'next_seq', label: 'Next', allowOrdering: false},
        {}, // edit/save and delete/cancel buttons
        // {}, // delete/cancel button
    ];

    // build the row content as an object map
    let tableRowContent = sequences.map(s => [
        s.name === editSeq ? (
            <TextField
                id="name"
                type="text"
                inputProps={{
                    inputMode: 'numeric',
                    pattern: '[0-9]*',
                    style: { textAlign: 'left' },
                }}
                variant="standard"
                size="small"
                value={name}
                onChange={(e) => {
                    let val = e.target.value;
                    setNextSeq(val.replace(/[^0-9]*/g, ''));
                }}
                sx={{
                    maxWidth: 150,
                }}
            />
        ) : s.name,,
        s.name === editSeq ? (
            <Select
                id="componentType"
                variant="standard"
                size="small"
                value={componentType}
                onChange={(e) => {
                    setComponentType(e.target.value);
                }}
                sx={{
                    maxWidth: 100,
                }}
            >
                {Object.values(componentTypes).map((item) => {
                    return (
                        <MenuItem value={item.name}>
                            {item.name}
                        </MenuItem>
                    )
                })}
            </Select>
        ) : s.component_type.name,
        s.name === editSeq ? (
            <TextField
                id="format"
                type="text"
                variant="standard"
                size="small"
                value={format}
                onChange={(e) => {
                    let val = e.target.value;
                    setFormat(val);
                }}
                sx={{
                    maxWidth: 120,
                }}
            />
        ) : s.format,
        s.name === editSeq ? (
            <Switch
                checked={increment}
                onChange={() => {setIncrement(!increment)}}
                slotProps={{
                    input: { 'aria-label': 'controlled' },
                }}
            />
        ) : (
            <Switch
                disabled
                checked={increment}
                slotProps={{
                    input: { 'aria-label': 'controlled' },
                }}
            />
        ),
        s.name === editSeq ? (
            <TextField
                id="nextSeq"
                // label="Next Sequence"
                type="text"
                inputProps={{
                    inputMode: 'numeric',
                    pattern: '[0-9]*',
                    style: { textAlign: 'right' },
                }}
                variant="standard"
                size="small"
                value={nextSeq}
                onChange={(e) => {
                    let val = e.target.value;
                    setNextSeq(val.replace(/[^0-9]*/g, ''));
                }}
                sx={{
                    maxWidth: 40,
                }}
            />
        ) : s.next_seq,
        s.name === editSeq ? (
            <>
            <Button
                style={{
                    maxWidth: '30px',
                    maxHeight: '25px',
                    minWidth: '30px',
                    minHeight: '25px',
                    marginLeft: '0'
                }}
                variant="outlined"
                onClick={handleSave}
            >
                <SaveIcon />
            </Button>
            <Button
                style={{
                    maxWidth: '30px',
                    maxHeight: '25px',
                    minWidth: '30px',
                    minHeight: '25px',
                    marginLeft: '5px'
                }}
                variant="outlined"
                onClick={handleCancel}
            >
                <CloseIcon />
            </Button>
            </>
        ) : (
            <>
            <Button
                style={{
                    maxWidth: '30px',
                    maxHeight: '25px',
                    minWidth: '30px',
                    minHeight: '25px',
                    marginLeft:'0'
                }}
                variant="outlined"
                onClick={() => handleEdit(s.name)}
            >
                <EditIcon />
            </Button>
            <Button
                style={{
                    maxWidth: '30px',
                    maxHeight: '25px',
                    minWidth: '30px',
                    minHeight: '25px',
                    marginLeft:'5px'
                }}
                variant="outlined"
                onClick={() => handleDelete(s.name)}
            >
                <DeleteIcon />
            </Button>
            </>
        ),
    ]);

    return (
        <>
            <Authenticator />
            <ElementRangePanel
                min={min}
                updateMin={(n) => { setMin(n) }}
                range={range}
                updateRange={(n) => { setRange(n) }}
                count={count}
                width={"800px"}
                rightColumn={(
                    <ComponentSequenceAddButton
                        componentTypes={componentTypes}
                        toggleReload={toggleReload}
                    />
                )}
            />

            <ErrorMessage
                style={{ marginTop: '10px', marginBotton: '10px' }}
                errorMessage={errorData}
            />

            <ElementList
                tableRowContent={tableRowContent}
                loaded={loaded}
                orderBy={orderBy}
                direction={orderDirection}
                setOrderBy={setOrderBy}
                setOrderDirection={setOrderDirection}
                tableHeadCells={tableHeadCells}
                width={"800px"}
            />
        </>
    )
}

export default ComponentSequenceList;
