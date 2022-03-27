import { Paper, Table, TableBody, TableRow, 
    TableHead, TableCell, TableContainer, 
    CircularProgress,
    TableSortLabel,
    Typography,
} from '@mui/material';

import { 
    emDashIfEmpty 
} from './utility/utility.js';

/**
 * A MUI Component that returns a table containing a header along with 
 * the content to put in the table rows.
 * @param {Array[Array[Object]]} tableRowContent - an array of rows for the
 * table, which themselves are arrays of objects.
 * @param {Array[object]} tableHeadCells - an array of table header cells to
 * put in the header of the table.
 * @param {bool} loaded - whether the table's elements were loaded
 * @param {string} orderBy - What table header id to order the 
 * table's elements by
 * @param {string} direction - the order direction, must be 'asc' or 'desc' 
 * @param {function} setOrderBy - a function to update the value to order
 * the table by, when the user changes it
 * @param {function} setOrderDirection - a function to update the direction to
 * order the table by, when the user clicks on a table header.
 * @param {number} width - the width of the table itself.
 */
function ElementList(
    { 
        tableRowContent, 
        tableHeadCells,
        loaded, 
        orderBy, 
        direction, 
        setOrderBy, 
        setOrderDirection,
        width
        }
    ) {

    /**
     * Function to call when clicking on a table header to change sort.
     * @param {string} property - the name of the property that 
     * you are changing the order of.
     */
    const updateSort = (property) => {
        if (orderBy === property) {
            // if this property is already selected, flip the direction which
            // its contents are sorted in.
            setOrderDirection(direction === 'asc' ? 'desc' : 'asc')
        }
        else {
            setOrderBy(property)
            setOrderDirection('asc')
        }
    }

    // set the width of the table. Has a default value of 600px if a width
    // is not specified.
    let tableWidth = (width) ? width : '600px';

    // initial contents of the table IF the element list is not loaded
    let content = (
        <TableRow>  
            <TableCell 
                colSpan={3} 
                style={{
                    textAlign: 'center',
                }}
            >
                <CircularProgress 
                    style={{
                        paddingTop: 2,
                        paddingBottom: 2,
                    }}
                />
            </TableCell>
        </TableRow>
    );

    // if the elements are loaded, update the contents of the table.
    if (loaded) {

        if (tableRowContent.length === 0) {
            content = (
                <TableRow>
                    <TableCell 
                        colSpan={10} 
                        style={{
                            padding: '16px',
                            textAlign: 'center',
                        }}
                    >
                        <Typography style={{
                            color: 'grey',
                        }}>
                            No objects found.
                        </Typography>
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
                                        align={(index === 0) ? "left" : "right"}
                                        style={{
                                            wordWrap: 'break-word',
                                        }}
                                    >
                                        {emDashIfEmpty(c)}
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
        <TableContainer 
            component={Paper}
            style={{
                marginTop: '8px',
                width: tableWidth,
                maxWidth: '100%',
                marginLeft: 'auto',
                marginRight: 'auto',
                textAlign: 'center',
            }} 
        >
            <Table 
                size="small"
            >
                <TableHead>
                    <TableRow>
                        {
                            tableHeadCells.map((headCell, index) => (
                                <TableCell
                                    key={headCell.id}
                                    align={(index === 0) ? 'left' : 'right'}
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
