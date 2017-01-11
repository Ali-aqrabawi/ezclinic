{
    (function () {
        var initState = function initState(json) {
            state.teeth = json === "" ? {} : JSON.parse(json);
        };

        var saveStateField = function saveStateField() {
            var field = document.getElementById("id_dental_chart");
            field.value = JSON.stringify(state.teeth);
        };

        var updateDentalChart = function updateDentalChart() {
            var svg = document.querySelector(".dental-chart--image").contentDocument;
            var chart = document.querySelector(".dental-chart");

            for (var tooth in state.teeth) {
                var action = state.teeth[tooth];
                var element = svg.querySelector("#tooth-" + tooth + " .tooth-shape");
                // If we changed dental chart from deciduous to permanent,
                // ignore old state
                if (!element) {
                    continue;
                }
                var x = svg.querySelector("#tooth-" + tooth + "-x");

                element.className.baseVal.replace(/tooth__red/, '');
                element.className.baseVal.replace(/tooth__yellow/, '');
                element.className.baseVal.replace(/tooth__green/, '');

                if (action === "x") {
                    x.className.baseVal += " tooth__x";
                } else {
                    element.className.baseVal += " tooth__" + action;
                    x.className.baseVal.replace(/tooth__x/, '');
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
            var tooth_type = element.dataset.action;
            state.teeth[state.current_tooth] = tooth_type;
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
            for (var _i = 0; _i < elements.length; _i++) {
                elements[_i].addEventListener("click", setToothState, true);
            }

            svg.addEventListener("click", function () {
                if (state.current_tooth) {
                    hideToothMenu();
                }
            }, true);

            initState(init_json);
            updateDentalChart();
        };

        var state = {
            "current_tooth": null,
            "teeth": {}
        };

        window.initDentalChart = initDentalChart;
    })();
}
