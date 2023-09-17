function createSongMoodVisualization(mood_distribution, selector) {
    const width = 300;
    const height = 300;
    const radius = Math.min(width, height) / 2;

    // Define colors
    const color = d3.scaleOrdinal()
                    .domain([0, 1, 2, 3])
                    .range(["#1DB954", "#191414", "#B3B3B3", "#FFFFFF"]);

    // Create the SVG container
    const svg = d3.select(selector) // You can select a specific container if needed
                  .append("svg")
                  .attr("width", width)
                  .attr("height", height)
                  .append("g")
                  .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    // Create the pie chart
    const pie = d3.pie();
    const arc = d3.arc()
                  .innerRadius(0)
                  .outerRadius(radius);

    const arcs = svg.selectAll("arc")
                    .data(pie(mood_distribution))
                    .enter()
                    .append("g")
                    .attr("class", "arc");

    // Draw the pie slices
    arcs.append("path")
        .attr("d", arc)
        .attr("fill", function(d, i) {
            return color(i);
        });

    // Optional: Add labels (for a basic label showing the mood index)
    arcs.append("text")
        .attr("transform", function(d) {
            return "translate(" + arc.centroid(d) + ")";
        })
        .attr("text-anchor", "middle")
        .text(function(d, i) {
            return d.data > 0 ? i : ""; 
        });
}

function createDanceabilityVisualization(data, selector) {
    const margin = {top: 20, right: 20, bottom: 30, left: 40};
    const width = 500 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Set up scales
    const xScale = d3.scaleLinear()
        .domain([0, d3.max(data.danceability)])
        .range([0, width]);

    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data.energy)])
        .range([height, 0]);

    // Create the SVG container
    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Create the X axis
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale))
        .append("text")
        .attr("x", width / 2)
        .attr("y", 25)
        .attr("dy", ".71em")
        .style("text-anchor", "middle")
        .text("Danceability");

    // Create the Y axis
    svg.append("g")
        .call(d3.axisLeft(yScale))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Energy");

    // Plot the data points
    svg.selectAll("circle")
        .data(data.danceability)
        .enter().append("circle")
        .attr("cx", d => xScale(d))
        .attr("cy", (d, i) => yScale(data.energy[i]))
        .attr("r", 4)
        .attr("fill", "#1DB954");
}

function createPopularityVisualization(data, selector) {
    // Dimensions and margins
    const margin = {top: 20, right: 20, bottom: 30, left: 40};
    const width = 500 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Set up x scale
    const xScale = d3.scaleLinear()
        .domain([0, 100]) // Popularity values generally range from 0 to 100
        .range([0, width]);

    // Generate a histogram using d3's histogram function
    const histogram = d3.histogram()
        .domain(xScale.domain())
        .thresholds(xScale.ticks(20)) // Approx. 20 bins
        (data.song_popularity);

    // Set up y scale
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(histogram, d => d.length)])
        .range([height, 0]);

    // Create the SVG container
    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Create bars for histogram to contain rects and labels
    const bars = svg.selectAll(".bar")
        .data(histogram)
        .enter()
        .append("g")
        .attr("class", "bar")
        .attr("transform", d => "translate(" + xScale(d.x0) + "," + yScale(d.length) + ")");

    // Create the rectangles representing the bins
    bars.append("rect")
        .attr("x", 1)
        .attr("width", xScale(histogram[0].x1) - xScale(histogram[0].x0) - 1)
        .attr("height", d => height - yScale(d.length))
        .attr("fill", "#1DB954");

    // Create the X axis
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale))
        .append("text")
        .attr("x", width / 2)
        .attr("y", 25)
        .attr("dy", ".71em")
        .style("text-anchor", "middle")
        .text("Song Popularity");

    // Create the Y axis
    svg.append("g")
        .call(d3.axisLeft(yScale))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Number of Songs");
}


function createArtistDistributionVisualization(data, selector) {
    // Create a tooltip div
    const tooltip = d3.select("body")
        .append("div")
        .style("position", "absolute")
        .style("background", "rgba(255, 255, 255, 0.8)")
        .style("padding", "8px")
        .style("border", "1px solid #000")
        .style("border-radius", "5px")
        .style("visibility", "hidden")
        .style("pointer-events", "none");  // Ensures that the tooltip doesn't interfere with other mouse events

    // Modify the bars to add mouse events
    svg.selectAll(".bar")
    .on("mouseover", function(event, d, i) {
        // Position the tooltip near the mouse cursor and update its content
        tooltip.style("visibility", "visible")
            .text("Count: " + data.count[i])
            .style("top", (event.pageY - 10) + "px")
            .style("left", (event.pageX + 10) + "px");
    })
    .on("mouseout", function() {
        // Hide the tooltip
        tooltip.style("visibility", "hidden");
    });

    // Dimensions and margins
    const margin = {top: 20, right: 20, bottom: 30, left: 150};
    const width = 600 - margin.left - margin.right;
    const height = data.name.length * 30; // Assuming each bar and its margin to be 30px

    // Set up y scale (for artist names)
    const yScale = d3.scaleBand()
        .range([0, height])
        .domain(data.name)
        .padding(0.2);

    // Set up x scale (for count of songs by the artist)
    const xScale = d3.scaleLinear()
        .range([0, width])
        .domain([0, d3.max(data.count)]);

    // Create the SVG container
    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Create bars
    svg.selectAll(".bar")
        .data(data.name)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("y", d => yScale(d))
        .attr("height", yScale.bandwidth())
        .attr("x", 0)
        .attr("width", (d, i) => xScale(data.count[i]))
        .attr("fill", "#1DB954");

    // Create the Y axis
    svg.append("g")
        .call(d3.axisLeft(yScale));

    // Create the X axis
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale))
        .append("text")
        .attr("x", width / 2)
        .attr("y", 25)
        .attr("dy", ".71em")
        .style("text-anchor", "middle")
        .text("Count");
}


function createFavoriteGenresVisualization(data, selector) {

}