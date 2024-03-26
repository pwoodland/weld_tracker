/************************************
***        FRONT-END CLEANUP      ***
*************************************/

// hiding the first td in the table rows
const tableRows = document.querySelectorAll("tr");
// hide the first td cause its irrelevant
for (let i = 0; i < tableRows.length; i++) {
    tableRows[i].firstElementChild.style.display = "none";
}

/************************************
***      DOM ELEMENT ARRAYS       ***
*************************************/

// getting all the <td>s
const tableCells = document.getElementsByClassName('editable'); 

// Get all the delete buttons
const deleteButtons = document.getElementsByClassName("delete_button");

/************************************
***     MASS EVENT LISTENERS      ***
*************************************/

// adding the event listener to every editable td
for (let i = 0; i < tableCells.length; i++) {
    tableCells[i].addEventListener('focusout', sendData);
}

// add the event lsitener to every delete button
for (let i = 0; i < deleteButtons.length; i++) {
    deleteButtons[i].addEventListener('click', deleteData);
}

/************************************
***           API CALLS           ***
*************************************/

// getting the row for unfocused td
async function sendData() {
    console.log("Getting row for unfocused <td>");
    console.log(this.parentNode.textContent);
    try {
        const response = await fetch('/welds/edit', {
            method: "POST",
            body: JSON.stringify(this.parentNode.textContent),
            headers: {
                "Content-Type": 'application/json'
            }
        });
        console.log("sent the data");
        if (response.ok) {
            const jsonResponse = await response.json();
            console.log(jsonResponse);
        }
    } catch (error) {
        console.log(error);
    }
}

// delete the row API call
async function deleteData() {
    try {
        const response = await fetch('/welds/delete', {
            method: "DELETE",
            headers: {
                "Content-Type": 'application/json'
            },
            body: JSON.stringify(this.parentNode.textContent)
        });
        if (response.ok) {
            const jsonResponse = await response.json();
            console.log(jsonResponse);
            this.parentNode.style.display = "none";
        }
    } catch (error) {
        console.log(error);
    }
}


/************************************
***     SPECIFIC INTERACTIONS     ***
*************************************/

// change the button text and tds to be editable or uneditable
function changeLock() {
    if (lockButton.innerHTML == "Lock data") {
        lockButton.innerHTML = "Unlock data";
        for (let i = 0; i < tableCells.length; i++){
            tableCells[i].setAttribute("contenteditable", "false");
        }
        for (let o = 0; o < tableRows.length; o++) {
            deleteButtons[o].style.display = "none";
        }
    } else if (lockButton.innerHTML == "Unlock data") {
        lockButton.innerHTML = "Lock data";
        for (let i = 0; i < tableCells.length; i++) {
            tableCells[i].setAttribute("contenteditable", "true");
        }
        for (let o = 0; o < tableRows.length; o++) {
            deleteButtons[o].style.display = "inline";
            console.log(deleteButtons[o]);
        }
    } else {
        console.log("Something wrong with changeLock function");
    }
}

// Create event listener for lock button click
const lockButton = document.getElementById('lock');
lockButton.addEventListener('click', changeLock);


// start a filter option
// create event listener for search box
const searchBox = document.getElementById('search_box');
searchBox.addEventListener('keyup', searchTable);

// define search box filter
function searchTable() {
    const filters = this.value.toUpperCase().split(" ");            // creating multiple filters if space in search box
    const tableBody = document.getElementById("welds_data");        // getting the tbody (weld data)
    const tableRows = tableBody.getElementsByTagName("tr");         // getting all the rows in the tbody

    for (row of tableRows) {
        const tcells = row.cells;
        let shouldDisplayRow = false;
        for (let cell = 1; cell < tcells.length; cell++) {           // ignoring first column cause its just the database id#
            for (filter of filters) {
                if ((tcells[cell].innerText.toUpperCase().includes(filter)) || tcells[cell].textContent.toUpperCase().includes(filter)) {
                    shouldDisplayRow = true;
                    break;
                }
            }
        }
        row.style.display = shouldDisplayRow ? "" : "none";
    }
}