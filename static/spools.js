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

// adding the event listener to every td
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
        const response = await fetch('/spools/edit', {
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
        const response = await fetch('/spools/delete', {
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
        for (let i = 0; i < tableCells.length; i++){
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

// Create event listener for button click
const lockButton = document.getElementById('lock');
lockButton.addEventListener('click', changeLock);