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

const theme = createTheme({
    typography: {
        body2: {
            fontWeight: 800,
            fontSize: 16,
        },
    }
});

const TextLink = styled((props) => (
    <Link
        {...props}
        style={{
            textDecoration: 'none',    
        }}
    />
))(({ theme }) => ({
}));

const Root = styled((props) => (
    <Paper 
        {...props}
    />
))(({ theme }) => ({
    marginTop: theme.spacing(1),
    padding: theme.spacing(1),
    width: '1200px',
    maxWidth: '100%',
    marginLeft: 'auto',
    marginRight: 'auto',
    textAlign: 'center',
}));

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

// dagre layouting
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

// TODO: Probably don't hardcode this.
const nodeWidth = 160, nodeHeight = 50;

const getLayoutedElements = (elements) => {
    // https://reactflow.dev/examples/layouting/

    const direction = 'TB';

    dagreGraph.setGraph({ rankdir: direction });
  
    elements.forEach((el) => {
      if (isNode(el)) {
        dagreGraph.setNode(el.id, { width: nodeWidth, height: nodeHeight });
      } else {
        dagreGraph.setEdge(el.source, el.target);
      }
    });
  
    dagre.layout(dagreGraph);
  
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


export default function ComponentConnectionVisualizer() {

    // https://reactrouter.com/docs/en/v6/api#usesearchparams
    const [searchParams, setSearchParams] = useSearchParams();

    // console.log(searchParams.get("edges"));

    const [elements, setElements] = useState([]);

    const elementIds = useRef({});

    const [component, setComponent] = useState(undefined);

    // actual depth
    const [depth, setDepth] = useState(0);

    // value that the depth-input will show
    const [depthInputValue, setDepthInputValue] = useState(0);

    const toggleLayoutBoolRef = useRef(false);
    const [toggleLayoutBool, setToggleLayoutBool] = useState(false);
    const toggleLayout = () => {
        toggleLayoutBoolRef.current = !toggleLayoutBoolRef.current; 
        setToggleLayoutBool(toggleLayoutBoolRef.current) 
    };

    const enteredTime = useRef(Math.floor(Date.now()));
    const time = useRef(Math.floor(Date.now() / 1000));

    const defaultPosition = {x: 500, y: 270};

    function addElementId(id) {
        elementIds.current[id] = true;
    }

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

    const addEdge = (id, source, target) => {

        // catch it
        // TODO, MAKE THIS MORE EFFICIENT (dictionary lookup!!!)
        if (elementIds.current[id]) {
            return;
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
    }

    const removeElement = (id) => {
        let index = elements.findIndex(
            (els) => els.id === id
        );
        if (index > -1) {
            setElements((els) => els.splice(index, 1));
        }
        elementIds.current[id] = false;
    }

    const removeAllElements = () => {
        setElements([]);
        elementIds.current = {};
    }

    const visualizeComponent = async () => {
        if (component === undefined) {
            return;
        }

        removeAllElements();

        time.current = Math.floor(enteredTime.current / 1000);

        addComponent(
            component.name, 
            defaultPosition.x - nodeWidth / 2, 
            defaultPosition.y - nodeHeight / 2
        );

        // depth will be decremented by 1 each time, like BFS.

        // this will act as a quasi-queue 
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

        // funny BFS
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

    const onLayout = useCallback(
        () => {
            const layoutedElements = getLayoutedElements(elements);
            setElements(layoutedElements);
        },
        [elements]
    );

    useEffect(() => {
        onLayout();
    }, [toggleLayoutBool]);

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

    async function expandConnections(name, time) {

        let input = `/api/get_all_connections_at_time`;
        input += `?name=${name}`;
        input += `&time=${time}`;

        let componentsAdded = [];

        return new Promise(
            resolve => {
                fetch(input).then(
                    res => res.json()
                ).then(data => {
                    for (const edge of data.result) {
        
                        let otherName = (name === edge.inVertexName) ? 
                            edge.outVertexName : edge.inVertexName;
        
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
                                    const val = e.target.value;
                                    if (!val) {
                                        setDepthInputValue("");
                                        setDepth(0);
                                    }
                                    else {
                                        const parsedInt = parseInt(val);

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