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