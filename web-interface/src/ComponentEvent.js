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
                    (<Timestamp unixTime={time} />)
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