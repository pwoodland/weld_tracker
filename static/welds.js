// hiding the first td in the table rows
const tableRows = document.querySelectorAll("tr");
// hide the first td cause its irrelevant
for (let i = 0; i < tableRows.length; i++) {
    tableRows[i].firstElementChild.style.display = "none";
}

// getting all the <td>s
const tableCells = document.getElementsByClassName('editable'); 

// adding the event listener to every td
for (let i = 0; i < tableCells.length; i++) {
    tableCells[i].addEventListener('focusout', sendData);
}

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

// change the button text and tds to be editable or uneditable
function changeLock() {
    if (lockButton.innerHTML == "Lock data") {
        lockButton.innerHTML = "Unlock data";
        for (let i = 0; i < tableCells.length; i++){
            tableCells[i].setAttribute("contenteditable", "false");
        }
    } else if (lockButton.innerHTML == "Unlock data") {
        lockButton.innerHTML = "Lock data";
            for (let i = 0; i < tableCells.length; i++){
                tableCells[i].setAttribute("contenteditable", "true");
            }
    } else {
        console.log("Something wrong with changeLock function");
    }
}

// Create event listener for button click
const lockButton = document.getElementById('lock');
lockButton.addEventListener('click', changeLock);