async function sendData() {
    // On clicking the Submit, this JS function is activated
    console.log("sendData() was called!");

    // Read form inputs from the page
    const data = {
        val2: document.getElementById("val2").value,
        val4: document.getElementById("val4").value,
        at_pension_age: document.getElementById("at_pension_age").value
    };

    // Got the data from the page, send it to flask server via POST, and wait (non-blocking) for the response.
    // (note that without the await the fetch would have return a "Promise" object that is not the actual response...)
    let result; //Declare because result is put in a block and used afterwards outside it
    try {
        const response = await fetch('/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        // Check for http level errors
        if (!response.ok) {
            console.error("Server returned error:", response.status);
            alert("Something went wrong. Please try again.");
            return;
        }

        // Pause. Waits for the body to be read and converted into usable JSON
        result = await response.json();
        } catch (error) {
            console.error("Network error:", error);
            alert("Network error. Please check your connection.");
            }

        let table1 = "<h3>Income info (user inputs):</h3>";
        table1 += "<table border='1'><tr>";
        for (let col of result.main_table.columns) {
            table1 += "<th>" + col + "</th>";
        }
        table1 += "</tr>";
        for (let row of result.main_table.rows) {
            table1 += "<tr>";
            for (let cell of row) {
                table1 += "<td>" + cell + "</td>";
            }
            table1 += "</tr>";
        }
        table1 += "</table>";

        // Render NET INCOME table
        let netTable = "";
        if (result.net_income_table.rows.length > 0) {
            netTable += "<h3>Income and tax:</h3>";
            netTable += "<table border='1'><tr>";
            for (let col of result.net_income_table.columns) {
                netTable += "<th>" + col + "</th>";
            }
            netTable += "</tr>";
            for (let row of result.net_income_table.rows) {
                netTable += "<tr>";
                for (let cell of row) {
                    netTable += "<td>" + cell + "</td>";
                }
                netTable += "</tr>";
            }
            netTable += "</table>";
        }

        document.getElementById("output").innerHTML = table1 + "<br>" + netTable;
}

// Make sendData globally available
window.sendData = sendData;
console.log("sendData attached to window, indicating this main.js has been loaded");