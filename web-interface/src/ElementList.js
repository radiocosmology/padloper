import { Paper, Table, TableBody, TableRow, 
    TableHead, TableCell, TableContainer, 
    CircularProgress,
    TableSortLabel
} from '@mui/material';

import { 
    emDashIfEmpty 
} from './utility/utility.js';

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
                        colSpan={3} 
                        style={{
                            padding: '16px',
                            textAlign: 'center',
                        }}
                    >
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
                                        align={(index === 0) ? "left" : "right"}
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
                width: '600px',
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
