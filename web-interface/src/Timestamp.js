import Tooltip from '@mui/material/Tooltip';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import { 
    unixTimeToString, 
} from './utility/utility.js';

export default function Timestamp(
    {
        unixTime,
        ...props
    }
) {

    return (
        <Tooltip 
            title={
                <>
                    <Stack spacing={0.35} style={{
                        textAlign: 'center',
                    }}>
                        <div>
                            {unixTimeToString(unixTime, true)}
                        </div>
                        <div>
                            Unix: {unixTime}
                        </div>
                    </Stack>
                </>
            }
            disableFocusListener 
            disableTouchListener
            arrow
        >
            <Typography {...props}>
                {unixTimeToString(unixTime, false)}
            </Typography>
            
            
            
        </Tooltip>
    )
}