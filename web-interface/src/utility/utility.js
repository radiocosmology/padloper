// takes UNIX time in seconds
export function unixTimeToString(UNIX_timestamp, includeTime){
    let a = new Date(UNIX_timestamp * 1000);
    let months = [
        'Jan','Feb','Mar','Apr','May','Jun','Jul',
        'Aug','Sep','Oct','Nov','Dec'
    ];
    let year = a.getFullYear();
    let month = months[a.getMonth()];
    let date = a.getDate();
    let hour = a.getHours();
    let min = a.getMinutes();
    let sec = a.getSeconds();

    let time = `${date} ${month} ${year}`;
    if (includeTime) {
        time += `, ${hour}:${min}:${sec}`;
    }
    return time;
}

// takes a string, returns "—" if the string is equal to "".
export function emDashIfEmpty(str) {
    return (str === '' || str == null ? '—' : str);
}

// return whether value satisfies the regular expression regex
export function verifyRegex(value, regex) {
    // this ideally should never be called but...
    if (!regex || typeof value !== 'string') {
        return false;
    }
    else {
        return value.match(regex);
    }
}