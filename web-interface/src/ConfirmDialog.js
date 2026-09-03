import React from 'react';
import {
    Button, Dialog, DialogActions, DialogContent, DialogContentText,
    DialogTitle,
} from '@mui/material';

/**
 * A small confirmation dialog shown before destructive actions.
 *
 * @param {bool} open - whether the dialog is shown
 * @param {string} title - the dialog title
 * @param {string} message - the question put to the user
 * @param {string} confirmLabel - label of the confirming button
 * @param {string} confirmColor - MUI colour of the confirming button
 * @param {bool} busy - disables the buttons while the action is in flight
 * @param {function} onConfirm - called when the user confirms
 * @param {function} onClose - called when the user cancels or dismisses
 */
export default function ConfirmDialog({
    open, title, message, confirmLabel = 'Confirm', confirmColor = 'error',
    busy = false, onConfirm, onClose,
}) {
    return (
        <Dialog
            open={open}
            onClose={busy ? undefined : onClose}
            aria-labelledby="confirm-dialog-title"
        >
            <DialogTitle id="confirm-dialog-title">{title}</DialogTitle>
            <DialogContent>
                <DialogContentText>{message}</DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={busy}>
                    Cancel
                </Button>
                <Button
                    onClick={onConfirm}
                    color={confirmColor}
                    variant="contained"
                    disabled={busy}
                    autoFocus
                >
                    {confirmLabel}
                </Button>
            </DialogActions>
        </Dialog>
    );
}
