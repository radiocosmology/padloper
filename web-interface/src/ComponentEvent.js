import Timestamp from './Timestamp.js';

import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import CommentIcon from '@mui/icons-material/Comment';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';

import { 
    emDashIfEmpty 
} from './utility/utility.js';
import { Typography } from '@mui/material';

/**
 * Styling for the background behind an event entry label
 */
const EntryRowLabel = styled((props) => (
    <Paper 
        elevation={0}
        {...props}
    />
))(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .05)',
    width: '80px',
    marginRight: theme.spacing(4),
}));

/**
 * A MUI component representing a single event for a component.
 * @param {string} name - the name of the event
 * @param {int} time - the Unix time of the event (when it actually happened)
 * @param {string} uid - the ID of the user that made the event
 * @param {int} edit_time - the Unix time of when the event was edited
 * @param {string} comments - The comments associated with the event
 * @param {object} theme - The MUI Theme object to inherit a theme 
 * @returns 
 */
function ComponentEvent(
    {
        name,
        time,
        uid,
        edit_time,
        comments,
        theme
    }
) {
    return (
        <ThemeProvider theme={theme}>
            <Stack 
            direction='row' spacing={1}>
                <EntryRowLabel>{name}</EntryRowLabel>

                <AccessTimeIcon fontSize="small"/>

                <Timestamp unixTime={time} />

                <PersonIcon 
                    fontSize="small"
                    style={{
                        marginLeft: theme.spacing(3),
                    }}
                />
                <Typography>
                    {emDashIfEmpty(uid)} 
                </Typography> 
                <Stack direction="row" spacing={0}>
                    (<Timestamp unixTime={edit_time} />)
                </Stack>

                <CommentIcon 
                    fontSize="small"
                    style={{
                        marginLeft:theme.spacing(3),
                    }}
                />
                <div>{emDashIfEmpty(comments)}</div>
            </Stack>
        </ThemeProvider>
    )
}

export default ComponentEvent;