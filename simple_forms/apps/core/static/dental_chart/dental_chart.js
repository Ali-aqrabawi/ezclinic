"use strict";

{
let state = {
    "current_tooth": null,
    "teeth": {}
};

function initState(json) {
    state.teeth = json === "" ? {} : JSON.parse(json);
}

function saveStateField() {
    const field = document.getElementById("id_dental_chart");
    field.value = JSON.stringify(state.teeth);
}

function updateDentalChart () {
    const svg = document.querySelector(".dental-chart--image").contentDocument;
    const chart = document.querySelector(".dental-chart");

    for (let tooth in state.teeth) {
        const action = state.teeth[tooth];
        const element = svg.querySelector(`#tooth-${tooth} .tooth-shape`);
        // If we changed dental chart from deciduous to permanent,
        // ignore old state
        if (! element) {
            continue
        }
        const x = svg.querySelector(`#tooth-${tooth}-x`);

        element.classList.remove("tooth__red");
        element.classList.remove("tooth__yellow");
        element.classList.remove("tooth__green");

        if (action === "x") {
            x.classList.add("tooth__x");
        } else {
            element.classList.add(`tooth__${action}`);
            x.classList.remove("tooth__x");
        }
    }
}

function showToothMenu(event) {
    const element = event.target;
    const menu = document.querySelector(".dental-chart--menu");
    const embeded = document.querySelector(".dental-chart--image");
    const svg_node = embeded.contentDocument.firstChild;
    const point = svg_node.createSVGPoint();

    for (let e = element; e ; e = e.parentNode) {
        if (e.dataset.tooth) {
            state.current_tooth = e.dataset.tooth;
            break;
        }
    }
    point.x = e.clientX;
    point.y = e.clientY;
    let loc = point.matrixTransform(svg_node.getScreenCTM().inverse());
    menu.style.left = embeded.offsetLeft + loc.x + "px";
    menu.style.top = embeded.offsetTop + loc.y+ "px";
    menu.classList.add("dental-chart--menu__visible");
}

function hideToothMenu() {
    const menu = document.querySelector(".dental-chart--menu");
    menu.classList.remove("dental-chart--menu__visible");
    state.current_tooth = null;
}

function setToothState(e) {
    const element = e.target;
    const tooth_type = element.dataset.action;
    state.teeth[state.current_tooth] = tooth_type;
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
    svg.querySelectorAll('g[id^="tooth-"]').forEach(function(element) {
        if (allow_edit) {
            element.addEventListener("click", showToothMenu, true);
            element.classList.add("tooth__editable");
        }
        element.querySelector("path").classList.add("tooth-shape")
        element.querySelector("text").classList.add("tooth-x")
        element.classList.add(element.id, "tooth");
        element.dataset.tooth = element.id.replace(/tooth-/, '');
    });

    document.querySelectorAll(".dental-chart--menu-variant").forEach(function(element) {
        element.addEventListener("click", setToothState, true);
    });

    svg.addEventListener("click", function() {
        if (state.current_tooth) {
            hideToothMenu();
        }
    }, true);

    initState(init_json);
    updateDentalChart();
}

window.initDentalChart = initDentalChart;

}
