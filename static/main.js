console.log("hello?")

let tableCells = document.getElementsByClassName('editable');


function proveEvent() {
    console.log("event happended");
}

for (let i = 0; i < tableCells.length; i++) {
    tableCells[i].addEventListener('focusout', proveEvent);
}
