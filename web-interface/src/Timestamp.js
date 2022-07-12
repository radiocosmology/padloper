import Tooltip from '@mui/material/Tooltip';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import { 
    unixTimeToString, 
} from './utility/utility.js';

/**
 * A Tooltip that displays a Unix time in date/time format, and when hovered,
 * also displays hours/minutes along with the actual Unix time.
 * @param {int} unixTime - the Unix time to display/consider.
 * @param {*} ...props - properties to add to the text of the unix time 
 * (e.g. styling) 
 */
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
                        {/* Done so they lie on top of each other vertically */}
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
                {unixTimeToString(unixTime, true)}
            </Typography>
            
            
            
        </Tooltip>
    )
}