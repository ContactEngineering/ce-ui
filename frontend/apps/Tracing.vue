<script setup lang="ts">

import { inject, onMounted } from 'vue';
import { useToastController, BButton } from 'bootstrap-vue-next';
import * as d3 from "d3";

const appProps = inject("appProps");

const { show } = useToastController();

const width = 1040;
const height = 500;
// const path = d3.path();

const nodes = [];
const lines = [];

function handle_click(event) {

    const [x, y] = d3.pointer(event);

    nodes.push({ x: x, y: y, id: nodes.length });

    if (nodes.length > 1) {
        lines.push({ from: nodes[nodes.length - 2], to: nodes[nodes.length - 1], id: lines.length });
    }

    update();

}

onMounted(() => {
    d3.select("svg")
        .attr("width", width)
        .attr("height", height)
        .on("click", handle_click)
})

function update(params) {
    // NOTE: Add new nodes
    d3.select("svg")
        .selectAll(".node")
        .data(nodes)
        .join("g")
        .classed("node", true)
        .attr("transform", d => `translate(${d.x},${d.y})`)
        .call(d3.drag()
            .on("start", (event, d) => { })
            .on("drag", (event, d) => (d.x = event.x, d.y = event.y))
            .on("end", (event, d) => { })
            .on("start.update drag.update end.update", update))
        .attr("fill", "none")
        .attr("stroke", "#ff0000")
        .append("circle")
        .attr("r", 6)

    // NOTE: add new lines
    d3.select("svg")
        .selectAll(".line")
        .data(lines)
        .join("line")
        .classed("line", true)
        .attr("stroke", "#aaa")
        .attr("stroke-dasharray", "2 2")
        .attr("x1", d => d.from.x)
        .attr("y1", d => d.from.y)
        .attr("x2", d => d.to.x)
        .attr("y2", d => d.to.y)
}

function clear() {
    lines = [];
    nodes = [];
    update();
}

</script>

<template>
    <div class="d-flex align-items-center flex-column">
        <div class="mb-1 w-75">
            <BButton variant="danger" @click="clear()">Clear</BButton>
        </div>
        <svg class="border"></svg>
    </div>
</template>
