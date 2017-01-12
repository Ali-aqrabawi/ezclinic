{
    (function () {
        var initState = function initState(json) {
            state.teeth = {};
            if (json && json !== "") {
                state.teeth = JSON.parse(json);
            }
        };

        var saveStateField = function saveStateField() {
            var field = document.getElementById("id_dental_chart");
            field.value = JSON.stringify(state.teeth);
        };

        var undo = function undo() {
            var previous = previous_teeth_states.pop();
            if (previous) {
                initState(previous);
                updateDentalChart();
            }
        };

        // Redraw colors for state change


        var updateDentalChart = function updateDentalChart() {
            var svg = document.querySelector(".dental-chart--image").contentDocument;
            var chart = document.querySelector(".dental-chart");

            // Clear old state
            var elements = svg.querySelectorAll(".tooth-shape");
            for (var i = 0; i < elements.length; i++) {
                elements[i].className.baseVal = elements[i].className.baseVal.replace(/tooth__\w+/, '');
            }
            elements = svg.querySelectorAll(".tooth-x");
            for (var _i = 0; _i < elements.length; _i++) {
                elements[_i].className.baseVal = elements[_i].className.baseVal.replace(/tooth__x/, '');
            }

            for (var tooth in state.teeth) {
                var action = state.teeth[tooth];
                var element = svg.querySelector("#tooth-" + tooth + " .tooth-shape");
                // If we changed dental chart from deciduous to permanent,
                // ignore old state
                if (!element) {
                    continue;
                }

                var x = svg.querySelector("#tooth-" + tooth + "-x");

                if (action === "x") {
                    // In case of absent tooth (or tooth to remove) we make
                    // absensce sign — &times; — visible
                    x.className.baseVal += " tooth__x";
                } else {
                    // In other cases make tooth colored
                    element.className.baseVal += " tooth__" + action;
                }
            }
        };

        var showToothMenu = function showToothMenu(event) {
            var element = event.target;
            var embeded = document.querySelector(".dental-chart--image");
            var svg_node = embeded.contentDocument.firstChild;
            var menu = document.querySelector(".dental-chart--menu");

            for (var e = element; e; e = e.parentNode) {
                // Firefox does not support dataset on SVGElement yet
                if (e.dataset && e.dataset.tooth) {
                    state.current_tooth = e.dataset.tooth;
                    break;
                }
            }
            menu.style.left = embeded.offsetLeft + event.clientX + "px";
            menu.style.top = embeded.offsetTop + event.clientY + "px";
            menu.classList.add("dental-chart--menu__visible");
        };

        var hideToothMenu = function hideToothMenu() {
            var menu = document.querySelector(".dental-chart--menu");
            menu.classList.remove("dental-chart--menu__visible");
            state.current_tooth = null;
        };

        var setToothState = function setToothState(event) {
            var element = event.target;
            var tooth_type = void 0;
            for (var e = element; e; e = e.parentNode) {
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
        };

        var initDentalChart = function initDentalChart(init_json, allow_edit) {
            var svg = document.querySelector(".dental-chart--image").contentDocument;

            // Attach style to SVG object
            var link = svg.createElementNS("http://www.w3.org/1999/xhtml", "link");
            link.setAttribute("href", "dental_chart.css");
            link.setAttribute("type", "text/css");
            link.setAttribute("rel", "stylesheet");
            svg.firstChild.appendChild(link);

            // Add classes to teeth
            var elements = svg.querySelectorAll('g[id^="tooth-"]');
            for (var i = 0; i < elements.length; i++) {
                var element = elements[i];
                if (allow_edit) {
                    element.addEventListener("click", showToothMenu, true);
                    element.className.baseVal += " tooth__editable";
                }
                // As IE doesn’t support classList for SVG element, use ol’ good className
                element.querySelector("path").className.baseVal += " tooth-shape";
                element.querySelector("text").className.baseVal += " tooth-x";
                element.className.baseVale += " " + element.id + " tooth";
                // Firefox lacks of dataset support in SVGElement
                if (!("dataset" in element)) {
                    element.dataset = {};
                }
                element.dataset.tooth = element.id.replace(/tooth-/, '');
            }

            elements = document.querySelectorAll(".dental-chart--menu-variant");
            for (var _i2 = 0; _i2 < elements.length; _i2++) {
                elements[_i2].addEventListener("click", setToothState, false);
            }

            svg.addEventListener("click", function () {
                if (state.current_tooth) {
                    hideToothMenu();
                }
            }, true);

            if (allow_edit && document.querySelector(".dental-chart--undo")) {
                document.querySelector(".dental-chart--undo").addEventListener("click", undo, false);
            }

            if (!inited) {
                initState(init_json);
                inited = true;
            }
            updateDentalChart();
        };

        var inited = false;
        var state = {
            "current_tooth": null,
            "teeth": {}
        };

        var previous_teeth_states = [];

        window.initDentalChart = initDentalChart;
    })();
}
