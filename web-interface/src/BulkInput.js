import React, { useState, useEffect } from 'react';
import axios from 'axios';

import { styled } from '@mui/material/styles';
import {
    Button, Dialog, DialogActions, DialogContent, DialogContentText,
    DialogTitle, Paper, Typography, Grid, TextField, IconButton,
    InputAdornment, Tooltip, Link, Box, Divider, List, ListItem,
    ListItemButton, ListItemText,
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

import { withBase, requireOkJson } from './paths.js';
import Authenticator from './components/Authenticator';
import { unixTimeToISOString } from './utility/utility';


const CodeBlock = styled((props) => (
    <Box
        component="pre"
        {...props}
    />
))(({ theme }) => ({
    fontFamily: 'monospace',
    fontSize: 'medium',
    whiteSpace: 'pre-wrap',
    wordWrap: 'break-word',
    backgroundColor: theme.palette.grey["200"],
    padding: theme.spacing(2, 2),
    margin: theme.spacing(1, 0),
    borderRadius: theme.shape.borderRadius,
}))


function BulkInput() {
    // comment that will be added to the components
    const [comment, setComment] = useState("");

    // timestamp and time entry error states
    const [time, setTime] = useState(Math.floor(Date.now()));
    const [timeError, setTimeError] = useState("");

    // state variables to store the LTF and any potential errors
    const [ltf, setLtf] = useState("");
    const [ltfError, setLtfError] = useState("");
    const [ltfHelpOpen, setLtfHelpOpen] = useState(false);

    /**
     * Validate the Layout Text Format to ensure it is ready for submission
     * @todo
     */
    const validateLtf = (e) => {
        // split ltf into groups of lines where separated by blank line
        // const operations = ltf.split("\n\n").map((l) => l.split("\n"));
        // console.log(operations);
    }

    /**
     * Submit the LTF to the backend for processing
     */
    const handleSubmit = () => {
        if (!ltf) {
            setLtfError("LTF cannot be empty.");
            return;
        }

        if (timeError) {
            alert("Please fix the timestamp error before submitting.");
            return;
        }

        // Perform submission logic here
        // console.log("Submitting form with data:");
        // console.log("Timestamp:", time);
        // console.log("Comment:", comment);
        // console.log("LTF:", ltf);

        let path = '/api/bulk_input';
        let payload = { ltf, time, comment };
        axios.post(withBase(path), payload, {
            headers: {
                'Content-Type': 'application/json'
            }
        }).then((res) => {
            if (res?.data?.error) {
                setLtfError(res.data.error);
            } else if (res?.data?.result) {
                console.log("Success!");
                setLtf("");
            }
            // setLtf(res?.data?.result);
        }).catch((err) => {
            console.error(err);
        });

        // Clear the form after submission
        setComment("");
        // setLtf("");
        setTimeError("");
        setLtfError("");
    };

    return (
        <>
            <Authenticator />
            <Paper
                elevation={2}
                sx={{
                    mt: 4,
                    p: 4,
                    mb: 2,
                    margin: 'auto',
                    width: '100%',
                    maxWidth: {
                        md: '600px',
                    },
                }}
            >
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <Typography
                            component="h1"
                            variant="h5"
                            sx={{ textAlign: 'center' }}
                        >
                            Bulk Input
                        </Typography>
                    </Grid>
                    <Grid item xs={6}>
                        <TextField
                            id="datetime-input"
                            label="Timestamp"
                            type="datetime-local"
                            fullWidth
                            defaultValue={unixTimeToISOString(time)}
                            onBlur={(e) => {
                                const date = Date.parse(e.target.value);
                                if (!isNaN(date)) {
                                    setTime(Math.round(date));
                                    setTimeError("");
                                } else {
                                    setTimeError("Invalid date.");
                                }
                            }}
                            error={timeError !== ""}
                            helperText={timeError}
                            InputLabelProps={{
                                shrink: true,
                            }}
                        />
                    </Grid>
                    <Grid item xs={6}>
                        <TextField
                            id="comment"
                            label="Comment"
                            fullWidth
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <TextField
                            id="bulk-input"
                            label="Enter LTF"
                            multiline
                            rows={10}
                            fullWidth
                            value={ltf}
                            onChange={(e) => setLtf(e.target.value)}
                            onBlur={validateLtf}
                            error={ltfError !== ""}
                            helperText={ltfError}
                            FormHelperTextProps={{ sx: { whiteSpace: "pre-line" } }}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <Tooltip title="What is LTF?">
                                            <IconButton
                                                color="primary"
                                                onClick={() => setLtfHelpOpen(true)}
                                                edge="end"
                                                sx={{
                                                    position: 'absolute',
                                                    top: 4,
                                                    right: 16,
                                                }}
                                            >
                                                <HelpOutlineIcon />
                                            </IconButton>
                                        </Tooltip>
                                    </InputAdornment>
                                ),
                            }}
                        />
                    </Grid>
                    <Grid item xs={6} sx={{ textAlign: 'center' }}>
                        <Button
                            variant="contained"
                            color="primary"
                            fullWidth
                            disabled={timeError !== ""}
                        >
                            Preview LTF
                        </Button>
                    </Grid>
                    <Grid item xs={6} sx={{ textAlign: 'center' }}>
                        <Button
                            variant="outlined"
                            color="primary"
                            fullWidth
                            disabled={timeError !== ""}
                            onClick={handleSubmit}
                        >
                            Apply LTF
                        </Button>
                    </Grid>
                </Grid>
            </Paper>

            {/* Help Modal for LTF */}
            <Dialog
                open={ltfHelpOpen}
                onClose={() => setLtfHelpOpen(false)}
                aria-labelledby="ltf-help-dialog-title"
                aria-describedby="ltf-help-dialog-description"
            >
                <DialogTitle id="ltf-help-dialog-title">
                    <Typography variant="h5">Layout Text Format (LTF) Reference</Typography>
                </DialogTitle>
                <DialogContent>
                    <Box
                        sx={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            justifyContent: 'center',
                            alignItems: 'center',
                            gap: 1,
                            mb: 2,
                            textAlign: 'center',
                            // position: 'sticky',
                            // top: 0,
                            // zIndex: 1,
                            // backgroundColor: 'background.paper',
                            // padding: 1,
                        }}
                    >
                        <Link href="#ltf-making-connections" underline="hover" sx={{ color: 'text.secondary' }}>
                            Making Connections
                        </Link>
                        <Divider orientation="vertical" flexItem sx={{ height: 'auto', borderColor: 'text.secondary' }} />
                        <Link href="#ltf-disconnecting" underline="hover" sx={{ color: 'text.secondary' }}>
                            Disconnecting Components
                        </Link>
                        <Divider orientation="vertical" flexItem sx={{ height: 'auto', borderColor: 'text.secondary' }} />
                        <Link href="#ltf-setting-properties" underline="hover" sx={{ color: 'text.secondary' }}>
                            Setting Properties
                        </Link>
                        <Divider orientation="vertical" flexItem sx={{ height: 'auto', borderColor: 'text.secondary' }} />
                        <Link href="#ltf-comments" underline="hover" sx={{ color: 'text.secondary' }}>
                            Comments and Blank Lines
                        </Link>
                        <Divider orientation="vertical" flexItem sx={{ height: 'auto', borderColor: 'text.secondary' }} />
                        <Link href="#ltf-multi-line" underline="hover" sx={{ color: 'text.secondary' }}>
                            Multi-line Entries
                        </Link>
                    </Box>
                    <Box id="ltf-making-connections" sx={{ mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Making Connections
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        <DialogContentText variant="body1">
                            Connections are made by placing serial numbers on adjacent lines:
                            <CodeBlock>
                                {`
                                    ANT0000A
                                    LNA0000A

                                    LNA0000A
                                    CXA0000A

                                    AMP0000A
                                    CDCXA0000A
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            As a shortcut, connection chains can be entered without repitition; the above can be rendered as follows:
                            <CodeBlock>
                                {`
                                    ANT0000A
                                    LNA0000A
                                    CXA0000A

                                    AMP0000A
                                    CDCXA0000A
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            Component connections can also be made on one line by using the "&gt;" character, separated from each component with a space. Operations can also be separated by a line-ending semicolon rather than a blank line. The above can also be written as follows:
                            <CodeBlock>
                                {`
                                    ANT0000A > LNA0000A > CXA0000A;
                                    AMP0000A > CDCXA0000A;
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            Note that this is likely less useful for field data entry with barcodes, but it may be helpful for streamlined online data entry.
                            <br /><br />
                            Subcomponents may be connected with "&gt;&gt;", again separated with spaces. Subcomponent connections are directional, so "&lt;&lt;" can be used to connect in the other direction. Thus, the following configurations are equivalent:
                            <CodeBlock>
                                {`
                                    ANT0000P1 >> ANT0000A

                                    ANT0000A << ANT0000P1
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            Alternatively, if the sequences are configured correctly as subcomponents, connecting normally will automatically set it up as a subcomponent.
                        </DialogContentText>
                    </Box>
                    <Box id="ltf-disconnecting" sx={{ mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Disconnecting &amp; Replacing Components
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        <DialogContentText variant="body1">
                            Connections are severed by placing two forward slashes between two components, either on one line or three:
                            <CodeBlock>
                                {`
                                    ANT0000A // LNA0000A

                                    AMP0000A
                                    //
                                    CDCXA0000A
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            Connection severing can be chained like connecting components. This would normally be used to sever connections on either side of a component in a signal chain, i.e. to replace the component.
                            <CodeBlock>
                                {`
                                    ANT0000A // LNA0000A // CXA0000A
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            If two components are not actively connected, attempting to sever them will return a warning and continue with following operations.
                            <br /><br />
                            As a shortcut to replace one component with a new one, "&lt;&gt;" can be used in place of first severing the old connections then reconnecting the new component. The following sets of operations are equivalent:
                            <CodeBlock>
                                {`
                                    ANT0000A // LNA0000A // CXA0000A;
                                    ANT0000A > LNA0000B > CXA0000A;

                                    LNA0000A <> LNA0000B;
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            Note that the replacement operator can also be split into three lines like the severing operator.
                        </DialogContentText>
                    </Box>
                    <Box id="ltf-setting-properties" sx={{ mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Setting Component Properties
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        <DialogContentText variant="body1">
                            Properties are entered on the same line as a component; more than one property can be added at once.
                            <CodeBlock>
                                {`
                                    LNA0000A attenuation=50

                                    ANT0000A pol1=N pol2=W
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            Note that there is no whitespace surrounding the equals sign.
                            <br /><br />
                            Properties can be removed by withholding the argument:
                            <CodeBlock>
                                {`
                                    LNA0000A attenuation=
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            Properties can be added at the same time as connections are made. The following connects the two components and specifies their properties simultaneously:
                            <CodeBlock>
                                {`
                                    LNA0000A attenuation=50
                                    ANT0000A pol1=N pol2=W
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            If multiple properties are given for a component, then they will <b>all</b> be applied in succession, even if they are different. This is not usually desired behavior, so be careful when specifying properties; e.g. don't set <code>attenuation</code> twice in the same line.
                            <br /><br />
                            If a space character is necessary in an attribute, use a plus character, <code>+</code> instead. For example, <code>type=Low+Noise+Amplifier</code> is equivalent to setting the <code>type</code> attribute to <code>Low Noise Amplifier</code>.
                        </DialogContentText>
                    </Box>
                    <Box id="ltf-comments" sx={{ mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Comments and Blank Lines
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        <DialogContentText variant="body1">
                            Lines starting with a hash (<code>#</code>) are comments. Lines starting with two dollar signs (<code>$$</code>) are treated like blank lines. This may be useful in cases where blank lines are undesireable.
                            <CodeBlock>
                                {`
                                    # The following are two connections.
                                    LNA0000A
                                    ANT0000A
                                    $$------
                                    LNA0001A
                                    ANT0001A
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                        </DialogContentText>
                    </Box>
                    <Box id="ltf-multi-line" sx={{ mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Multi-line Entries
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        <DialogContentText variant="body1">
                            Some barcodes are designed to be scanned in stages. For example, bulkheads may have three scans: a 'header', the row, and the column.
                            <CodeBlock>
                                {`
                                    BKR...A
                                    ...C...
                                    ....02.
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            In this example, the full stop (".") is a wildcard, and the above translates to <code>BKRC02A</code>. Hence, the following,
                            <CodeBlock>
                                {`
                                    CXS0000A
                                    BKR...A
                                    ...C...
                                    ....02.
                                    CXS0001A
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            is equivalent to:
                            <CodeBlock>
                                {`
                                    CXS0000A
                                    BKRC02A
                                    CXS0001A
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            In addition to the dash, a plus sign <em>at the beginning of a string</em> means that any number of initial characters can be matched. Hence, <code>+C...</code> would be equivalent to <code>...C...</code> in the example above. The dots at the end are not explicitly required but help verify positioning, and are thus recommended in more complex patterns.
                            <br /><br />
                            It is, however, important to note that the "<code>+</code>" wildcard will match the first available location that is large enough to accomodate the continuation string, so be careful when using it. Additionally, the order of the applied string matters. For example, the following operations,
                            <CodeBlock>
                                {`
                                    ANT.....
                                    +0000
                                    +A

                                    ANT.....
                                    +A
                                    +0000
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>,
                            will resolve to two different strings:
                            <CodeBlock>
                                {`
                                    ANT0000A

                                    ANTA0000
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            Due to this possible mismatch, using the full dot sequence rather than the plus shorthand is recommended for patterns involving more than two barcode scans, as the scan order would no longer matter.
                            <br /><br />
                            Properties for multi-line entries can be included on any line in the entry, but properties on later lines will override properties on earlier lines. For example, the following operations,
                            <CodeBlock>
                                {`
                                    LNA..... attenuation=50
                                    ...0000.
                                    .......A attenuation=40

                                    LNA..... attenuation=50
                                    ...0001. polarization=N
                                    .......A
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            will resolve to the following:
                            <CodeBlock>
                                {`
                                    LNA0000A attenuation=40

                                    LNA0001A attenuation=50 polarization=N
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                            As such, it is generally recommended to include properties only on the last line of a multi-line entry, but there are some use cases that may benefit from allowing entries to be overridden in sequence.
                            <br /><br />
                            The dot interpolation can also be input on one line with pipe characters ("<code>|</code>") and a semicolon, though this is likely less useful, as the general use case would be for field scanning multiple barcodes.
                            <CodeBlock>
                                {`
                                    LNA..... | ...0000. | +A;
                                `.replaceAll(/^[ ]+/gm, "").trim()}
                            </CodeBlock>
                        </DialogContentText>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setLtfHelpOpen(false)} color="primary">
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    )
}

export default BulkInput;
