import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactFlow, { 
    Controls, Background, Handle, Position, ControlButton, isNode,
    useZoomPanHelper
} from 'react-flow-renderer';
import styled from '@mui/material/styles/styled';
import createTheme from '@mui/material/styles/createTheme';
import { Link, useSearchParams } from "react-router-dom";

import dagre from 'dagre';

import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import OutlinedInput from '@mui/material/OutlinedInput';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';

import UnfoldMoreIcon from '@mui/icons-material/UnfoldMore';
import DragHandleRoundedIcon from '@mui/icons-material/DragHandleRounded';
import SortIcon from '@mui/icons-material/Sort';

import ComponentAutocomplete from './ComponentAutocomplete.js';
import { ThemeProvider } from '@emotion/react';

import { unixTimeToISOString } from './utility/utility.js';

/**
 * MUI custom theme
 * See https://mui.com/customization/theming/#theme-configuration-variables
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
 * Styled link with no text decoration.
 */
const TextLink = styled((props) => (
    <Link
        {...props}
        style={{
            textDecoration: 'none',    
        }}
    />
))(({ theme }) => ({
}));

/**
 * Styled component used as the backdrop for the options panel
 */
const OptionsPanel = styled((props) => (
    <Paper 
        {...props}
    />
))(({ theme }) => ({
    width: '1000px',
    maxWidth: '100%',
    textAlign: 'center',
    marginTop: theme.spacing(2),
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
}));

/**
 * Styled component used as the backdrop for the panel storing the visualization
 */
const VisualizerPanel = styled((props) => (
    <Paper 
        elevation={2}
        {...props}
    />
))(({ theme }) => ({
    height: '540px',
    width: '1000px',
    maxWidth: '100%',
}));

/**
 * Styled Paper component used as the wrapper for a component node in the
 * visualization.
 */
const ComponentNodeWrapper = styled((props) => (
    <Paper 
        variant="outlined"
        {...props}
    />
))(({ theme }) => ({
    background: 'white',
    borderColor: '#777777',
    borderWidth: '2px',
    width: '160px',
    height: '50px',
    textAlign: 'center',
}));

/**
 * Styled component used as the drag handle for the component nodes in the
 * visualization.
 */
const ComponentNodeDragHandle = styled((props) => (
    <Button
        className="drag-handle"
        disableRipple
        variant="outlined"
        size="small"
        style={{
            maxWidth: '25px',
            minWidth: '25px',
            maxHeight: '22px',
            minHeight: '22px',
            position: 'absolute',
            top: '-11px',
            left: 'calc(50% - 12.5px)',
            background: 'white',
            borderWidth: '2px',
        }}>
        <DragHandleRoundedIcon />
    </Button>
))(({ theme }) => ({

}));

/**
 * Styled button used as the button to expand a component's connections,
 * on the component nodes in the visualization.
 */
const ExpandConnectionsButton = styled((props) => (
    <Button 
        style={{
            maxWidth: '30px',
            minWidth: '30px',
            maxHeight: '30px',
            minHeight: '30px',
        }}
        {...props}
    >
        <UnfoldMoreIcon />
    </Button>
))(({ theme }) => ({
}));

/**
 * Dagre graph used for positioning nodes
 * See https://github.com/dagrejs/dagre 
 */
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

// TODO: Probably don't hardcode this.
const nodeWidth = 160, nodeHeight = 50;

/**
 * Lays out the nodes of the graph visualization in a top-to-bottom fashion.
 * 
 * @param {Array} elements - The list of nodes and edges for the React Flow
 * visualization
 * @returns A list of the nodes and edges with proper positioning.
 */
const getLayoutedElements = (elements) => {
    // https://reactflow.dev/examples/layouting/

    /**
     * The direction of the layout is top to bottom. This can be changed
     * by hardcoding it and changing it or by adding a parameter.
     */
    const direction = 'TB';

    dagreGraph.setGraph({ rankdir: direction });
  
    // set up the dagre graph
    elements.forEach((el) => {
        if (isNode(el)) {
            dagreGraph.setNode(el.id, { width: nodeWidth, height: nodeHeight });
        } else {
            dagreGraph.setEdge(el.source, el.target);
        }
    });
  
    // do layout
    dagre.layout(dagreGraph);
  
    // return the layouted elements
    return elements.map((el) => {
      if (isNode(el)) {
        const nodeWithPosition = dagreGraph.node(el.id);
        el.targetPosition = 'top';
        el.sourcePosition = 'bottom';
  
        // unfortunately we need this little hack to pass a slightly different 
        // position to notify react flow about the change. 
        // Moreover we are shifting the dagre node position 
        // (anchor=center center) to the top left so it matches the 
        // react flow node anchor point (top left).
        el.position = {
          x: nodeWithPosition.x - nodeWidth / 2 + Math.random() / 1000,
          y: nodeWithPosition.y - nodeHeight / 2,
        };
      }
  
      return el;
    });
};

/**
 * The MUI component that represents the visualizer for components along with
 * an option panel for changing the date when the component's connections
 * are considered, the component that is considered, and the depth of the
 * "branching" (when you press visualize, you have the option of branching out) 
 * @returns 
 */
export default function ComponentConnectionVisualizer() {

    // https://reactrouter.com/docs/en/v6/api#usesearchparams
    const [searchParams, setSearchParams] = useSearchParams();

    // console.log(searchParams.get("edges"));

    // the React Flow elements to be used in the visualization
    const [elements, setElements] = useState([]);

    // a dictionary that will store the React Flow IDs of the elements used
    const elementIds = useRef({});

    // which component is to be considered
    const [component, setComponent] = useState(undefined);

    // actual depth of the BFS search
    const [depth, setDepth] = useState(0);

    // value that the depth-input will show
    const [depthInputValue, setDepthInputValue] = useState(0);

    /**
     * The useRef hook is used as doing
     * setToggleLayoutBool(!toggleLayoutBool) will use the old value of
     * toggleLayoutBool before the state has been refreshed, so it won't
     * actually refreshed. However, using useRef like
     * "toggleLayoutBoolRef.current = !toggleLayoutBoolRef.current" will
     * instantly update the value of oggleLayoutBoolRef.current without
     * waiting for a state change.
     */
    const toggleLayoutBoolRef = useRef(false);
    const [toggleLayoutBool, setToggleLayoutBool] = useState(false);
    const toggleLayout = () => {
        toggleLayoutBoolRef.current = !toggleLayoutBoolRef.current; 
        setToggleLayoutBool(toggleLayoutBoolRef.current) 
    };

    // the unix time in MILLISECONDS. useRef so it can be instantly changed.
    const enteredTime = useRef(Math.floor(Date.now()));

    // the unix time in SECONDS. useRef so it can be instantly changed.
    const time = useRef(Math.floor(Date.now() / 1000));

    // the default position of nodes in the visualization.
    const defaultPosition = {x: 0, y: 0};

    /**
     * Indicate that a React Flow ID of "id" has been added to the
     * visualization.
     * @param {string} id 
     */
    function addElementId(id) {
        elementIds.current[id] = true;
    }

    /**
     * Add a component to the React Flow graph.
     * @param {string} name - the name of the component to add
     * @param {number} x - the x-coordinate of where to add the component
     * @param {number} y - the y-coordinate of where to add the component
     * @returns A Boolean indicating whether the component 
     * was successfully added.
     */
    async function addComponent(name, x, y) {

        // catch it
        if (elementIds.current[name]) {
            return false;
        }

        let newElement = {
            id: name,
            connectable: false,
            type: 'component',
            dragHandle: '.drag-handle',
            data: { name: name },
            position: { x: x, y: y },
        }
        
        addElementId(name);
        setElements((els) => els.concat(newElement));

        return true;
    }

    /**
     * Add an edge to the React Flow graph.
     * @param {string} id - the ID of the edge to add 
     * @param {string} source - the name of the component that the 
     * edge starts at.
     * @param {string} target - the name of the component that the
     * edge ends at. 
     * @returns Return whether the edge was successfully added.
     */
    const addEdge = (id, source, target) => {

        // catch it
        if (elementIds.current[id]) {
            return false;
        }

        let newElement = {
            id: id,
            source: source,
            target: target,
            type: 'smoothstep',
            style: {
                stroke: '#555555',
                strokeWidth: 1,
            }
        }
        addElementId(id);
        setElements((nodes) => nodes.concat(newElement));

        return true;
    }

    /**
     * Removes a React Flow element given the ID.
     * @param {string} id - The React Flow ID of the element to remove.
     */
    const removeElement = (id) => {
        let index = elements.findIndex(
            (els) => els.id === id
        );
        if (index > -1) {
            setElements((els) => els.splice(index, 1));
        }
        elementIds.current[id] = false;
    }

    /**
     * Remove all nodes and edges from the React Flow graph.
     */
    const removeAllElements = () => {
        setElements([]);
        elementIds.current = {};
    }

    /**
     * Visualize the component, and branch out and visualize nearby components
     * using breadth first search.
     */
    const visualizeComponent = async () => {
        if (component === undefined) {
            return;
        }

        removeAllElements();

        // the time should be in seconds instead of milliseconds
        time.current = Math.floor(enteredTime.current / 1000);

        // add the component
        /**
         * TODO: Change the position of the component so it appears below the
         * other components.
         */
        addComponent(
            component.name, 
            defaultPosition.x - nodeWidth / 2, 
            defaultPosition.y - nodeHeight / 2
        );

        // depth will be decremented by 1 each time, like BFS.

        /**
         * this will act as a quasi-queue (just increment the index each time
         * you dequeue something)  
         */ 
        let queue = [];

        // this will store names that are visited already.
        let visited = {};

        // the index of the element at the front of the queue,
        // to be incremented each time you "dequeue"
        let queueFrontIndex = 0;

        queue.push({name: component.name, currDepth: 0});

        if (depth == 0) {
            return;
        }

        // funny breadth first search
        while (queueFrontIndex < queue.length) {

            // so you don't add nodes that you've already visited
            visited[queue[queueFrontIndex].name] = true;

            let newComponents = await expandConnections(
                queue[queueFrontIndex].name, 
                time.current
            );

            if (queue[queueFrontIndex].currDepth + 1 < depth) {
                for (let compName of newComponents) {
                    if (!visited[compName]) {
                        queue.push({
                            name: compName, 
                            currDepth: queue[queueFrontIndex].currDepth + 1
                        })
                    }
                }
            }
            queueFrontIndex++;

            toggleLayout();
        }

    }

    /**
     * Layout the elements in the React Flow visuzalization using Dagre.
     */
    const onLayout = useCallback(
        () => {
            const layoutedElements = getLayoutedElements(elements);
            setElements(layoutedElements);
        },
        [elements]
    );

    // layout the graph once the toggle layout bool has been toggled
    useEffect(() => {
        onLayout();
    }, [toggleLayoutBool]);

    /**
     * A MUI component representing a component node.
     * @param {*} data - data for the React Flow component.
     * Really only need data.name from here.
     */
    function ComponentNode({ data }) {
        return (
            <ThemeProvider theme={theme}>
                <Handle 
                    type="target" 
                    position="top"
                    style={{background: 'none', border: 'none'}}
                />
                <Handle 
                    type="source" 
                    position="bottom"
                    style={{
                        background: 'none', 
                        border: 'none',
                        top: '88%',
                    }}
                />
                <ComponentNodeWrapper>
                    <ComponentNodeDragHandle />
                    <Grid
                        container
                        justifyContent="center"
                        alignItems="center"
                        style={{
                            height: '100%'
                        }}
                    >
                        <Grid item xs={9}>
                            <Typography
                                variant="body2"
                            >
                                <Link to={`/component/${data.name}`}>
                                    {data.name}
                                </Link>
                            </Typography>
                        </Grid>
                        <Grid item>
                            <ExpandConnectionsButton 
                                onClick={() => expandConnections(
                                    data.name, time.current)}
                            />
                        </Grid>
                    </Grid>
                </ComponentNodeWrapper>
            </ThemeProvider>
    
        )
    } 

    /**
     * Expand and visualize the components that the component with name "name"
     * is connected to at time "time"
     * @param {string} name - name of the component to check connections with 
     * @param {int} time - time to check components at
     * @returns A Promise, which, when resolved, returns the array of the names
     * of the components added.
     */
    async function expandConnections(name, time) {

        // construct the query string
        let input = `/api/get_all_connections_at_time`;
        input += `?name=${name}`;
        input += `&time=${time}`;

        /**
         * build up an array of the names of components actually added (does not
         * consider components that were already in the visualization)
         */
        let componentsAdded = [];

        return new Promise(
            resolve => {
                fetch(input).then(
                    res => res.json()
                ).then(data => {
                    for (const edge of data.result) {
        
                        let otherName = (name === edge.inVertexName) ? 
                            edge.outVertexName : edge.inVertexName;
        
                        // TODO: Change the default position.
                        let added = addComponent(otherName, 0, 0);
                        addEdge(
                            edge.id, 
                            edge.outVertexName, 
                            edge.inVertexName
                        );
        
                        if (added) {
                            componentsAdded.push(otherName);
                        }
                    }
                    resolve(componentsAdded);
                });
            }
        )
        
    }

    return (
        <Grid 
            container 
            direction="column"
            justifyContent="flex-start"
            alignItems="center"
            spacing={2}
        >

            <Grid item>
                <OptionsPanel>
                    <Stack
                        direction="row"
                        justifyContent="center"
                        alignItems="center"
                        spacing={4}
                    >
                        <ComponentAutocomplete 
                            onSelect={setComponent} 
                        />
                        <TextField
                            required
                            id="datetime-local"
                            label="Time"
                            type="datetime-local"
                            defaultValue={
                                unixTimeToISOString(enteredTime.current)
                            }
                            sx={{ width: 240 }}
                            InputLabelProps={{
                                shrink: true,
                            }}
                            size="large"
                            onChange={(event) => {
                                let date = new Date(event.target.value);
                                enteredTime.current = Math.round(
                                    date.getTime()
                                    );
                            }}
                        />

                        <FormControl>
                            <InputLabel htmlFor="depth-input">
                                Depth
                            </InputLabel>
                            <OutlinedInput 
                                id="depth-input"
                                type="number"
                                label="Depth"
                                defaultValue={depthInputValue}
                                value={depthInputValue}
                                sx={{ width: 130 }}
                                onChange={(e) => {

                                    // value of the depth
                                    const val = e.target.value;

                                    // if the depth field is empty, set it to 0
                                    if (!val) {
                                        setDepthInputValue("");
                                        setDepth(0);
                                    }
                                    else {
                                        const parsedInt = parseInt(val);

                                        /**
                                         * make sure that the depth is between
                                         * 0 and 100, inclusive.
                                         */
                                        let newDepth = (parsedInt <= 100) ?
                                            parsedInt : 100;
                                        if (newDepth < 0) {
                                            newDepth = -newDepth;
                                        }

                                        setDepth(newDepth);
                                        setDepthInputValue(newDepth);
                                    }

                                    return null;
                                }}
                                onBlur={(e) => {
                                    /**
                                     * When the user leaves the input empty,
                                     * set it to 0.
                                     */
                                    if (depthInputValue === "") {
                                        setDepth(0);
                                        setDepthInputValue(0);
                                    }
                                }}
                            />
                        </FormControl>
                        

                        <Button 
                            variant="contained"
                            onClick={visualizeComponent}
                            disabled={component === undefined}
                        >
                            Visualize
                        </Button>
                        
                    </Stack>
                </OptionsPanel>
            </Grid>

            <Grid item>
                <VisualizerPanel>
                    <ReactFlow 
                        elements={elements}
                        nodesConnectable={false}
                        nodeTypes={{component: ComponentNode}}
                    >
                        <Background
                            variant="dots"
                            gap={12}
                            size={0.5}
                        />
                        <Controls>
                            <ControlButton 
                                onClick={() => {onLayout()}}
                            >
                                <SortIcon />
                            </ControlButton>
                        </Controls>
                    </ReactFlow>
                </VisualizerPanel>
            </Grid>

        </Grid>

    )

}