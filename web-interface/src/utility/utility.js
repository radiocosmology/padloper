// takes UNIX time in seconds

/**
 * Take in a Unix time in seconds, then format it as a string.
 * @param {int} UNIX_timestamp - Unix time in seconds
 * @param {bool} includeTime - whether or not to include the 
 * hours/minutes/seconds 
 * @returns If includeTime is false, return a string of the format
 * <DAY> <MONTH> <YEAR>.
 * If includeTime is true, return a string of the format
 * <DAY> <MONTH> <YEAR>, HH:MM:SS
 */
export function unixTimeToString(UNIX_timestamp, includeTime){

    // Make a date object, turn the Unix time into milliseconds first.
    let a = new Date(UNIX_timestamp * 1000);

    // a list of all the months (wow!!)
    let months = [
        'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'
    ];

    let year = a.getFullYear();
    let month = months[a.getMonth()];
    let date = a.getDate();
    let hour = a.getHours();

    // prepend a 0 to the front of the minutes/seconds 
    // if they are a single digit, this will turn 5 minutes into 05 minutes.
    // if they are two digits, this 0 will be cut off when it is sliced later.
    let min = "0" + a.getMinutes();
    let sec = "0" + a.getSeconds();

    let time = `${date} ${month} ${year}`;
    if (includeTime) {
        // if the minutes/seconds are currently 3 digits, 
        // only keep the last two (the first digit is most certainly a 0)
        time += `, ${hour}:${min.slice(-2)}:${sec.slice(-2)}`;
    }

    return time;
}

/**
 * Take Unix time in MILLISECONDS, then format it as an ISO string.
 * See https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString
 * https://en.wikipedia.org/wiki/ISO_8601
 * @param {int} time - Unix time in MILLISECONDS 
 * @returns An ISO-formatted date/time to minute precision.
 */
export function unixTimeToISOString(time) {

    // TIME IS IN MILLISECONDS!!!!!!!!!!!!!!!
    let date = new Date(time);

    // For minute precision
    return date.toISOString().substring(0,16); 
}

// 
/**
 * Take a string, return "—" if the string is equal to "", and return the string
 * itself otherwise.
 * @param {string} str - the string to look at. 
 * @returns — if the string is empty, and if not, then return the string itself.
 */
export function emDashIfEmpty(str) {
    return (str === '' || str == null ? '—' : str);
}

/**
 * Return whether value satisfies the regular expression regex
 * @param {string} value - The string to chcek and see if it satisfies the regex 
 * @param {*} regex - the regular expression to evaluate value on
 * @returns Result of matching value against regex.
 * 
 * See https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/match
 */
export function verifyRegex(value, regex) {

    const pattern = new RegExp(regex);
    return pattern.test(value);
}

// export function verifyRegex(value, regex) {
//     if (!regex || typeof value !== 'string') {
//         return false;
//     }
//     else {
//         console.log(regex)
//         return regex.test(value);
//     }
// }