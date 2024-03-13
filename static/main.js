console.log("hello?") // testing my console works

let tableCells = document.getElementsByClassName('editable'); // getting all the <td>s

proveEvent(); // testing my function works

// just more tests so I know it works
// it isn't being called/invoked when I 'focusout' of a td
function proveEvent() {
    console.log("event happended");
    alert("hello there");
}

for (let i = 0; i < tableCells.length; i++) {
    tableCells[i].addEventListener('focusout', proveEvent);
    console.log("event listener added to: " + tableCells[i]);   // this line is not running
}


console.log(tableCells); // logs sucessfully, the data is there
