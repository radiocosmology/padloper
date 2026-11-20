import React, {
    useState, useEffect, useRef, useCallback, useMemo, useLayoutEffect,
} from 'react';
import ReactDOM from 'react-dom';
import ReactFlow, {
    Controls, Background, Handle, ControlButton, applyNodeChanges,
    applyEdgeChanges, ReactFlowProvider, useReactFlow, MiniMap,
    useNodesState, useEdgesState, Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import styled from '@mui/material/styles/styled';
import createTheme from '@mui/material/styles/createTheme';
import { Link } from "react-router-dom";
import './custom.css'

import Dagre, { layout } from 'dagre';
import ELK from 'elkjs';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import OutlinedInput from '@mui/material/OutlinedInput';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Fab from '@mui/material/Fab'

import UnfoldMoreIcon from '@mui/icons-material/UnfoldMore';
import UnfoldLessIcon from '@mui/icons-material/UnfoldLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
//import DragHandleRoundedIcon from '@mui/icons-material/DragHandleRounded';
import SortIcon from '@mui/icons-material/Sort';

import ComponentAutocomplete from './ComponentAutocomplete.js';
import { ThemeProvider } from '@emotion/react';

import { unixTimeToISOString } from './utility/utility.js';
import Authenticator from './components/Authenticator.js';
import { minWidth } from '@mui/system';
import { Checkbox, FormLabel } from '@mui/material';

window.addEventListener("error", (e) => {
    if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || e.message === 'ResizeObserver loop limit exceeded') {
        e.stopImmediatePropagation();
    }
});


const position = { x: 0, y: 0 };


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
    width: '100%',
    height: '100%',
    textAlign: 'center',
}));

/**
 * ELK graph used for positioning nodes
 * See https://github.com/kieler/elkjs
 */
const elk = new ELK();

const elkOptions = {
    'elk.algorithm': 'layered',
    'elk.layered.spacing.nodeNodeBetweenLayers': '50',
    'elk.spacing.nodeNode': '10',
    'elk.hierarchyHandling': 'INCLUDE_CHILDREN',
    'elk.layered.nodePlacement.bk.fixedAlignment': 'LEFTDOWN',
};

const getLayoutedElements = (nodes, edges, options = {}, sizes = {}) => {
    function prepNode(node) {
        let size = sizes[node.id];
        let children = node.children ? node.children.map(prepNode) : node.children;
        return {
            ...node,
            // Adjust the target and source handle positions based on the layout
            // direction.
            targetPosition: isHorizontal ? 'left' : 'top',
            sourcePosition: isHorizontal ? 'right' : 'bottom',

            // Hardcode a width and height for elk to use when layouting.
            width: size ? size.width : 200,
            height: size ? size.height + 10 : 50,

            // apply mapping on child nodes
            children: children,

            // change layout options of parents
            layoutOptions: children ? {
                ...node.layoutOptions,
                "elk.padding": `[left=10, top=${size ? size.height + 10 : 60}, right=10, bottom=10]`,
                "elk.spacing.nodeNode": "10",
            } : node.layoutOptions
        }
    }

    function mapChildren(node, parent=undefined) {
        var res = [];
        for (let i = 0; i < node.children.length; i++) {
            const child = node.children[i];
            let childData = {
                ...child,
                position: { x: child.x, y: child.y },
                style: {
                    width: child.width,
                    minHeight: child.height
                },
            };
            childData.data.minHeight = child.height;
            childData.data.minWidth = 200;
            if (parent) {
                childData.parentId = parent;
                childData.extent = 'parent';
            }
            res.push(childData);
            if (child.children) {
                res.push(...mapChildren(child, child.id));
            }
        }
        return res;
    }

    const isHorizontal = options?.['elk.direction'] === 'RIGHT';
    const graph = {
        id: 'root',
        layoutOptions: options,
        children: nodes.map(prepNode),
        edges: edges,
    };

    return elk
        .layout(graph)
        .then((layoutedGraph) => {
            let res = {
                nodes: mapChildren(layoutedGraph),
                edges: layoutedGraph.edges,
            }
            return res;
        })
        .catch(console.error);
};

function NewConnectionsPanel() {
    const isMounted = useRef(false);

    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const { fitView } = useReactFlow();

    // const onConnect = (params) => setEdges((eds) => addEdge(params, eds));
    const onLayout = useCallback(({ direction }) => {
        if (!isMounted.current) {
            return;
        }

        const elements = document.querySelectorAll('.react-flow__node');
        let sizes = {};
        elements?.forEach(el => {
            let id = el?.dataset?.id;
            let paperEl = el?.querySelector('.MuiPaper-root');
            let gridEl = paperEl?.querySelector('.MuiGrid-item');
            if (id) {
                sizes[id] = { width: paperEl?.clientWidth, height: gridEl?.clientHeight };
            }
        });

        const opts = { 'elk.direction': direction, ...elkOptions };

        getLayoutedElements(nodes, edges, opts, sizes).then(
            ({ nodes: layoutedNodes, edges: layoutedEdges }) => {
                setNodes(layoutedNodes);
                setEdges(layoutedEdges);
                fitView();
            },
        );

        if (firstRender) {
            // fitView();
            setFirstRender(false);
            // return;
        }
    }, [nodes, edges]);

    // Calculate the initial layout on mount.
    // useLayoutEffect(() => {
    //     onLayout({ direction: 'DOWN' });
    // }, []);

    // encapsulates the active component
    const [component, setComponent] = useState(undefined);
    const componentRef = useRef();
    componentRef.current = component;

    // encapsulates the set of all active components
    const [allComponents, setAllComponents] = useState([]);

    // encapsulates the set of all active connections
    const [allConnections, setAllConnections] = useState([]);

    // encapsulates the unix time in MILLISECONDS at which we are visualizing
    const enteredTime = useRef(Math.floor(Date.now()));

    // encapsulates the unix time in MILLISECONDS at which we are visualizing
    // const [viewTime, setViewTime] = useState(Math.floor(Date.now()));

    // encapsulates the depth of our search
    const [depth, setDepth] = useState(0);

    // state that acts as a trigger to reload the visualization
    const [reloadTrigger, setReloadTrigger] = useState(false);

    // state that acts as a flag for when the components are ready to process
    const [componentsReady, setComponentsReady] = useState(false);

    // state that acts as a flag for when the nodes have been set properly
    const [nodesReady, setNodesReady] = useState(false);

    // check if this is the first render
    const [firstRender, setFirstRender] = useState(true);

    // set the URL to current state when inputs are changed
    useEffect(() => {
        if (!isMounted.current) {
            return;
        }
        if (component !== undefined) {
            const timeSeconds = parseInt(enteredTime.current/1000)
            window.location.hash = `#cmp=${component.name}&time=${timeSeconds}&depth=${depth}`;
        }
    }, [reloadTrigger, depth]);

    const fetchData = async () => {
        // Function to parse hash parameters from the URL
        const getHashParams = () => {
            const hash = window.location.hash.substring(1);
            const params = new URLSearchParams(hash);
            return {
                component: params.get('cmp') || undefined,
                time: params.get('time') || Math.floor(Date.now() / 1000),
                depth: params.get('depth'),
                // expanded: params.get('expanded') ? params.get('expanded').split(',') : [],
            };
        };

        // get params
        const {
            component: initialCmp,
            time: initialTime,
            depth: initialDepth,
            // expanded: initialExpanded,
        } = getHashParams();

        if (initialDepth) {
            setDepth(initialDepth);
        }

        if (initialCmp) {
            try {
                const response = await fetch(`/api/components_tree/${initialCmp}/${initialDepth}/${initialTime}`)
                const data = await response.json();
                // setUrlSet(true);
                setAllComponents(data.result.nodes);
                setAllConnections(data.result.edges);
                setComponent(data.result.nodes[0]);
                setComponentsReady(!componentsReady);
            } catch (error) {
                console.error('Failed to get component', error);
            }
        }
    }

    /**
     * Clear everything and fetch the data when reloadTrigger is toggled
     */
    useEffect(() => {
        setNodes([]);
        setEdges([]);
        fetchData();
    }, [reloadTrigger]);

    /**
     * Process the component and connection information into a node and
     * edge list that we can render
     */
    const processData = () => {
        const getNode = (id, arr) => {
            for (let i = 0; i < arr.length; i++) {
                let node = arr[i];
                if (id === node.id) {
                    return node;
                } else if (node.children) {
                    let childNode = getNode(id, node.children);
                    if (childNode) {
                        return childNode
                    }
                }
            }
        }
        const moveChild = (childId, parentId) => {
            let childIndex = newNodes.findIndex(node => node.id === childId);
            let child = newNodes[childIndex];
            newNodes.splice(childIndex, 1);
            let parent = getNode(parentId, newNodes);
            if (parent && parent.children) {
                parent.children.push(child);
            } else if (parent) {
                parent.children = [child];
                parent.layoutOptions = {
                    ...parent.layoutOptions,
                    "elk.padding": "[left=10, top=50, right=10, bottom=10]",
                    "elk.spacing.nodeNode": "10",
                }
            }
        }
        let newNodes = [];
        allComponents.forEach(comp => {
            let nodeData = {
                id: comp.id.toString(),
                data: { label: comp.name, ctype: comp.ctype, version: comp.version },
                type: 'component',
                position,
                layoutOptions: {},
                level: comp.level,
            }
            // if (comp.level === Math.max(...allComponents.map(c => c.level))) {
            //     nodeData.layoutOptions = {
            //         ...nodeData.layoutOptions,
            //         'elk.layered.layering.layerConstraint': 'LAST_SEPARATE',
            //     }
            // }
            if (comp.id === component.id) {
                nodeData.layoutOptions = {
                    ...nodeData.layoutOptions,
                    'elk.alignment': "CENTER"
                }
            }
            newNodes.push(nodeData);
        });

        let newEdges = [];
        allConnections.forEach(conn => {
            if (newEdges.map((e) => e.id).includes(conn.id)) {
                return;
            }
            if (conn.label === 'rel_connection') {
                let outLevel = allComponents.find(node => node.id === conn["OUT"].id).level;
                let inLevel = allComponents.find(node => node.id === conn["IN"].id).level;
                newEdges.push({
                    id: conn.id["@value"].relationId,
                    source: (outLevel < inLevel) ? conn["OUT"].id.toString() : conn["IN"].id.toString(),
                    target: (outLevel < inLevel) ? conn["IN"].id.toString() : conn["OUT"].id.toString(),
                    type: 'smoothstep',
                });
            } else if (conn.label === 'rel_subcomponent') {
                moveChild(conn["OUT"].id.toString(), conn["IN"].id.toString());
            }
        });

        setNodes(newNodes);
        setEdges(newEdges);
        setNodesReady(!nodesReady);
    }

    /**
     * After the data is fetched on reload trigger, process the data using
     * a trigger on the components and connections
     */
    useEffect(() => {
        if (!isMounted.current) {
            return;
        }
        processData();
    }, [componentsReady]);

    /**
     * After the first render, trigger a re-render to align properly
     */
    // useEffect(() => {
    //     if (!isMounted.current) {
    //         return;
    //     }
    //     processData();
    // }, [firstRender]);

    /**
     * Render the components once the data has been loaded
     */
    useEffect(() => {
        if (!isMounted.current) {
            return;
        }
        onLayout({ direction: 'DOWN' });
    }, [nodesReady])

    /**
     * This last-triggered effect lets the program know everything has been
     * mounted.
     */
    useEffect(() => {
        isMounted.current = true;
    }, [])

    /**
     * Expand the connections of a node
     */
    // const expandConnections = async function (name, time) {
    //     return new Promise((resolve) => {
    //         expandNodes(name, time).then(
    //             (addedNodes) => {
    //                 // Resizing and re-positioning nodes is done after the
    //                 // promise is resolved, because we need to wait for React Flow to finish
    //                 // its calculations first. (this still doesn't work perfecty!)
    //                 for (var i = 0; i < addedNodes.length; i++) {
    //                     // if one of the added components is a parent node
    //                     if (isParentNode.current[addedNodes[i].name]) {
    //                         setAddedParent(addedNodes[i].name);
    //                     }
    //                 }
    //                 if (isParentNode.current[name]) {
    //                     if (componentRef.current.name === name) {
    //                         setAddedParent(name);
    //                     }
    //                     // update state if expanded node is a supercomponent
    //                     else {
    //                         setExpandedSupercomponent(name);
    //                     }
    //                 }
    //                 resolve(addedNodes);
    //             }
    //         );
    //     })
    // }

    /**
    * A MUI component representing a component node.
    * @param {*} data - data for the React Flow component.
    */
    const ComponentNode = function ({ data, style }) {
        return (
            <ThemeProvider theme={theme}>
                <Handle
                    type="target"
                    position="top"
                    style={{ background: 'none', border: 'none', top: '0' }}
                />
                <Handle
                    type="source"
                    position="bottom"
                    style={{ background: 'none', border: 'none', bottom: '0' }}
                />
                <ComponentNodeWrapper>
                    <Grid
                        container
                        justifyContent="center"
                        style={{
                            height: '100%',
                            minHeight: data.minHeight,
                        }}
                    >
                        <Grid item xs={10} style={{height: 'fit-content'}}>
                            <Link to={`/component/${data.label}`}>
                                {data.label}
                            </Link>
                            <br />{data.ctype}
                            {data.version != null && <span><br />{data.version}</span>}
                            {/* <br />pushing
                            <br />a whole bunch
                            <br />of extra stuff
                            <br />to explore spacing */}
                            {/* <br />
                            {propertiesVisible ? <div><p>hey</p></div> : ''}
                            {data.shownProperties ? data.shownProperties.map(([propertyName, values, unit]) => (
                                <div key={propertyName}>
                                    <p>
                                        <u>{propertyName}:</u> {values.join(', ')} {unit}
                                    </p>
                                </div>
                            ))
                                : ''} */}
                            {/* </Typography> */}
                        </Grid>
                        {/* <Fab
                            aria-label="expand"
                            size="small"
                            sx={{
                                position: 'absolute',
                                top: 0,
                                right: 0,
                                // color: 'primary.main',
                                background: 'none',
                                boxShadow: 'none',
                                maxWidth: '30px',
                                minWidth: '30px',
                                maxHeight: '30px',
                                minHeight: '30px',
                                '&:hover': {
                                    background: 'none',
                                }
                            }}
                            onClick={() => {
                                expandConnections(data.name, enteredTime.current);
                            }}
                        >
                            <ExpandMoreIcon />
                        </Fab> */}
                    </Grid>
                </ComponentNodeWrapper>
            </ThemeProvider>
        )
    }

    const nodeTypes = useMemo(() => ({ component: ComponentNode }), []);

    return (
        <>
            <Authenticator/>
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
                            direction={"row"}
                            justifyContent={"center"}
                            alignItems={"center"}
                            spacing={4}
                        >
                            <ComponentAutocomplete
                                onSelect={(val) => {
                                    setComponent(val);
                                }}
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
                                onChange={(e) => {
                                    let date = new Date(e.target.value);
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
                                    value={depth}
                                    sx={{ width: 130 }}
                                    onChange={(e) => {
                                        let val = e.target.value;
                                        setDepth(
                                            Math.min(100, Math.max(
                                                0, parseInt(val) | 0
                                            ))
                                        );
                                    }}
                                />
                            </FormControl>
                            <Button
                                variant="contained"
                                onClick={() => {
                                    // trigger a reload with the new component
                                    setReloadTrigger(!reloadTrigger);
                                }}
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
                            nodes={nodes}
                            edges={edges}
                            // onConnect={onConnect}
                            onNodesChange={onNodesChange}
                            onEdgesChange={onEdgesChange}
                            nodeTypes={nodeTypes}
                            fitView
                        >
                            <Background
                                variant='dots'
                                gap={12}
                                size={.5}
                            />
                            <Controls>
                                <ControlButton
                                    onClick={() => { processData() }}
                                >
                                    <SortIcon />
                                </ControlButton>
                            </Controls>
                            <MiniMap pannable zoomable/>
                        </ReactFlow>
                    </VisualizerPanel>
                </Grid>
            </Grid>
        </>
    )
}

export default function NewVisualizer() {
    return (
        <ReactFlowProvider>
            <NewConnectionsPanel />
        </ReactFlowProvider>
    )
}
