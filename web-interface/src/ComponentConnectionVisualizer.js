import React, { useState, useEffect, useRef, useCallback,
    useMemo } from 'react';
import ReactFlow, { 
Controls, Background, Handle, ControlButton, isNode, MarkerType,
applyNodeChanges, applyEdgeChanges, ReactFlowProvider, useReactFlow, Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import styled from '@mui/material/styles/styled';
import createTheme from '@mui/material/styles/createTheme';
import { Link, useSearchParams } from "react-router-dom";
import './custom.css'

import Dagre from 'dagre';

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
//import DragHandleRoundedIcon from '@mui/icons-material/DragHandleRounded';
import SortIcon from '@mui/icons-material/Sort';

import ComponentAutocomplete from './ComponentAutocomplete.js';
import { ThemeProvider } from '@emotion/react';

import { unixTimeToISOString } from './utility/utility.js';
import Authenticator from './components/Authenticator.js';

window.addEventListener("error", (e) => {
if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || e.message === 'ResizeObserver loop limit exceeded') {
//console.log("Oh, yeah × 22!!!!");
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
* Styled component used as the drag handle for the component nodes in the
* visualization.
*/
/*const ComponentNodeDragHandle = styled((props) => (
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

}));*/

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
// const dagreGraph = new dagre.graphlib.Graph();
// dagreGraph.setDefaultEdgeLabel(() => ({}));
const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));


// TODO: Probably don't hardcode this.
// let nodeWidth = 250, nodeHeight = 50;
let nodeWidth = 250;

/**
* Lays out the nodes of the graph visualization in a top-to-bottom fashion.
* 
* @param {Array} elements - The list of nodes and edges for the React Flow
* visualization
* @returns A list of the nodes and edges with proper positioning.
//  */
// const getLayoutedElements = (elements) => {
//     // https://reactflow.dev/examples/layouting/

//     /**
//      * The direction of the layout is top to bottom. This can be changed
//      * by hardcoding it and changing it or by adding a parameter.
//      */
//     const direction = 'TB';

//     dagreGraph.setGraph({ rankdir: direction });

//     // set up the dagre graph
//     elements.forEach((el) => {
//         if (isNode(el)) {
//             dagreGraph.setNode(el.id, { width: nodeWidth, height: nodeHeight });
//         } else {
//             dagreGraph.setEdge(el.source, el.target);
//         }
//     });

//     // do layout
//     dagre.layout(dagreGraph);

//     // return the layouted elements
//     return elements.map((el) => {
//       if (isNode(el)) {
//         const nodeWithPosition = dagreGraph.node(el.id);
//         el.targetPosition = 'top';
//         el.sourcePosition = 'bottom';

//         // unfortunately we need this little hack to pass a slightly different 
//         // position to notify react flow about the change. 
//         // Moreover we are shifting the dagre node position 
//         // (anchor=center center) to the top left so it matches the 
//         // react flow node anchor point (top left).
//         el.position = {
//           x: nodeWithPosition.x - nodeWidth / 2 + Math.random() / 1000,
//           y: nodeWithPosition.y - nodeHeight / 2,
//         };
//       }

//       return el;
//     });
// };
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
* Get node by ID
*/
const getNode = (nodes, id) => {
return nodes.find((node) => node.id === id);
}

/**
* The MUI component that represents the visualizer for components along with
* an option panel for changing the date when the component's connections
* are considered, the component that is considered, and the depth of the
* "branching" (when you press visualize, you have the option of branching out) 
* @returns 
*/
function ComponentConnectionsPanel() {

// https://reactrouter.com/docs/en/v6/api#usesearchparams
const [searchParams, setSearchParams] = useSearchParams();

// the React Flow nodes to be used in the visualization
const [nodes, setNodes] = useState([]);

// a dictionary to store whether each node is a parent or not
const isParentNode = useRef({});

// a dictionary to store the children of a given node
const childrenNodes = useRef({});

// from https://reactflow.dev/docs/guides/layouting/
const { fitView } = useReactFlow();

// store position
// TODO: remove this?
const lastAdded = useRef({x: 350, y: 100}); 

// a dictionary that maps "rows"/levels in the graph to occupied blocks. this is for layouting
// TODO: come up with more name  
const rowsOccupied = useRef({});

// store sub component position
// const [subLastAdded, setSubLastAdded] = useState({x: -nodeWidth, y: 120 - nodeHeight})

// a dictionary that will store the React Flow IDs of the nodes used
const nodeIds = useRef({});

// a dictionary that maps the node IDs to their coordinates
const nodeCoords = useRef({});

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

// "next" component selected by the user, if any
// not sure if this is the best way to do this
const selectedComponent = useRef(undefined);

// actual depth of the BFS search
const [depth, setDepth] = useState(0);

// value that the depth-input will show
const [depthInputValue, setDepthInputValue] = useState(0);

const onNodesChange = useCallback((changes) => setNodes((nds) =>
                          applyNodeChanges(changes, nds)), []);
const onEdgesChange = useCallback((changes) => setEdges((eds) => 
                        applyEdgeChanges(changes, eds)), [] );

// to store calls to expandConnections
const [expanded, setExpanded] = useState([]);

// to track whether url component is set
const [urlSet, setUrlSet] = useState(false);

const [propertiesVisible, setPropertiesVisible] = useState(false);
const propertiesVisibleRef = useRef();
propertiesVisibleRef.current = propertiesVisible;

/**
* The useRef hook is used as doing
* setToggleLayoutBool(!toggleLayoutBool) will use the old value of
* toggleLayoutBool before the state has been refreshed, so it won't
* actually refreshed. However, using useRef like
* "toggleLayoutBoolRef.current = !toggleLayoutBoolRef.current" will
* instantly update the value of oggleLayoutBoolRef.current without
* waiting for a state change.
*/
/*    const toggleLayoutBoolRef = useRef(false);
const [toggleLayoutBool, setToggleLayoutBool] = useState(false);
const toggleLayout = () => {
toggleLayoutBoolRef.current = !toggleLayoutBoolRef.current; 
setToggleLayoutBool(toggleLayoutBoolRef.current) 
};*/

// the unix time in MILLISECONDS. useRef so it can be instantly changed.
const enteredTime = useRef(Math.floor(Date.now()));

// the unix time in SECONDS. useRef so it can be instantly changed.
const time = useRef(Math.floor(Date.now() / 1000));

// the default position of nodes in the visualization.
const defaultViewport = {x: 0, y: 0};

const [reloadComponent, setReloadComponent] = useState(false);

// React flow instance to access internal state (e.g., internal node properties like height)
const flowInstance = useReactFlow();

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
}, [component]);

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

    // TODO: remove
    console.log("INITIALCMP?");
    console.log("INITIALCMP:", initialCmp);
    
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
    // TODO: this does not get run for when you re-visualise the same component if the 
    // expanded and depth do not change. So it fails to fetch the properties again. 
    // how to fix this?
    fetchData();
}, [window.location.hash, reloadComponent]);

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


function revealProperties(node) {
    console.log("reveal the", node.data.properties);
    // TODO: change component select from list to have properties
    if (node.data.properties && node.data.properties.length > 0) {
        console.log(node.data.properties)
        // console.log(unixTimeToISOString(node.data.properties[0].start.time * 1000))
        // console.log(unixTimeToISOString(node.data.properties[0].end.time * 1000))
        // console.log(unixTimeToISOString(enteredTime.current))
        const filteredProperties = node.data.properties.filter((property) => {
            // console.log(property.start.time * 1000 <= enteredTime.current)
            // console.log(enteredTime.current <= property.end.time * 1000)
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
            // shownProperties: node.data.properties[0].type.name + ':' + node.data.properties[0].values[0],
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
    // console.log(nodes)
    if (propertiesVisible) {
        // nodeHeight = 200;
        console.log('propertiesVisible')
        console.log(enteredTime.current)
        setNodes((nds) =>
        nds.map((node) => {
            return revealProperties(node);
        })
      );
    } else {
        // nodeHeight = 50;
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
function sortNodes () {
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
function addNodeCoords(id, coords, row, parent=null) {
    nodeCoords.current[id] = {
        coords: coords,
        row: row,
        parentCoords: null
    };
    if (parent !== null) {
        nodeCoords.current[id].parentCoords = nodeCoords.current[parent].coords;
        nodeCoords.current[id].row = nodeCoords.current[parent].row;
    }
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
function addComponent(comp, x, y, row, subcomponent=false, parent=null, width='250px', height='50px') {
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
      data: { name: comp.name, ctype: comp.type, version: comp.version, properties: comp.properties, shownProperties: '',  
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
  addNodeCoords(comp.name, {x: x, y: y}, row, parent)
} else {
  console.log("Adding non-subcomponent ", comp)
//   console.log("Coords: ", x, y)
  newNode = {
      id: comp.name,
      connectable: false,
      type: 'component',
  //            dragHandle: '.drag-handle',
      data: { name: comp.name, ctype: comp.type, version: comp.version, properties: comp.properties, shownProperties: '',
            minHeight: height  },
  //            data: {label: name},
      position: { x: x, y: y},
      style: {
        width: width,
        minHeight: height
      },
  //            position: { x: 10, y: 10 },
  }
  addNodeCoords(comp.name, {x: x, y: y}, row)
}
addNodeId(comp.name);
// set parent node status to false
isParentNode.current[comp.name] = false;
childrenNodes.current[comp.name] = [];
// reveal properties if showProperties is visible
console.log("PROPS VIS?", propertiesVisibleRef.current);
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
e_style = {stroke: '#555555', strokeWidth: 3, strokeDashArray: '2,2', zIndex: '2000'};
e_arrow = 'arrowclosed';
e_type = 'straight';
} else {
e_style = {stroke: '#555555', strokeWidth: 1, zIndex: '2000'};
e_arrow = null;
e_type = 'smoothstep';
}

let newEdge = {
id: id,
source: source,
target: target,
type: e_type,
style: e_style,
arrowHeadType: e_arrow,
        //    markerStart: {type: 'arrow', width: 100, height: 100, strokeWidth: 4, color: '#ffff00'}, //e_marker,
        //    markerEnd: {type: 'arrow', strokeWidth: 4, color: '#00ff00'}, //e_marker,
}
addEdgeId(id);
setEdges((edges) => edges.concat(newEdge));

return true;
}

/**
* Removes a React Flow node given the ID.
* @param {string} id - The React Flow ID of the element to remove.
*/
// const removeNode = (id) => {
//     console.log(nodes, nodeIds);
//     let index = nodes.findIndex(
//         (els) => els.id === id
//     );
//     console.log(index);
//     if (index > -1) {
//         setNodes((els) => els.splice(index, 1));
//     }
//     nodeIds.current[id] = false;
// }
const removeNode = (id) => {
setNodes((els) => els.filter((el) => el.id !== id));
nodeIds.current[id] = false;
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
rowsOccupied.current = {};
}

// /**
//  * Get node by ID
//  */
// const getNode = (nodes, id) => {
//     console.log(nodes, id);
//     return nodes.find((node) => node.id === id);
// }

const createSubcomponent = useCallback((parent, children) => {
const x = getNode(nodes, parent);
}, 
[nodes]
);

/**
* Visualize the component, and branch out and visualize nearby components
* using breadth first search.
*/
const visualizeComponent = async () => {

    if (component === undefined) {
        return;
    }
    removeAllElements();
    // TODO: remove this
    console.log("THE COMPONENT:", component);

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

    // this is the first component, so row/level = 0
    // 30 is horizontal padding between rows
    addOccupiedSpace(0, 350, 350 + nodeWidth, false);

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
//     const onLayout = useCallback(
//         () => {
// //            const layoutedElements = getLayoutedElements(elements);
// //            setElements(layoutedElements);
//         },
// //        [nodes] // Will this work?
//     );
const onLayout = useCallback(
(direction) => {
// Define the subset of nodes to be laid out (you can adjust this as needed)
// const subsetOfNodes = nodes.slice(0, 2);
const subsetOfNodes = nodes;
// console.log(subsetOfNodes)
// Get the nodes to be laid out
const layouted = getLayoutedElements(subsetOfNodes, nodes, edges, { direction });

setNodes([...layouted.nodes]);
setEdges([...layouted.edges]);
// console.log(layouted.nodes);

window.requestAnimationFrame(() => {
fitView();
});
},
[nodes, edges]
);

// layout the graph once the toggle layout bool has been toggled
//    useEffect(() => {
//        onLayout();
//    }, [toggleLayoutBool]);

// TODO: put properties information here

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
                    <br/>{data.ctype.name}
                    <br/>
                    {/* {data.shownProperties} */}
                    {/* {data.shownProperties.map(([propertyName, { values, unit }]) => (
                       <div key={propertyName}>`propertyName`</div> 
                    ))} */}
                    {/* {console.log(propertiesVisible)} */}
                    {/* {data.showProperties && data.properties[0] ?
                    data.properties[0].type.name + ':' + data.properties[0].values[0] */}
                    {/* :
                    ''
                    } */}
                    {/* {Object.entries(data.shownProperties).map(([propertyName, { values, unit }]) => (
                        <div key={propertyName}>
                        <p>
                            <strong>{propertyName}:</strong> {values.join(', ')} {unit}
                        </p>
                        </div>
                    ))} */}
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
                            console.log("NODES", flowInstance.getNodes());
                            expandConnections(data.name, time.current).then(
                                (addedNodes) => {
                                    // Updating the sizes and locations of nodes is done after the 
                                    // promise is resolved, because it needs to wait for React Flow to finish
                                    // its calculations first. 
                                    console.log("component", componentRef.current);
                                    console.log(isParentNode.current[data.name]);
                                    for (var i = 0; i < addedNodes.length; i++) {
                                        // for all added components, if one of them is 
                                        if (isParentNode.current[addedNodes[i].name]) {
                                            setAddedParent(addedNodes[i].name);
                                        }
                                    }
                                    if (isParentNode.current[data.name]) {      
                                        console.log(componentRef.current.name);
                                        if (componentRef.current.name === data.name) {
                                            setAddedParent(data.name);
                                            console.log(flowInstance.getNode(data.name))
                                        }

                                        // if expanded node is a supercomponent
                                        // update the state
                                        else {
                                            setExpandedSupercomponent(data.name)

                                        }
                                        
                                    }
                                    
                                }
                            );
                        }
                      }
                    />
            </Grid>
        </Grid>
    </ComponentNodeWrapper>
</ThemeProvider>

)
} 


useEffect(() => {
    // Resize the parent, if necessary
    console.log("added parent reached", addedParent);
    if (addedParent && childrenNodes.current[addedParent]) {
        console.log("PARENTE", flowInstance.getNode(addedParent));
        console.log(childrenNodes.current);
        console.log("chidlren", childrenNodes.current[addedParent]);
        const children = childrenNodes.current[addedParent];
        const parentHeight = flowInstance.getNode(addedParent).height;
        console.log(parentHeight);
        var newHeight = 0;

        // get the height of the tallest child
        for (var i = 0; i < children.length; i ++) {
            let child = flowInstance.getNode(children[i]);
            console.log(child);
            newHeight = Math.max(newHeight, parentHeight + child.height);
            console.log(child.height);
        }
        console.log("newheight", newHeight);

        flowInstance.setNodes((nodes) => nodes.map((node) => {
            if (node.id === addedParent) {
                return ({
                    ...node,
                    style: {...node.style, height: newHeight}, 
                });
            } 
            else if (children.includes(node.id)) {
                // adjust position of the subcomponent if necessary
                return ({
                    ...node,
                    position: {x: node.position.x, y: newHeight - node.height}
                });
            }
            else {
                return node;
            }
        }));
        }
}, [addedParent])


useEffect(() => {
    // format subcomponents, if we added some
    // remember higher y values are lower
    // this almost works but pass in the parent and then just loop through all its subcomponents
    // instead. fuck you
    console.log("expanded supercomponent reached", expandedSupercomponent)
    if (expandedSupercomponent) {   // so this doesn't run when addedSubcomponents is null
        // get parent height
        const superHeight = flowInstance.getNode(expandedSupercomponent).height;

        const subNames = childrenNodes.current[expandedSupercomponent];
        console.log("SUBCOMPOENNTS", subNames);
        
        flowInstance.setNodes((nodes) => nodes.map((node) => {
            if (subNames.includes(node.id)) {
                console.log("booh yah x2", node.id);
                // const newHeight = parentHeight - node.height;
                console.log(node);
                return ({
                    ...node,
                    position: {x: node.position.x, y: superHeight - node.height}
                });
            } else {
                return node;
            }
        }));
    }
    
}, [expandedSupercomponent])


/**
* Expand and visualize the components that the component with name "name"
* is connected to at time "time"
* @param {string} name - name of the component to check connections with 
* @param {int} time - time to check components at
* @param {node} expandedNode - the actual node object in the Flow representing the 
* component to check connections with
* @returns A Promise, which, when resolved, returns the array of the names
* of the components added.
*/
async function expandConnections(name, time) {
// setExpanded((prev) => [...prev, name]);
if (expandedNodes.current[name]) {
    // If expanded, return immediately
    return([]);
}

let input = `/api/get_connections`;
input += `?name=${name}`;
input += `&time=${time}`;

/**
* build up an array of the names of components actually added (does not
* consider components that were already in the visualization)
*/
let componentsAdded = [];

let nodeHeight = flowInstance.getNode(name).height;
console.log("NEW NODE HEIGHT", nodeHeight);

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
            let subLastAdded = {x: -nodeWidth, y: 120 - nodeHeight}
            // TODO: remove these?
            // let maxSubHeight = nodeHeight;
            for (const sub of subcomponents) {
                // console.log(sub.name + ':')
                // debugger;
                console.log("addComponent1");
                let subAdded = addComponent(sub, subLastAdded.x + nodeWidth + 10, subLastAdded.y, 
                                            nodeCoords.current[curr.name].row + 1, true, curr.name);

                // console.log(subAdded)
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

                            // maxSubHeight = Math.max(maxSubHeight, node.style.height)
                            return ({
                                ...node,
                                data: { ...node.data, label: node.id,},
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
                        data: { ...node.data, label: node.id,},
                        style : {
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
                let current_node = nodeCoords.current[curr.name];
                let added = addComponent(parent, current_node.coords.x, current_node.coords.y, 
                                        current_node.row, false, null, newWidth * 1.5 + 'px');

                if (added) {
                    // add occupied space
                    addOccupiedSpace(current_node.row, current_node.coords.x, 
                        current_node.coords.x + newWidth * 1.5, true);
                    componentsAdded.push(parent);
                    lastAdded.current.y += nodeHeight + 20;

                    console.log("current node", curr.name)

                    formatRowsVertical(nodeCoords.current[parent.name].row, nodeHeight, 
                        [parent.name, curr.name]);

                    // point curr to parent
                    setNodes((nodes) => nodes.map((node) => {
                        if (node.id === curr.name) {
                            return ({
                                ...node,
                                data: { ...node.data, label: node.id},
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

            if (!nodeCoords.current[curr.name]) {
                // add to node coords
                addNodeCoords(curr.name, {x: 10, y: nodeHeight}, nodeCoords.current[parent.name].row, parent.name);
            }
        }

        if (subcomponents.length > 0) {
            let subLastAdded = {x: -nodeWidth, y: nodeHeight}
            let maxSubHeight = nodeHeight;

            for (const sub of subcomponents) {
                // console.log(sub.name + ':')
                // debugger;
                console.log("addComponent3")
                let subAdded = addComponent(sub, subLastAdded.x + nodeWidth + 10, subLastAdded.y, 
                                            nodeCoords.current[curr.name].row, true, curr.name);
                if (subAdded) {
                    isParentNode.current[curr.name] = true;
                    componentsAdded.push(sub)
                    subLastAdded.x += nodeWidth + 10;

                    // set sub as a child of curr
                    childrenNodes.current[curr.name] = [...childrenNodes.current[curr.name], sub.name];
                    // update nodeCoords. curr is parent node of node to be added
                    addNodeCoords(sub.name, {x: subLastAdded.x, y: subLastAdded.y}, nodeCoords.current[curr.name].row, curr.name);

                } else {
                    subLastAdded.x += nodeWidth + 10;
                    // subcomponent exists -> set as child of curr
                    setNodes((nodes) => nodes.map((node) => {
                        if (node.id === sub.name) {
                            // console.log(node.id)
                            // console.log(sub.name)
                            // console.log(curr)
                            maxSubHeight = Math.max(maxSubHeight, node.style.height)
                            return ({
                                ...node,
                                data: { ...node.data, label: node.id,},
                                position: {
                                    x: subLastAdded.x,
                                    y: subLastAdded.y
                                },
                                // parentNode: curr,
                                // extent: 'parent'
                            });
                        } else {
                            return node;
                        }
                    }));
                    // update nodeCoords. curr is parent node of node to be added
                    addNodeCoords(sub.name, {x: subLastAdded.x, y: subLastAdded.y}, nodeCoords.current[curr.name].row, curr.name);
                }
            }
            
            // update current size
            const newWidth = subcomponents.length * (nodeWidth + 20);

            setNodes((nodes) => nodes.map((node) => {
                if (node.id === curr.name) {
                    return ({
                        ...node,
                        data: { ...node.data, label: node.id},
                        style: {
                            width: newWidth,
                            height: node.style.height
                        }
                    });
                } else {
                    return node;
                }
            }));
            let node_x = nodeCoords.current[curr.name].coords.x;
            if (newWidth > flowInstance.getNode(curr.name).width) {
                addOccupiedSpace(nodeCoords.current[curr.name].row, node_x, node_x + newWidth, true);
            }
            resolve(componentsAdded);
        }

        // absolute node coordinates, even if it's inside another component
        let node_coords = flowInstance.getNode(curr.name).positionAbsolute;
        let curr_x = node_coords.x;
        let rowNumber = nodeCoords.current[curr.name].row + 1;
        
        let curr_y = node_coords.y;
        
        // Get starting coordinates of child component:
        curr_x -= Math.floor((edges.length - 1)/2) * (nodeWidth + 30);
        if (edges.length % 2 == 0) {
            curr_x -= (nodeWidth + 30) / 2;
        }
        console.log("width", edges.length * (nodeWidth + 30) - 30);
        console.log("the current x", curr_x);
        curr_x = getAvailableSpace(rowNumber, curr_x, edges.length * (nodeWidth + 30) - 30, 30);
        console.log("the availbale", curr_x);
        let num_added = 0;
        for (let i=0; i < edges.length; i++) {
            let edge = edges[i]
            // find other node from curr
            let other = (name === edge.inVertex.name) ? 
                    edge.outVertex : edge.inVertex;
            console.log("addComponent4");
            console.log(other.name);
            let added = addComponent(other, curr_x, curr_y + nodeHeight + vertPadding, 
                                    rowNumber);
            addOccupiedSpace(rowNumber, curr_x, curr_x + nodeWidth, false);
            curr_x += nodeWidth + 30;
            addEdge(
                edge.id, 
                edge.outVertex.name, 
                edge.inVertex.name,
                edge.subcomponent
            );
            if (added) {
                componentsAdded.push(other);
                if (i == edges.length - 1) {
                    lastAdded.current.y += nodeHeight + vertPadding;
                }
                num_added += 1;
            }
        }
        // console.log(childrenNodes.current)

        // setSubLastAdded({...subLastAdded})
        if (componentsAdded.length > 0 && !urlSet) {
            setExpanded((prev) => [...prev, name]);
        }
        console.log(lastAdded.current);
        expandedNodes.current[name] = true;
        lastAdded.current = ({...lastAdded.current});
        sortNodes();
        // formatSubcomponents();
        resolve(componentsAdded);
        console.log("current node coords", nodeCoords.current);
        console.log("current row occupied", rowsOccupied.current);
    });
}
)
}


/**
* "Pushes" down rows in the graph. 
* @param {number} startingRow - first row to push down. All rows beneath it will be pushed down as well.
* @param {number} height - the amount by which to push down the rows.
* @param {Array<string>} ignoreNodes - nodes to ignore during the reformatting. 
*/
async function formatRowsVertical(startingRow, height, ignoreNodes = null) {
    setNodes((nodes) => nodes.map((node) => {
        if ((nodeCoords.current[node.id]) && (nodeCoords.current[node.id].row >= startingRow) 
            && (ignoreNodes.indexOf(node.id) === -1)) {
            return {
                ...node,
                position: {x: node.position.x, y: node.position.y + height}
            };
        }
        else {
            return node;
        }
        
    }));
}


/**
* Moves nodes in a row (and all their children) to the right 
* @param {number} row - row containing the nodes we want to move
* @param {number} x - the amount by which to move the nodes
* @param {number} startingX - 
*/
async function formatRowsHorizontal(row, x, startingX) {
    console.log("formatting horizontal")
    let toPush = [];        // array that will store nodes to push
    for (const node in nodeCoords.current) {
        if ((nodeCoords.current[node].row == row) && (nodeCoords.current[node].coords.x >= startingX) 
            && (!nodeCoords.current[node].parentCoords)) {
            toPush = toPush.concat(pushRight(node));
        }
    }

    setNodes((nodes) => nodes.map((node) => {
        if (toPush.includes(node.id)) {
            return {
                ...node,
                position: {x: node.position.x + x + 30, y: node.position.y}
            };
        }
        else {
            return node;
        }
    }));
}


function pushRight(node) {
    let nodesArray = [];
    nodesArray.push(node);      // add node to array
    for (var i = 0; i < flowInstance.getEdges().length; i ++) {
        const edge = flowInstance.getEdges()[i];
        if (edge.source == node) {
            if (nodeCoords.current[edge.target].row >= nodeCoords.current[node].row) {
                nodesArray = nodesArray.concat(pushRight(edge.target));
            }
        }
        if (edge.target == node) {
            if (nodeCoords.current[edge.source].row >= nodeCoords.current[node].row) {
                nodesArray = nodesArray.concat(pushRight(edge.source));
            }
        }
    }

    return nodesArray;
}


/**
* TODO: update this description for clarity
* Gets space in row number [rowNumber] closest to x-value [x] that will fit the object with width [width] 
* @param {number} rowNumber - rownumber
* @param {number} x - x-coordinate of leftmost edge of "block" to be added
* @param {number} width - the width of the block to be added
* @param {number} padding - the padding between blocks
* returns the x-coordinate of the new center of the block. 
*/
function getAvailableSpace(rowNumber, x, width, padding) {
    if (!rowsOccupied.current[rowNumber]) {      // row is empty
        return x;
    }
    let currentRowOccupied = rowsOccupied.current[rowNumber];
    let numBlocks = currentRowOccupied.length;
    width += padding * 2;
    if (x + width/2 <= (currentRowOccupied[0].start + currentRowOccupied[0].end) / 2) {
        // case where we want to put the new nodes to the left of everything
        // first check if it fits
        console.log("left of everything");
        // TODO: use math.min instead?
        if (x + width + padding <= currentRowOccupied[0].start) {
            // if it fits, just return x
            return x;
        }
        // otherwise return the new x
        console.log("returning current");
        console.log(currentRowOccupied[0].start, width);
        return currentRowOccupied[0].start - width + padding;
    }

    else if (x + width/2 >= (currentRowOccupied[numBlocks - 1].start + currentRowOccupied[numBlocks - 1].end) / 2) {
        // similar case for the very last one
        // TODO: use math.max instead?
        if (x >= currentRowOccupied[numBlocks - 1].end + padding) {
            return x;
        }
        // else 
        return currentRowOccupied[numBlocks - 1].end + padding;
        // return currentRowOccupied[numBlocks - 1].end;
    }

    // final else case
    // loop until the closest space is found
    console.log("final else case reached");
    let i = 0;
    let fit;
    while (currentRowOccupied[i + 1]) {
        if ((x + width/2 >= (currentRowOccupied[i].start + currentRowOccupied[i].end) / 2) && 
        (x + width/2 <= (currentRowOccupied[i+1].start + currentRowOccupied[i+1].end) / 2)) {
            // then the closest "gap" for the block will be between blocks i and i+1
            console.log("gap found", i);
            // first check if it fits:
            fit = fitObjectInGap(currentRowOccupied[i], currentRowOccupied[i+1], width, x, padding);
            if (fit) {    // if it fits we can return the value
                return fit;
            }
            // if it doesn't fit, then we need to find the closest gap that DOES fit
            // loop over offsets
            let offset = 1;
            while ((i - offset >= 0) && (i + offset < numBlocks - 1)) {
                if (x - currentRowOccupied[i-offset].start > currentRowOccupied[i-offset+1].end - x) {
                    // if x is closer to right block than left block, switch the order
                    offset = -offset;
                }
                fit = fitObjectInGap(currentRowOccupied[i-offset], currentRowOccupied[i-offset+1], width, x, padding);
                if (fit) {
                    return fit;
                }
                fit = fitObjectInGap(currentRowOccupied[i+offset], currentRowOccupied[i+offset+1], width, x, padding);
                if (fit) {
                    return fit;
                }
                // if no fit was found, update the offset
                offset = Math.abs(offset) + 1;
            }
            if (i - offset < 0) {
                while (i + offset < numBlocks - 1) {
                    if (x - currentRowOccupied[0].start <= currentRowOccupied[i+offset].end - x) {
                        return currentRowOccupied[0].start - width/2;
                    }
                    fit = fitObjectInGap(currentRowOccupied[i+offset], currentRowOccupied[i+offset+1], width, padding);
                    if (fit) {
                        return fit;
                    }
                    offset += 1;
                }
            }
            // otherwise i + offset >= numblocks - 1
            while (i - offset >= 0) {
                if (x - currentRowOccupied[i-offset].start >= currentRowOccupied[numBlocks-1].end - x) {
                    return currentRowOccupied[numBlocks-1].end + width/2;
                }
                fit = fitObjectInGap(currentRowOccupied[i-offset], currentRowOccupied[i-offset+1], width, padding);
                if (fit) {
                    return fit;
                }
                offset += 1;
            }
            // both sides are out of bounds, so we just stick it on whatever end is closer
            return currentRowOccupied[numBlocks-1].end + width/2;
        }
        i += 1;
    }
}


// todo: add description
// fit object in between block1 and block2
// return x-coordinate if it fits and null if it doesn't
// x in parameter is starting x
function fitObjectInGap(block1, block2, width, x, padding) {
    console.log(block2.start - block1.end);
    console.log(width);
    console.log(padding);
    if (block2.start - block1.end >= width) {
        // it fits 
        console.log("fitting object it fits");
        if ((x - padding >= block1.end) && (x + width - padding <= block2.start)) {
            // it doesn't need to be moved
            return x;
        }
        // if above not true, need to figure out which direction to move the block in and how far
        else if (x < block1.end) {
            return block1.end + padding;
        }
        return block2.start - width + padding;
    }
    // it doesn't fit
    return null;
}


// want to make sure these are in order
// assume that start, end don't overlap with an already occupied space, unless replace is true
// todo: slim this and the function above down?
async function addOccupiedSpace(rowNumber, start, end, replace) {
    let i = 0;
    let currentRowOccupied = rowsOccupied.current[rowNumber];
    if (!rowsOccupied.current[rowNumber]) {
        rowsOccupied.current[rowNumber] = [{start: start, end: end}];
    }
    else if (!replace) {
        while (i < currentRowOccupied.length - 1 && currentRowOccupied[i].start < end) {
            i += 1;
        }
        if (currentRowOccupied[i].start > start) {
            // i is the index we want to insert into
            currentRowOccupied.splice(i, 0, {start: start, end: end});
        }
        else {
            currentRowOccupied.splice(i + 1, 0, {start: start, end: end});
        }
    }
    else {      // replace is true, we're replacing an existing block
        i = 0;
        while (i < currentRowOccupied.length - 1) {
            if ((currentRowOccupied[i].end >= start) && (currentRowOccupied[i].start <= end)) {
                let dist = Math.abs(end - currentRowOccupied[i].end);
                let startingX = Math.min(currentRowOccupied[i].end, end);

                rowsOccupied.current[rowNumber][i].end = Math.max(currentRowOccupied[i].end, end);
                rowsOccupied.current[rowNumber][i].start = Math.min(currentRowOccupied[i].start, start);
                formatRowsHorizontal(rowNumber, dist, startingX);
                return;
            }
            else {
                i += 1;         // incremement i
            }
        }
    }
}

const nodeTypes = useMemo(
() => ({component: ComponentNode}), []
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
                    console.log("hi", val);
                    selectedComponent.current = val;
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
                onClick= {() => {
                    // clear URL
                    // clear components + states
                    // set new component
                    lastAdded.current = {x: 350, y: 100};
                    setExpanded([]);
                    removeAllElements();
                    setComponent(selectedComponent.current);
                    console.log("selected", selectedComponent.current, component);
                    setReloadComponent(!reloadComponent);
                    visualizeComponent();
                    setAddedParent(null);
                    setExpandedSupercomponent(null);
                }}
                disabled={selectedComponent === undefined}
            >
                Visualize
            </Button>


            <Button
                variant='contained'
                onClick={() =>
                    {setPropertiesVisible(!propertiesVisible);
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
                    onClick={() => {onLayout()}}
                >
                    <SortIcon />
                </ControlButton>
            </Controls>
            {/* <Panel position="top-right"> */}
                {/* <button onClick={() => setPropertiesVisible(!propertiesVisible)}>{propertiesVisible ? 'Hide' : 'Show'} properties</button> */}
                {/* layout buttons: doesn't work with subcomponents */}
                {/* <button onClick={() => onLayout('TB')}>vertical layout</button> */}
                {/* <button onClick={() => onLayout('LR')}>horizontal layout</button> */}
            {/* </Panel> */}
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
            <ComponentConnectionsPanel/>
        </ReactFlowProvider>
    )
}