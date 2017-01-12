{
let state = {
    "current_tooth": null,
    "teeth": {}
};

let previous_teeth_states = [];

function initState(json) {
    state.teeth = {};
    if (json && json !== "") {
        state.teeth = JSON.parse(json);
    }
}

function saveStateField() {
    const field = document.getElementById("id_dental_chart");
    field.value = JSON.stringify(state.teeth);
}

function undo() {
    let previous = previous_teeth_states.pop();
    if (previous) {
        initState(previous);
        updateDentalChart();
    }
}

// Redraw colors for state change
function updateDentalChart () {
    const svg = document.querySelector(".dental-chart--image").contentDocument;
    const chart = document.querySelector(".dental-chart");

    // Clear old state
    let elements = svg.querySelectorAll(".tooth-shape");
    for (let i = 0; i < elements.length; i++) {
        elements[i].className.baseVal = elements[i].className.baseVal.replace(/tooth__\w+/, '');
    }
    elements = svg.querySelectorAll(".tooth-x");
    for (let i = 0; i < elements.length; i++) {
        elements[i].className.baseVal = elements[i].className.baseVal.replace(/tooth__x/, '');
    }

    for (let tooth in state.teeth) {
        const action = state.teeth[tooth];
        const element = svg.querySelector(`#tooth-${tooth} .tooth-shape`);
        // If we changed dental chart from deciduous to permanent,
        // ignore old state
        if (! element) {
            continue
        }

        const x = svg.querySelector(`#tooth-${tooth}-x`);

        if (action === "x") {
            // In case of absent tooth (or tooth to remove) we make
            // absensce sign — &times; — visible
            x.className.baseVal += " tooth__x";
        } else {
            // In other cases make tooth colored
            element.className.baseVal += ` tooth__${action}`;
        }
    }
}

function showToothMenu(event) {
    const element = event.target;
    const embeded = document.querySelector(".dental-chart--image");
    const svg_node = embeded.contentDocument.firstChild;
    let menu = document.querySelector(".dental-chart--menu");

    for (let e = element; e ; e = e.parentNode) {
        // Firefox does not support dataset on SVGElement yet
        if (e.dataset && e.dataset.tooth) {
            state.current_tooth = e.dataset.tooth;
            break;
        }
    }
    menu.style.left = embeded.offsetLeft + event.clientX + "px";
    menu.style.top = embeded.offsetTop + event.clientY + "px";
    menu.classList.add("dental-chart--menu__visible");
}

function hideToothMenu() {
    const menu = document.querySelector(".dental-chart--menu");
    menu.classList.remove("dental-chart--menu__visible");
    state.current_tooth = null;
}

function setToothState(event) {
    const element = event.target;
    let tooth_type;
    for (let e = element; e ; e = e.parentNode) {
        if (e.dataset && e.dataset.action) {
            tooth_type = e.dataset.action;
            break;
        }
    }
    previous_teeth_states.push(JSON.stringify(state.teeth));
    if (tooth_type === "clear") {
        delete state.teeth[state.current_tooth];
    } else {
        state.teeth[state.current_tooth] = tooth_type;
    }
    hideToothMenu();
    updateDentalChart();
    saveStateField();
}

function initDentalChart (init_json, allow_edit) {
    const svg = document.querySelector(".dental-chart--image").contentDocument;

    // Attach style to SVG object
    const link = svg.createElementNS("http://www.w3.org/1999/xhtml", "link");
    link.setAttribute("href", "dental_chart.css");
    link.setAttribute("type", "text/css");
    link.setAttribute("rel", "stylesheet");
    svg.firstChild.appendChild(link);

    // Add classes to teeth
    let elements = svg.querySelectorAll('g[id^="tooth-"]');
    for (let i = 0; i < elements.length; i++) {
        let element = elements[i];
        if (allow_edit) {
            element.addEventListener("click", showToothMenu, true);
            element.className.baseVal += " tooth__editable";
        }
        // As IE doesn’t support classList for SVG element, use ol’ good className
        element.querySelector("path").className.baseVal += " tooth-shape";
        element.querySelector("text").className.baseVal += " tooth-x";
        element.className.baseVale += ` ${element.id} tooth`;
        // Firefox lacks of dataset support in SVGElement
        if (!("dataset" in element)) {
            element.dataset = {};
        }
        element.dataset.tooth = element.id.replace(/tooth-/, '');
    }

    elements = document.querySelectorAll(".dental-chart--menu-variant");
    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener("click", setToothState, false);
    }

    svg.addEventListener("click", function() {
        if (state.current_tooth) {
            hideToothMenu();
        }
    }, true);

    if (allow_edit && document.querySelector(".dental-chart--undo")) {
        document.querySelector(".dental-chart--undo").addEventListener("click", undo, false);
    }

    initState(init_json);
    updateDentalChart();
}

window.initDentalChart = initDentalChart;

}
