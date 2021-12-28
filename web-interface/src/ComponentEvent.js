import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import CommentIcon from '@mui/icons-material/Comment';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';

import { 
    unixTimeToString, 
    emDashIfEmpty 
} from './utility/utility.js';

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
            <Stack direction='row' spacing={1}>
                <EntryRowLabel>{name}</EntryRowLabel>

                <AccessTimeIcon fontSize="small"/>
                <div>
                    {unixTimeToString(time, true)}
                </div>

                <PersonIcon 
                    fontSize="small"
                    style={{
                        marginLeft: theme.spacing(3),
                    }}
                />
                <div>
                    {emDashIfEmpty(uid)} ({unixTimeToString(
                        edit_time, false)
                    })
                </div>

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