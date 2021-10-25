import { Paper, Box, Table, TableBody, TableRow, 
    TableHead, TableCell, TableContainer, 
    CircularProgress,
    TableSortLabel
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Link } from "react-router-dom";

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
    noElementsText: {
        padding: theme.spacing(2),
        textAlign: 'center',
    }
}));


function ElementList(
    { 
        tableRowContent, 
        tableHeadCells,
        loaded, 
        orderBy, 
        direction, 
        setOrderBy, 
        setOrderDirection
        }
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

    // initial contents of the table IF the element list is not loaded
    let content = (
        <TableRow>  
            <TableCell colSpan={3} className={classes.progressWrapper}>
                <CircularProgress className={classes.progress} />
            </TableCell>
        </TableRow>
    );

    // if the elements are loaded, update the contents of the table.
    if (loaded) {

        if (tableRowContent.length == 0) {
            content = (
                <TableRow>
                    <TableCell colSpan={3} className={classes.noElementsText}>
                        No objects found :(
                    </TableCell>
                </TableRow>
            )
        } 

        else {
            content = (
                <>
                    {tableRowContent.map((row) => (
                        <TableRow>
                            {
                                row.map((c, index) => (
                                    <TableCell 
                                        align={(index == 0) ? "left" : "right"}
                                    >
                                        {(c == null) ? "--" : c}
                                    </TableCell>
                                ))
                            }
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
                            tableHeadCells.map((headCell, index) => (
                                <TableCell
                                    key={headCell.id}
                                    align={(index == 0) ? 'left' : 'right'}
                                >
                                    {
                                        (headCell.allowOrdering) ? (
                                            <TableSortLabel
                                                active={orderBy === headCell.id}
                                                direction={
                                                    orderBy === headCell.id 
                                                    ? direction : 'asc'
                                                }
                                                onClick={
                                                    () => {
                                                        updateSort(headCell.id)
                                                    }
                                                }
                                            >   
                                                {headCell.label}
                                            </TableSortLabel>
                                        ) : (
                                            headCell.label
                                        )
                                    }
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
