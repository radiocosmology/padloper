import Tooltip from '@mui/material/Tooltip';
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
            title={unixTimeToString(unixTime, true)}
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