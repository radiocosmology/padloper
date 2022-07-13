import { 
    Paper, 
    Button, 
    Select, 
    MenuItem } 
from '@mui/material';

import { ArrowForward, ArrowBack } from '@mui/icons-material';

/**
 * A MUI component that returns a panel containing the range of the elements
 * being viewed, and a selection for how many you can view at a time.
 * @param {int} min - the index of the first element to display in the list.
 * @param {function} updateMin - function to call to update min
 * @param {int} range - how many elements to display at once in the list
 * @param {function} updateRange - function to call to update range
 * @param {int} count - how many elements there are in total
 * @param {object} rightColumn - whatever you want to place in the right column
 * of the panel, could be a MUI element, or JSX. 
 * @param {int} width - the width of the panel.
 */
function ElementRangePanel(
        { 
            min, 
            updateMin, 
            range, 
            updateRange, 
            count, 
            rightColumn,
            rightColumn2,
            width,
        }
    ) {

    /**
     * Update the range.
     * @param {*} event - event associated with the range update, the new
     * range is stored in event.target.value.
     */
    const handleRangeChange = (event) => {
        updateRange(event.target.value);
    }

    /**
     * 
     * TODO: Why are min, updateMin, range, count here? They're already
     * parameters of ElementRangePanel, so why take them as parameters again?
     * They're already in the scope.
     * 
     * @param {int} min - the index of the first element to display in the list.
     * @param {function} updateMin - function to call to update min
     * @param {int} range - how many elements to display at once in the list
     * @param {int} count - how many elements there are in total
     * @param {bool} increment - Whether to increment or decrement the min by 
     * range, which is the same as going forward/back to a new page. 
     */
    const changeMin = (min, updateMin, range, count, increment) => {

        let newMin = min;
    
        if (increment) {
            // make sure it stays within the bounds.
            if (newMin + range < count) {
                newMin += range;
            }
        }
        else {
            // make sure it stays within the bounds
            if (newMin < range) {
                newMin = 0;
            }
            else {
                newMin -= range;
            }
        }
    
        updateMin(newMin);
    }

    // the maximum element to display
    let max = min + range;
    if (max >= count) {
        max = count;
    }

    let numDisplayText = `Viewing ${min+1}-${max} out of ${count}`;
    if (count === 0) {
        numDisplayText = "No objects found";
    }

    // the width of the panel, by default it is 600px.
    let paperWidth = (width) ? width : '600px';

    // return the range panel.
    return (
        <Paper
            style={{
                marginTop: '16px',
                paddingTop: '8px',
                paddingBottom: '8px',
                flexGrow: 1,
                marginBottom: '8px',
                textAlign: 'center',
                display: 'grid',
                justifyContent: 'space-between',
                rowGap: '8px',
                width: paperWidth,
                maxWidth: '100%',
                margin: 'auto',
            }}
        >
            <div
                style={{
                    paddingTop: '8px',
                    gridRow: 1,
                    gridColumn: 1,
                    margin: 'auto'
                    
                }}>
                {numDisplayText}
            </div>
            <div
                style={{
                    gridRow: 2,
                    gridColumn: '1 / 2',
                    margin: 'auto', 
                }}>
                <Button 
                    color="primary" 
                    style={{
                        marginRight: '8px',
                        marginLeft: '8px',
                        padding: '16px',
                    }}
                    onClick={() => {
                        changeMin(min, updateMin, range, count, false)
                    }}
                    disabled={min <= 0}
                >
                    <ArrowBack />
                </Button>

                Show 
                <Select
                    labelId="range-select-label"
                    id="range-select"
                    value={range}
                    onChange={handleRangeChange}
                    style={{
                        marginRight: '8px',
                        marginLeft: '8px',
                    }}
                    displayEmpty 
                >
                    <MenuItem value={10}>10</MenuItem>
                    <MenuItem value={25}>25</MenuItem>
                    <MenuItem value={50}>50</MenuItem>
                    <MenuItem value={100}>100</MenuItem>
                </Select>
                at a time

                <Button 
                    color="primary" 
                    style={{
                        marginRight: '8px',
                        marginLeft: '8px',
                        padding: '16px',
                    }}
                    onClick={() => {
                        changeMin(min, updateMin, range, count, true)
                    }}
                    disabled={max >= count}
                >
                    <ArrowForward />
                </Button>
            </div>

            <div
                style={{
                    marginLeft: '16px',
                    marginRight: '16px',
                    gridRow: '1 / 3',
                    gridColumn: 2,
                    marginTop: 'auto',
                    marginBottom: 'auto'
                }}>
                {rightColumn}
            </div>
            <div
                style={{
                   marginLeft:'100px',
                   padding:'10px',
                   width:'100%'
                }}
            >
                {rightColumn2}
            </div>
        </Paper>
    )
}

export default ElementRangePanel;