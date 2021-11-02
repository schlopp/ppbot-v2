function toggleFields(id) {
    command = document.getElementById(id);
    for (let element of command.children) {
        if (element instanceof HTMLFieldSetElement) {
            element.classList.toggle("visible");
        }
    }
}
