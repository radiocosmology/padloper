import React, {
    useState, useEffect, useRef, useCallback,
    useMemo
} from 'react';
import ReactFlow, {
    Controls, Background, Handle, ControlButton,
    applyNodeChanges, applyEdgeChanges, ReactFlowProvider, useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';
import styled from '@mui/material/styles/styled';
import createTheme from '@mui/material/styles/createTheme';
import { Link } from "react-router-dom";
import './custom.css'

import Dagre from 'dagre';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import OutlinedInput from '@mui/material/OutlinedInput';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';

import UnfoldMoreIcon from '@mui/icons-material/UnfoldMore';
//import DragHandleRoundedIcon from '@mui/icons-material/DragHandleRounded';
import SortIcon from '@mui/icons-material/Sort';

import ComponentAutocomplete from './ComponentAutocomplete.js';
import { ThemeProvider } from '@emotion/react';

import { unixTimeToISOString } from './utility/utility.js';
import Authenticator from './components/Authenticator.js';

window.addEventListener("error", (e) => {
    if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || e.message === 'ResizeObserver loop limit exceeded') {
        e.stopImmediatePropagation();
    }
});

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
    width: '100%',
    height: '100%',
    textAlign: 'center',
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
const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

// TODO: Probably don't hardcode this.
let nodeWidth = 250;

const getLayoutedElements = (layoutNodes, nodes, edges, options) => {
    g.setGraph({ rankdir: options.direction });

    layoutNodes.forEach((node) => g.setNode(node.id, node));
    edges.forEach((edge) => g.setEdge(edge.source, edge.target));

    Dagre.layout(g);

    // Map only the layouted nodes
    const layoutedNodeIds = layoutNodes.map((node) => node.id);
    const layoutedNodes = nodes.map((node) => {
        if (layoutedNodeIds.includes(node.id)) {
            const { x, y } = g.node(node.id);
            return { ...node, position: { x, y } };
        }
        return node;
    });

    return {
        nodes: layoutedNodes,
        edges,
    };
};

/**
* The MUI component that represents the visualizer for components along with
* an option panel for changing the date when the component's connections
* are considered, the component that is considered, and the depth of the
* "branching" (when you press visualize, you have the option of branching out) 
* @returns 
*/
function ComponentConnectionsPanel() {

    // the React Flow nodes to be used in the visualization
    const [nodes, setNodes] = useState([]);

    // a dictionary to store whether each node is a parent or not
    const isParentNode = useRef({});

    // a dictionary to store the children of a given node
    const childrenNodes = useRef({});

    // from https://reactflow.dev/docs/guides/layouting/
    const { fitView } = useReactFlow();

    // a dictionary that will store the React Flow IDs of the nodes used
    const nodeIds = useRef({});

    // a dictionary that maps the node IDs to their "levels" (from the top node)
    const nodeLevels = useRef({});

    // a dictionary to store which nodes were expanded already
    const expandedNodes = useRef({});

    // the React Flow edges to be used in the visualization
    const [edges, setEdges] = useState([]);

    // a dictionary that will store the React Flow IDs of the edges used
    const edgeIds = useRef({});

    // which component is to be considered
    const [component, setComponent] = useState(undefined);
    const componentRef = useRef();
    componentRef.current = component;

    // actual depth of the BFS search
    const [depth, setDepth] = useState(0);

    // value that the depth-input will show
    const [depthInputValue, setDepthInputValue] = useState(0);

    const onNodesChange = useCallback((changes) => setNodes((nds) =>
        applyNodeChanges(changes, nds)), []);
    const onEdgesChange = useCallback((changes) => setEdges((eds) =>
        applyEdgeChanges(changes, eds)), []);

    // to store calls to expandConnections
    const [expanded, setExpanded] = useState([]);

    // to track whether url component is set
    const [urlSet, setUrlSet] = useState(false);

    const [propertiesVisible, setPropertiesVisible] = useState(false);
    const propertiesVisibleRef = useRef();
    propertiesVisibleRef.current = propertiesVisible;

    // the unix time in MILLISECONDS. useRef so it can be instantly changed.
    const enteredTime = useRef(Math.floor(Date.now()));

    // the unix time in SECONDS. useRef so it can be instantly changed.
    const time = useRef(Math.floor(Date.now() / 1000));

    // the default position of nodes in the visualization.
    const defaultViewport = { x: 0, y: 0 };

    const [reloadComponent, setReloadComponent] = useState(false);

    // React flow instance to access internal state (e.g., internal node properties like height)
    const flowInstance = useReactFlow();

    // States to be used for layouting the graph
    const [addedParent, setAddedParent] = useState(null);
    const [expandedSupercomponent, setExpandedSupercomponent] = useState(null);


    /**
     * Set the URL based on actions performed.
     */
    useEffect(() => {
        const cmp = component != undefined ? component.name : '';
        if (component != undefined) {
            window.location.hash = `#cmp=${cmp}&time=${enteredTime.current}&depth=${depth}&expanded=${expanded}`;
        }
    }, [reloadComponent, expanded, depth]);

    /**
     * Run series of functions from the URL.
     */

    const fetchData = async () => {
        // Function to parse hash parameters from the URL
        const getHashParams = () => {
            const hash = window.location.hash.substring(1);
            const params = new URLSearchParams(hash);
            return {
                component: params.get('cmp') || undefined,
                time: params.get('time') || Math.floor(Date.now() / 1000),
                depth: params.get('depth'),
                expanded: params.get('expanded') ? params.get('expanded').split(',') : [],
            };
        };

        // get params
        const {
            component: initialCmp,
            time: initialTime,
            depth: initialDepth,
            expanded: initialExpanded,
        } = getHashParams();

        // enteredTime.current = +initialTime;
        if (initialDepth) {
            setDepth(initialDepth);
            setDepthInputValue(initialDepth);
        }
        setExpanded(initialExpanded);

        if (initialCmp) {
            try {
                const response = await fetch(`/api/components_name/${initialCmp}`)
                const data = await response.json();
                setUrlSet(true);
                setComponent(data.result);
            } catch (error) {
                console.error('Failed to get component', error);
            }
        }
    };

    useEffect(() => {
        // Fetches data when we have to reload the component
        // (when reloadComponent is toggled)
        fetchData();
    }, [reloadComponent]);

    /**
     * To visualize component
     */
    useEffect(() => {
        const asyncExpand = async () => {
            if (urlSet && component) {
                visualizeComponent();
                // debugger;
                const expandedTemp = expanded.slice()
                for (let expand of expanded) {
                    await expandConnections(expand, time.current);
                }
                if (expandedTemp != []) {
                    setExpanded(expandedTemp);
                }
                setUrlSet(false);
            }
        }
        asyncExpand();

    }, [component]);

    /**
     * To modify node to have/display property information
     */
    function revealProperties(node) {
        if (node.data.properties && node.data.properties.length > 0) {
            console.log(node.data.properties)
            const filteredProperties = node.data.properties.filter((property) => {
                return property.start.time * 1000 <= enteredTime.current && enteredTime.current <= property.end.time * 1000
            })
            console.log(filteredProperties)
            console.log(filteredProperties.reduce((listOfLists, property) => {
                const { type: { name, units }, values } = property;
                listOfLists.push([name, values, units]);
                return listOfLists;
            }, []))
            return {
                ...node,
                data: {
                    ...node.data,
                    shownProperties: filteredProperties.reduce((listOfLists, property) => {
                        const { type: { name, units }, values } = property;
                        listOfLists.push([name, values, units]);
                        return listOfLists;
                    }, [])
                },
            };
        } else {
            return node;
        }
    }

    useEffect(() => {
        if (propertiesVisible) {
            console.log(enteredTime.current)
            setNodes((nds) =>
                nds.map((node) => {
                    return revealProperties(node);
                })
            );
        } else {
            setNodes((nds) =>
                nds.map((node) => {
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            shownProperties: ''
                        }
                    }
                })
            )
        }
    }, [propertiesVisible])


    /**
     * Sort the nodes so that "parent" nodes appear before "children"
     * nodes.
     */
    function sortNodes() {
        setNodes((prevNodes) => {
            const sortedNodes = prevNodes.slice().sort((a, b) => {
                const isParentA = isParentNode.current[a.id];
                const isParentB = isParentNode.current[b.id];
                const aInB = childrenNodes.current[b.id].includes(a.id);
                const bInA = childrenNodes.current[a.id].includes(b.id);

                if (isParentA && !isParentB) {
                    return -1;
                } else if (!isParentA && isParentB) {
                    return 1;
                } else if (isParentA && isParentB && bInA) {
                    return -1
                } else if (isParentA && isParentB && aInB) {
                    return 1
                }
                return 0;
            });
            return sortedNodes;
        });
    }

    /**
    * Indicate that a React Flow ID of "id" has been added to the
    * visualization.
    * @param {string} id 
    */
    function addNodeId(id) {
        nodeIds.current[id] = true;
    }
    function addEdgeId(id) {
        edgeIds.current[id] = true;
    }

    /**
    * Add a component to the React Flow graph.
    * @param {string} name - the name of the component to add
    * @param {number} x - the x-coordinate of where to add the component
    * @param {number} y - the y-coordinate of where to add the component
    * @param {number} row - the "row" that this component will occupy
    * @returns A Boolean indicating whether the component 
    * was successfully added.
    */
    // TODO: need for async??
    function addComponent(comp, x, y, row, subcomponent = false, parent = null, width = '250px', height = '50px') {
        // catch it
        if (nodeIds.current[comp.name]) {
            return false;
        }
        let newNode;
        if (subcomponent) {
            console.log("Adding sub component ", comp)
            console.log("Coords: ", x, y)
            newNode = {
                id: comp.name,
                connectable: false,
                type: 'component',
                //            dragHandle: '.drag-handle',
                data: {
                    name: comp.name, ctype: comp.type, version: comp.version, properties: comp.properties, shownProperties: '',
                    minHeight: height
                },
                //            data: {label: name},
                position: { x: x, y: y },
                style: {
                    width: width,
                    minHeight: height
                },
                parentNode: parent,
                extent: 'parent',
            }
            nodeLevels.current[comp.name] = row;
        } else {
            console.log("Adding non-subcomponent ", comp)
            newNode = {
                id: comp.name,
                connectable: false,
                type: 'component',
                //            dragHandle: '.drag-handle',
                data: {
                    name: comp.name, ctype: comp.type, version: comp.version, properties: comp.properties, shownProperties: '',
                    minHeight: height
                },
                //            data: {label: name},
                position: { x: x, y: y },
                style: {
                    width: width,
                    minHeight: height
                },
                //            position: { x: 10, y: 10 },
            }
            nodeLevels.current[comp.name] = row;
        }
        addNodeId(comp.name);
        // set parent node status to false
        isParentNode.current[comp.name] = false;
        childrenNodes.current[comp.name] = [];
        // reveal properties if showProperties is visible
        if (propertiesVisibleRef.current) {
            newNode = revealProperties(newNode);
        }
        setNodes((els) => els.concat(newNode));
        return true;
    }

    /**
    * Add an edge to the React Flow graph.
    * @param {string} id - the ID of the edge to add 
    * @param {string} source - the name of the component that the 
    * edge starts at.
    * @param {string} target - the name of the component that the
    * edge ends at. 
    * @param {bool} subcomponent - indicates whether this is a
    * sub/supercomponent.
    * @returns Return whether the edge was successfully added.
    */
    const addEdge = (id, source, target, subcomponent) => {
        var e_style, e_arrow, e_type;

        // catch it
        if (edgeIds.current[id]) {
            return false;
        }

        if (subcomponent) {
            e_style = { stroke: '#555555', strokeWidth: 3, strokeDashArray: '2,2', zIndex: '2000' };
            e_arrow = 'arrowclosed';
            e_type = 'straight';
        } else {
            e_style = { stroke: '#555555', strokeWidth: 1, zIndex: '2000' };
            e_arrow = null;
            e_type = 'smoothstep';
        }

        let newEdge = {
            id: id,
            source: source,
            target: target,
            type: e_type,
            style: e_style,
            arrowHeadType: e_arrow
        }
        addEdgeId(id);
        setEdges((edges) => edges.concat(newEdge));

        return true;
    }

    /**
    * Removes a React Flow edge given the ID.
    * @param {string} id - The React Flow ID of the element to remove.
    */
    const removeEdge = (id) => {
        let index = edges.findIndex(
            (els) => els.id === id
        );
        if (index > -1) {
            setEdges((els) => els.splice(index, 1));
        }
        edgeIds.current[id] = false;
    }

    /**
    * Remove all nodes and edges from the React Flow graph.
    */
    const removeAllElements = () => {
        setNodes([]);
        nodeIds.current = {};
        setEdges([]);
        edgeIds.current = {};
        expandedNodes.current = {};
        isParentNode.current = {}
        childrenNodes.current = {};
    }

    /**
    * Visualize the component, and branch out and visualize nearby components
    * using breadth first search.
    */
    async function visualizeComponent() {

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
        console.log("addComponent5")
        addComponent(
            component,
            350,
            100,
            0
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

        queue.push({ name: component.name, currDepth: 0 });

        if (depth == 0) {
            return;
        }

        // funny breadth first search
        while (queueFrontIndex < queue.length) {

            // so you don't add nodes that you've already visited
            visited[queue[queueFrontIndex].name] = true;

            let newComponents = await expandConnections(
                queue[queueFrontIndex].name,
                time.current,
            );

            if (queue[queueFrontIndex].currDepth + 1 < depth) {
                for (let thisComp of newComponents) {
                    if (!visited[thisComp.name]) {
                        queue.push({
                            name: thisComp.name,
                            currDepth: queue[queueFrontIndex].currDepth + 1
                        })
                    }
                }
            }
            queueFrontIndex++;

            // toggleLayout();
        }

    }

    /**
    * Layout the elements in the React Flow visuzalization using Dagre.
    */
    const onLayout = useCallback(
        (direction) => {
            // Define the subset of nodes to be laid out (you can adjust this as needed)
            // const subsetOfNodes = nodes.slice(0, 2);
            const subsetOfNodes = nodes;
            // Get the nodes to be laid out
            const layouted = getLayoutedElements(subsetOfNodes, nodes, edges, { direction });

            setNodes([...layouted.nodes]);
            setEdges([...layouted.edges]);

            window.requestAnimationFrame(() => {
                fitView();
            });
        },
        [nodes, edges]
    );


    /**
    * A MUI component representing a component node.
    * @param {*} data - data for the React Flow component.
    * Really only need data.name from here.
    */
    function ComponentNode({ data, style }) {
        return (
            <ThemeProvider theme={theme}>
                <Handle
                    type="target"
                    position="top"
                    style={{ background: 'none', border: 'none' }}
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
                    <Grid
                        container
                        justifyContent="center"
                        // alignItems="center"
                        style={{
                            height: '100%',
                            minHeight: data.minHeight
                        }}
                    >
                        <Grid item xs={9}>
                            {/* <Typography
                    variant="body2"
                > */}
                            <Link to={`/component/${data.name}`}>
                                {data.name}
                            </Link>
                            <br />{data.ctype.name}
                            <br />
                            {propertiesVisible ? <div><p>hey</p></div> : ''}
                            {data.shownProperties ? data.shownProperties.map(([propertyName, values, unit]) => (
                                <div key={propertyName}>
                                    <p>
                                        <u>{propertyName}:</u> {values.join(', ')} {unit}
                                    </p>
                                </div>
                            ))
                                : ''}
                            {/* </Typography> */}
                        </Grid>
                        <Grid item>
                            <ExpandConnectionsButton
                                onClick={() => {
                                    expandConnections(data.name, time.current);
                                }
                                }
                            />
                        </Grid>
                    </Grid>
                </ComponentNodeWrapper>
            </ThemeProvider>

        )
    }

    // Resize the parent and adjust subcomponents based on the heights of each node
    async function formatParent(parent, justAdded) {
        if (parent && childrenNodes.current[parent]) {
            const children = childrenNodes.current[parent];
            const parentHeight = flowInstance.getNode(parent).height;
            var newHeight = 0;

            // get the height of the tallest subcomponent
            for (var i = 0; i < children.length; i++) {
                let child = flowInstance.getNode(children[i]);
                newHeight = justAdded ? Math.max(newHeight, parentHeight + child.height) :
                    Math.max(newHeight, parentHeight + child.height - 50);
            }
            flowInstance.setNodes((nodes) => nodes.map((node) => {
                if (newHeight && node.id === parent) {
                    return ({
                        ...node,
                        style: { ...node.style, height: newHeight },
                    });
                }
                else if (children.includes(node.id) && newHeight && node.height) {
                    return ({
                        ...node,
                        position: { x: node.position.x, y: newHeight - node.height }
                    });
                }
                // handle the case where nodes need to be moved
                else if ((nodeLevels.current[node.id] >= nodeLevels.current[parent]) && parentHeight && newHeight) {
                    return ({
                        ...node,
                        position: { x: node.position.x, y: node.position.y + newHeight - parentHeight }
                    })
                }
                else {
                    return node;
                }
            }));
        }
    }


    // waits for the parent to be updated properly before being called
    useEffect(() => {
        formatParent(addedParent, true)
    }, [addedParent])

    useEffect(() => {
        formatParent(expandedSupercomponent, false)
    }, [expandedSupercomponent])


    /**
    * Expand and visualize the components that the component with name "name"
    * is connected to at time "time"
    * @param {string} name - name of the component to check connections with 
    * @param {int} time - time to check components at
    * @returns A Promise, which, when resolved, returns the array of the names
    * of the components added.
    */
    async function expandNodes(name, time) {

        if (expandedNodes.current[name]) {
            // If expanded, return immediately
            return ([]);
        }

        let input = `/api/get_connections`;
        input += `?name=${name}`;
        input += `&time=${time}`;

        /**
        * build up an array of the names of components actually added (does not
        * consider components that were already in the visualization)
        */
        let componentsAdded = [];

        let nodeHeight = 50;

        if (flowInstance.getNode(name)) {
            nodeHeight = flowInstance.getNode(name).height ? flowInstance.getNode(name).height : nodeHeight;
        }

        return new Promise(
            resolve => {
                fetch(input).then(
                    res => res.json()
                ).then(data => {
                    console.log("Expanding Connections", name)
                    let subcomponents = [];
                    let parent;
                    let curr
                    let edges = [];
                    let vertPadding = 50;
                    for (const edge of data.result) {

                        // find other node from curr
                        let other = (name === edge.inVertex.name) ?
                            edge.outVertex : edge.inVertex;

                        // set curr node
                        if (!curr) {
                            curr = (name === edge.inVertex.name) ?
                                edge.inVertex : edge.outVertex;
                        }

                        if (edge.subcomponent) {
                            if (other.name === edge.outVertex.name) {
                                // other is subcomponent of curr
                                subcomponents.push(other);
                            } else {
                                // other is the parent of curr
                                parent = other;
                            }
                        } else {
                            if (!edgeIds.current[edge.id]) {
                                // if edge is not already in graph
                                // add normal edge to this component
                                edges.push(edge)
                            }
                        }
                    }

                    // expand to add child nodes to parent
                    if (expandedNodes.current[name] === true) {
                        let subLastAdded = { x: -nodeWidth, y: 120 - nodeHeight }
                        for (const sub of subcomponents) {
                            // debugger;
                            console.log("addComponent1");
                            let subAdded = addComponent(sub, subLastAdded.x + nodeWidth + 10, subLastAdded.y,
                                nodeLevels.current[curr.name] + 1, true, curr.name);

                            if (subAdded) {
                                isParentNode.current[curr.name] = true;
                                componentsAdded.push(sub)
                                subLastAdded.x += nodeWidth + 10;

                                // set sub as a child of curr
                                childrenNodes.current[curr.name] = [...childrenNodes.current[curr.name], sub.name]
                            } else {
                                // subcomponent exists -> set as child of curr

                                setNodes((nodes) => nodes.map((node) => {
                                    if (node.id === sub.name) {

                                        return ({
                                            ...node,
                                            data: { ...node.data, label: node.id, },
                                            position: {
                                                x: subLastAdded.x + nodeWidth + 10,
                                                y: subLastAdded.y
                                            },
                                            parentNode: curr.name,
                                            extent: 'parent'
                                        });
                                    } else {
                                        return node;
                                    }
                                }));
                                subLastAdded.x += nodeWidth + 10;
                            }
                        }
                        resolve(componentsAdded);
                        return;
                    }

                    if (parent) {
                        // update size based on # of SC curr
                        // add 1 more "row"
                        let newHeight = (subcomponents.length > 0) ? nodeHeight * 2 : 0;
                        let newWidth = (subcomponents.length > 0) ? subcomponents.length * (nodeWidth + 20) :
                            nodeWidth;
                        let parentFound = false;
                        setNodes((nodes) => nodes.map((node) => {
                            if (node.id === parent.name) {
                                const maxHeight = node.style.height + newHeight;
                                const maxWidth = Math.max(node.style.width, newWidth);

                                parentFound = true
                                return ({
                                    ...node,
                                    data: { ...node.data, label: node.id, },
                                    style: {
                                        width: maxWidth,
                                        height: maxHeight,
                                    }
                                });
                            } else {
                                return node;
                            }
                        }));
                        if (!parentFound) {

                            // ensure newHeight non-zero if creating parent for first time
                            newHeight = (newHeight === 0) ? nodeHeight : newHeight;

                            // create parent node
                            console.log("addComponent2")
                            let current_node = flowInstance.getNode(curr.name);
                            let added = addComponent(parent, current_node.position.x, current_node.position.y,
                                nodeLevels.current[curr.name], false, null, newWidth * 1.5 + 'px');

                            if (added) {
                                componentsAdded.push(parent);

                                formatRowsHorizontal(nodeLevels.current[curr.name],
                                    newWidth * 1.5 - current_node.width, current_node.position.x);

                                // point curr to parent
                                setNodes((nodes) => nodes.map((node) => {
                                    if (node.id === curr.name) {
                                        return ({
                                            ...node,
                                            data: { ...node.data, label: node.id },
                                            parentNode: parent.name,
                                            extent: 'parent',
                                            position: {
                                                x: 10,
                                                y: nodeHeight
                                            },
                                        });
                                    }
                                    else {
                                        return node;
                                    }
                                }));
                            }
                        }
                        // set parent node status to true
                        isParentNode.current[parent.name] = true;

                        // set curr as a child of parent
                        childrenNodes.current[parent.name] = [...childrenNodes.current[parent.name], curr.name];

                        if (!nodeLevels.current[curr.name]) {
                            // add to node levels to keep track of level
                            nodeLevels.current[curr.name] = nodeLevels.current[parent.name];
                        }
                    }

                    if (subcomponents.length > 0) {
                        let subLastAdded = { x: -nodeWidth, y: nodeHeight }
                        let maxSubHeight = nodeHeight;

                        for (const sub of subcomponents) {
                            console.log("addComponent3")
                            let subAdded = addComponent(sub, subLastAdded.x + nodeWidth + 10, subLastAdded.y,
                                nodeLevels.current[curr.name], true, curr.name);
                            if (subAdded) {
                                isParentNode.current[curr.name] = true;
                                componentsAdded.push(sub)
                                subLastAdded.x += nodeWidth + 10;

                                // set sub as a child of curr
                                childrenNodes.current[curr.name] = [...childrenNodes.current[curr.name], sub.name];
                                // Set node level
                                nodeLevels.current[sub.name] = nodeLevels.current[curr.name];

                            } else {
                                subLastAdded.x += nodeWidth + 10;
                                // subcomponent exists -> set as child of curr
                                setNodes((nodes) => nodes.map((node) => {
                                    if (node.id === sub.name) {
                                        maxSubHeight = Math.max(maxSubHeight, node.style.height)
                                        return ({
                                            ...node,
                                            data: { ...node.data, label: node.id, },
                                            position: {
                                                x: subLastAdded.x,
                                                y: subLastAdded.y
                                            }
                                        });
                                    } else {
                                        return node;
                                    }
                                }));
                                nodeLevels.current[sub.name] = nodeLevels.current[curr.name];
                            }
                        }

                        // update current size
                        const newWidth = subcomponents.length * (nodeWidth + 20);

                        setNodes((nodes) => nodes.map((node) => {
                            if (node.id === curr.name) {
                                return ({
                                    ...node,
                                    data: { ...node.data, label: node.id },
                                    style: {
                                        width: newWidth,
                                        height: node.style.height
                                    }
                                });
                            } else {
                                return node;
                            }
                        }));
                        let current_node = flowInstance.getNode(curr.name)
                        if (newWidth > current_node.width) {
                            formatRowsHorizontal(nodeLevels.current[curr.name],
                                newWidth - current_node.width, current_node.position.x);
                        }
                        resolve(componentsAdded);
                    }

                    // absolute node coordinates, even if it's inside another component
                    let node_coords = flowInstance.getNode(curr.name).positionAbsolute;
                    console.log("node coords", node_coords)
                    let curr_x = node_coords.x;
                    let rowNumber = nodeLevels.current[curr.name] + 1;

                    let curr_y = node_coords.y;

                    // Get starting coordinates of child component:
                    curr_x -= Math.floor((edges.length - 1) / 2) * (nodeWidth + 30);
                    if (edges.length % 2 == 0) {
                        curr_x -= (nodeWidth + 30) / 2;
                    }
                    curr_x = getAvailableSpace(rowNumber, curr_x, edges.length * (nodeWidth + 30) - 30, 30);
                    let num_added = 0;
                    for (let i = 0; i < edges.length; i++) {
                        let edge = edges[i]
                        // find other node from curr
                        let other = (name === edge.inVertex.name) ?
                            edge.outVertex : edge.inVertex;
                        let added = addComponent(other, curr_x, curr_y + nodeHeight + vertPadding,
                            rowNumber);
                        curr_x += nodeWidth + 30;
                        addEdge(
                            edge.id,
                            edge.outVertex.name,
                            edge.inVertex.name,
                            edge.subcomponent
                        );
                        if (added) {
                            componentsAdded.push(other);
                            num_added += 1;
                        }
                    }
                    if (componentsAdded.length > 0 && !urlSet) {
                        setExpanded((prev) => [...prev, name]);
                    }
                    expandedNodes.current[name] = true;
                    sortNodes();
                    resolve(componentsAdded);
                });
            }
        )
    }

    async function expandConnections(name, time) {
        return new Promise((resolve) => {
            expandNodes(name, time).then(
                (addedNodes) => {
                    // Resizing and re-positioning nodes is done after the 
                    // promise is resolved, because we need to wait for React Flow to finish
                    // its calculations first. (this still doesn't work perfecty!)
                    for (var i = 0; i < addedNodes.length; i++) {
                        // if one of the added components is a parent node
                        if (isParentNode.current[addedNodes[i].name]) {
                            setAddedParent(addedNodes[i].name);
                        }
                    }
                    if (isParentNode.current[name]) {
                        if (componentRef.current.name === name) {
                            setAddedParent(name);
                        }
                        // update state if expanded node is a supercomponent
                        else {
                            setExpandedSupercomponent(name);
                        }
                    }
                    resolve(addedNodes);
                }
            );
        })
    }

    /**
    * "Pushes" down rows in the graph. 
    * @param {number} startingRow - first row to push down. All rows beneath it will be pushed down as well.
    * @param {number} height - the amount by which to push down the rows.
    * @param {Array<string>} ignoreNodes - nodes to ignore during the reformatting. 
    */
    async function formatRowsVertical(startingRow, height, ignoreNodes = null) {
        setNodes((nodes) => nodes.map((node) => {
            if ((nodeLevels.current[node.id]) && (nodeLevels.current[node.id] >= startingRow)
                && (ignoreNodes.indexOf(node.id) === -1)) {
                return {
                    ...node,
                    position: { x: node.position.x, y: node.position.y + height }
                };
            }
            else {
                return node;
            }
        }));
    }


    /**
    * Moves nodes in a row and all their descendants to the right
    * @param {number} row - row containing the nodes we want to move
    * @param {number} x - the amount by which to move the nodes
    * @param {number} startingX - elements to the right of this x-value will be pushed right
    */
    async function formatRowsHorizontal(row, x, startingX) {
        const nodesList = flowInstance.getNodes();
        let pushed = [];        // array that will store nodes to push
        for (var i = 0; i < nodesList.length; i++) {
            var node = nodesList[i];
            if ((nodeLevels.current[node.id] == row) && (node.position.x > startingX)
                && (!node.parentNode)) {
                pushed = pushed.concat(getDescendants(node.id));
            }
        }

        setNodes((nodes) => nodes.map((node) => {
            if (pushed.includes(node.id)) {
                return {
                    ...node,
                    position: { x: node.position.x + x, y: node.position.y }
                };
            }
            else {
                return node;
            }
        }));
    }


    /**
    * Given a node x, returns an array containing the ids of node x
    * and all the nodes connected to x that appear *below* x in the visualisation graph.
    * @param {string} node - id of starting node
    * @returns an array of node ids as described above
    */
    function getDescendants(node) {
        let nodesArray = [];
        nodesArray.push(node);      // add node to array
        for (var i = 0; i < flowInstance.getEdges().length; i++) {
            const edge = flowInstance.getEdges()[i];
            if (edge.source == node) {
                if (nodeLevels.current[edge.target] >= nodeLevels.current[node]) {
                    nodesArray = nodesArray.concat(getDescendants(edge.target));
                }
            }
            if (edge.target == node) {
                if (nodeLevels.current[edge.source] >= nodeLevels.current[node]) {
                    nodesArray = nodesArray.concat(getDescendants(edge.source));
                }
            }
        }

        return nodesArray;
    }


    /**
    * Finds the "best" space to fit elements, given a width and an initial x-value
    * @param {number} rowNumber - rownumber of the element to be added
    * @param {number} x - x-coordinate of "block" to be added
    * @param {number} width - the width of the block to be added
    * @param {number} padding - the padding between blocks
    * returns an x-coordinate for the block. 
    */
    function getAvailableSpace(rowNumber, x, width, padding) {
        // Get all (non-subcomponent) nodes inside this row
        const nodeList = flowInstance.getNodes();
        let rowNodes = [];
        for (var j = 0; j < nodeList.length; j++) {
            const currNode = nodeList[j];
            if ((nodeLevels.current[currNode.id] == rowNumber) && (!currNode.parentNode)) {
                rowNodes.push(currNode);
            }
        }
        if (rowNodes.length == 0) {      // row is empty
            return x;
        }

        // sort the nodes by their x position, increasing (left to right):
        rowNodes.sort((a, b) => a.position.x - b.position.x)
        const numNodes = rowNodes.length;

        if (x <= (rowNodes[0].position.x)) {
            // case where we want to put the new nodes to the left of everything
            // first check if it fits
            if (x + width + padding <= rowNodes[0].position.x) {
                return x;
            }
            // otherwise return the new x
            return rowNodes[0].position.x - width - padding;
        }

        else if (x >= rowNodes[numNodes - 1].position.x) {
            const minX = rowNodes[numNodes - 1].position.x + rowNodes[numNodes - 1].width + padding;
            return x >= minX ? x : minX;
        }

        // otherwise, loop until the closest space is found
        for (var i = 0; i < numNodes - 1; i++) {
            // loop to find closest gap to the "target" x coordinate
            if ((x >= rowNodes[i].position.x) &&
                (x <= rowNodes[i + 1].position.x)) {
                var fit = fitObjectInGap(rowNodes[i].position.x + rowNodes[i].width,
                    rowNodes[i + 1].position.x, width, x, padding);
                if (fit) {
                    return fit;
                }
                else {      // it doesn't fit
                    // need to find next *closest* gap where it fits
                    var j = i + 1;      // to iterate through "gaps" to the right
                    var k = i - 1;      // to iterate through "gaps" to the left
                    while ((j < numNodes - 1) || (k >= 0)) {
                        if (j < numNodes - 1) {
                            fit = fitObjectInGap(rowNodes[j].position.x + rowNodes[j].width,
                                rowNodes[j + 1].position.x, width, x, padding);
                            if (fit) {
                                return fit;
                            }
                        }
                        if (k >= 0) {
                            fit = fitObjectInGap(rowNodes[k].position.x + rowNodes[k].width,
                                rowNodes[k + 1].position.x, width, x, padding);
                            if (fit) {
                                return fit;
                            }
                        }
                        // increment variables
                        j += 1;
                        k -= 1;
                    }
                }
            }
        }

        // shouldn't reach here, but if it happens then just put the new object on the far right
        return rowNodes[numNodes - 1].position.x + rowNodes[numNodes - 1].width + padding;
    }


    // fit object in between start x-coordinate and end x-coordinate
    // return x-coordinate if it fits and null if it doesn't
    // x in parameter is starting x
    function fitObjectInGap(start, end, width, x, padding) {
        if (end - start >= width + padding * 2) {
            // it fits
            if ((x - padding >= start) && (x + width + padding <= end)) {
                // it doesn't need to be moved
                return x;
            }
            // move the object so it fits
            else if (x < start) {
                return start + padding;
            }
            return end - width - padding;
        }
        // it doesn't fit
        return null;
    }

    const nodeTypes = useMemo(
        () => ({ component: ComponentNode }), []
    );

    window.addEventListener("error", (e) => {
        if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || e.message === 'ResizeObserver loop limit exceeded') {
            //console.log("Oh, yeah × 2!!!!");
            e.stopImmediatePropagation();
        }
    });

    return (
        <>
            <Authenticator />
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
                                onClick={() => {
                                    // clear URL
                                    // clear components + states
                                    // set new component
                                    setExpanded([]);
                                    removeAllElements();
                                    setReloadComponent(!reloadComponent);
                                    // visualizeComponent();
                                    setAddedParent(null);
                                    setExpandedSupercomponent(null);
                                }}
                                disabled={component === undefined}
                            >
                                Visualize
                            </Button>


                            <Button
                                variant='contained'
                                onClick={() => {
                                    setPropertiesVisible(!propertiesVisible);
                                }}
                                disabled={nodes && nodes.length === 0}
                            >
                                {propertiesVisible ? 'Hide' : 'Show'} properties
                            </Button>

                        </Stack>
                    </OptionsPanel>
                </Grid>

                <Grid item>
                    <VisualizerPanel>
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            onNodesChange={onNodesChange}
                            onEdgesChange={onEdgesChange}
                            nodeTypes={nodeTypes}
                            nodesConnectable={false}
                        >
                            <Background
                                variant="dots"
                                gap={12}
                                size={0.5}
                            />
                            <Controls>
                                <ControlButton
                                    onClick={() => { onLayout() }}
                                >
                                    <SortIcon />
                                </ControlButton>
                            </Controls>
                        </ReactFlow>
                    </VisualizerPanel>
                </Grid>

            </Grid>
        </>
    )
}

export default function ComponentconnectionVisualizer() {
    return (
        <ReactFlowProvider>
            <ComponentConnectionsPanel />
        </ReactFlowProvider>
    )
}