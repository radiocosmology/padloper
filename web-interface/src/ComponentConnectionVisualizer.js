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

window.addEventListener("error", (e) => {
if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || e.message === 'ResizeObserver loop limit exceeded') {
console.log("Oh, yeah × 22!!!!");
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
const nodeWidth = 250, nodeHeight = 50;

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
console.log( { ...node, position: { x, y } })
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
console.log(nodes, id);
return nodes.find((node) => node.id === id);
}


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

// the React Flow nodes to be used in the visualization
const [nodes, setNodes] = useState([]);

// a dictionary to store whether each node is a parent or not
const isParentNode = useRef({});

// from https://reactflow.dev/docs/guides/layouting/
const { fitView } = useReactFlow();

// store position
const [lastAdded, setLastAdded] = useState({x: 350, y: 100})

// store sub component position
// const [subLastAdded, setSubLastAdded] = useState({x: -nodeWidth, y: 120 - nodeHeight})

// a dictionary that will store the React Flow IDs of the nodes used
const nodeIds = useRef({});

// the React Flow edges to be used in the visualization
const [edges, setEdges] = useState([]);

// a dictionary that will store the React Flow IDs of the edges used
const edgeIds = useRef({});

// which component is to be considered
const [component, setComponent] = useState(undefined);

// actual depth of the BFS search
const [depth, setDepth] = useState(0);

// value that the depth-input will show
const [depthInputValue, setDepthInputValue] = useState(0);

const onNodesChange = useCallback((changes) => setNodes((nds) =>
                          applyNodeChanges(changes, nds)), []);
const onEdgesChange = useCallback((changes) => setEdges((eds) => 
                        applyEdgeChanges(changes, eds)), [] );

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

/**
 * Sort the nodes so that "parent" nodes appear before "children"
 * nodes.
 */
function sortNodes () {
    setNodes((prevNodes) => {
        const sortedNodes = prevNodes.slice().sort((a, b) => {
          const isParentA = isParentNode.current[a.id];
          const isParentB = isParentNode.current[b.id];
    
          if (isParentA && !isParentB) {
            return -1;
          } else if (!isParentA && isParentB) {
            return 1;
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
* @returns A Boolean indicating whether the component 
* was successfully added.
*/
// TODO: need for async??
function addComponent(comp, x, y, subcomponent=false, parent=null, width='250px', height='50px') {
// catch it
if (nodeIds.current[comp.name]) {
  return false;
}
let newNode;
if (subcomponent) {
  newNode = {
      id: comp.name,
      connectable: false,
      type: 'component',
  //            dragHandle: '.drag-handle',
      data: { name: comp.name, ctype: comp.type, version: comp.version },
  //            data: {label: name},
      position: { x: x, y: y },
      style: {
        width: width,
        height: height
      },
      parentNode: parent,
      extent: 'parent',
  }
} else {
    console.log(width)
    console.log(height)
  newNode = {
      id: comp.name,
      connectable: false,
      type: 'component',
  //            dragHandle: '.drag-handle',
      data: { name: comp.name, ctype: comp.type, version: comp.version },
  //            data: {label: name},
      position: { x: x, y: y },
      style: {
        width: width,
        height: height
      },
  //            position: { x: 10, y: 10 },
  }
}
addNodeId(comp.name);
// set parent node status to false
isParentNode.current[comp.name] = false;
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
e_style = {stroke: '#555555', strokeWidth: 3, strokeDashArray: '2,2'};
e_arrow = 'arrowclosed';
e_type = 'straight';
} else {
e_style = {stroke: '#555555', strokeWidth: 1};
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
//            markerStart: {type: 'arrow', width: 100, height: 100, strokeWidth: 4, color: '#ffff00'}, //e_marker,
//            markerEnd: {type: 'arrow', strokeWidth: 4, color: '#00ff00'}, //e_marker,
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
console.log(nodes);
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
}

// /**
//  * Get node by ID
//  */
// const getNode = (nodes, id) => {
//     console.log(nodes, id);
//     return nodes.find((node) => node.id === id);
// }

const createSubcomponent = useCallback((parent, children) => {
console.log(parent, children);
const x = getNode(nodes, parent);
console.log(x);
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

// the time should be in seconds instead of milliseconds
time.current = Math.floor(enteredTime.current / 1000);

// add the component
/**
* TODO: Change the position of the component so it appears below the
* other components.
*/
addComponent(
component, 
350, 
100,
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

if (depth === 0) {
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

//            toggleLayout();
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
        <Grid
            container
            justifyContent="center"
            // alignItems="center"
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
                    <br/>{data.ctype.name}
                </Typography>
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

/**
* Expand and visualize the components that the component with name "name"
* is connected to at time "time"
* @param {string} name - name of the component to check connections with 
* @param {int} time - time to check components at
* @returns A Promise, which, when resolved, returns the array of the names
* of the components added.
*/
async function expandConnections(name, time) {

let input = `/api/get_connections`;
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

        let subcomponents = [];
        let parent;
        let curr
        let edges = [];
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
                // add normal edge to this component
                edges.push(edge)
            }
        }

        if (parent) {
            // update size based on # of SC curr
            // add 1 more "row"
            const newHeight = (subcomponents.length > 0) ? nodeHeight * 2 : 0;
            const newWidth = (subcomponents.length > 0) ? subcomponents.length * (nodeWidth + 20) :
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
                // create parent node
                console.log(newWidth)
                console.log(newHeight)
                let added = addComponent(parent, lastAdded.x, lastAdded.y + nodeHeight + 20, false, null, newWidth * 2 + 'px', newHeight * 2 + 'px');
                if (added) {
                    componentsAdded.push(parent);
                    lastAdded.y += nodeHeight + 20;

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
                                    y: 90 - nodeHeight
                                },
                            });
                        } else {
                            return node;
                        }
                    }));
                }
            }
            // set parent node status to true
            isParentNode.current[parent.name] = true;

            
        }

        if (subcomponents.length > 0) {
            let subLastAdded = {x: -nodeWidth, y: 120 - nodeHeight}

            for (const sub of subcomponents) {
                let subAdded = addComponent(sub, subLastAdded.x + nodeWidth + 10, subLastAdded.y, true, curr.name);
                if (subAdded) {
                    componentsAdded.push(sub)
                    subLastAdded.x += nodeWidth + 10;
                } else {
                    // subcomponent exists -> set as child of curr
                    setNodes((nodes) => nodes.map((node) => {
                        if (node.id === sub.name) {
                            return ({
                                ...node,
                                data: { ...node.data, label: node.id,},
                                position: {
                                    x: subLastAdded.x + nodeWidth + 10,
                                    y: subLastAdded.y
                                },
                                parentNode: curr,
                                extent: 'parent'
                            });
                        } else {
                            return node;
                        }
                    }));
                    subLastAdded.x += nodeWidth + 10;
                }
            }
            
            // update current size
            const newWidth = subcomponents.length * (nodeWidth + 20);
            const newHeight = nodeHeight * 3;
            setNodes((nodes) => nodes.map((node) => {
                if (node.id === curr.name) {
                    return ({
                        ...node,
                        data: { ...node.data, label: node.id},
                        style: {
                            width: newWidth,
                            height: newHeight
                        }
                    });
                } else {
                    return node;
                }
            }));
        }

        for (const edge of edges) {
            // find other node from curr
            let other = (name === edge.inVertex.name) ? 
                    edge.outVertex : edge.inVertex;
            
            let added = addComponent(other, lastAdded.x, lastAdded.y + nodeHeight + 20);
    
            addEdge(
                edge.id, 
                edge.outVertex.name, 
                edge.inVertex.name,
                edge.subcomponent
            );

            if (added) {
                componentsAdded.push(other);
                lastAdded.y += nodeHeight + 20;
            }
        }


        // setSubLastAdded({...subLastAdded})
        setLastAdded({...lastAdded});
        sortNodes();
        resolve(componentsAdded);
    });
}
)
}

const nodeTypes = useMemo(
() => ({component: ComponentNode}), []
);

window.addEventListener("error", (e) => {
if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || e.message === 'ResizeObserver loop limit exceeded') {
console.log("Oh, yeah × 2!!!!");
e.stopImmediatePropagation();
}
});

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
                    setLastAdded({x: 350, y: 100});
                    // console.log('here', lastAdded);
                    visualizeComponent();
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
        <ReactFlowProvider>
            <ReactFlow 
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                nodesConnectable={false}
            >
            {/* {console.log(edges)} */}
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
                <Panel position="top-right">
                    <button onClick={() => onLayout('TB')}>vertical layout</button>
                    <button onClick={() => onLayout('LR')}>horizontal layout</button>
                </Panel>
            </ReactFlow>
        </ReactFlowProvider>
    </VisualizerPanel>
</Grid>

</Grid>

)

}
