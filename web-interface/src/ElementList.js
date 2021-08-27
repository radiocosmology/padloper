import { Paper, Box, Table, TableBody, TableRow, 
    TableHead, TableCell, TableContainer, 
    CircularProgress,
    TableSortLabel,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

// styling for the react elements.
const useStyles = makeStyles((theme) => ({
    table: {
        marginTop: theme.spacing(1),
        width: theme.spacing(75),
        maxWidth: '100%',
        marginLeft: 'auto',
        marginRight: 'auto',
        textAlign: 'center',
    },
    progressWrapper: {
        textAlign: 'center',
    },
    progress: {
        paddingTop: theme.spacing(2),
        paddingBottom: theme.spacing(2),
    },
    noComponentsText: {
        padding: theme.spacing(2),
        textAlign: 'center',
    }
}));


function ElementList(
    { components, loaded, orderBy, direction, setOrderBy, setOrderDirection }
    ) {
    
    const classes = useStyles();

    // function to call when clicking on a table header to change sort.
    // property is the name of the property that you are changing the order of.
    const updateSort = (property) => {
        if (orderBy === property) {
            setOrderDirection(direction === 'asc' ? 'desc' : 'asc')
        }
        else {
            setOrderBy(property)
            setOrderDirection('asc')
        }
    }

    // the header cells of the table with their ids, labels, and how to align
    // them. 
    const headCells = [
        {
            id: 'name', 
            label: 'Component Name', 
            align: 'left'
        },
        {
            id: 'component_type', 
            label: 'Type', 
            align: 'right'
        },
        {
            id: 'revision', 
            label: 'Revision', 
            align: 'right'
        },
    ];

    // initial contents of the table IF the component list is not loaded
    let content = (
        <TableRow>
            <TableCell colSpan={3} className={classes.progressWrapper}>
                <CircularProgress className={classes.progress} />
            </TableCell>
        </TableRow>
    );

    // if the components are loaded, update the contents of the table.
    if (loaded) {

        if (components.length == 0) {
            content = (
                <TableRow>
                    <TableCell colSpan={3} className={classes.noComponentsText}>
                        No components found :(
                    </TableCell>
                </TableRow>
            )
        } 

        else {
            content = (
                <>
                    {components.map((c) => (
                    <TableRow key={c.name}>
                        <TableCell component="th" scope="row">
                            {c.name}
                        </TableCell>
                        <TableCell align="right">
                            {c.component_type.name}
                        </TableCell>
                        <TableCell align="right">
                            {(c.revision.name == null) ? "--" : c.revision.name}
                        </TableCell>
                    </TableRow>
                    ))}
                </>
            );
        }
    }

    // return the table along with the content
    return (
        <TableContainer component={Paper} className={classes.table}>
            <Table className={classes.table} size="small">
                <TableHead>
                    <TableRow>
                        {
                            headCells.map((headCell) => (
                                <TableCell
                                    key={headCell.id}
                                    align={headCell.align}
                                >
                                    <TableSortLabel
                                        active={orderBy === headCell.id}
                                        direction={
                                            orderBy === headCell.id 
                                            ? direction : 'asc'
                                        }
                                        onClick={()=>{updateSort(headCell.id)}}
                                    >   
                                        {headCell.label}
                                    </TableSortLabel>
                                </TableCell>
                            ))
                        }
                    </TableRow>
                </TableHead>

                <TableBody>
                    {content}
                </TableBody>
                
            </Table>
        </TableContainer>
    )
}

export default ElementList;
