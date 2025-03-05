<script setup>

/**
 * Vue component for visualizing 2D maps (topography, pressure, etc.) using
 * Deep Zoom Image files and OpenSeadragon.
 */

import axios from "axios";
import {onMounted, ref, watch} from "vue";
import {BSpinner, useToastController} from "bootstrap-vue-next";

const props = defineProps({
    folderUrl: String,
    prefix: {
        type: String,
        default: ''
    },
    colorbar: {
        type: Boolean,
        default: false
    },
    downloadButton: {
        type: Boolean,
        default:
            false
    },
    retryDelay: {
        type: Number,
        default:
            5000
    }
});

const {show} = useToastController();

// The OpenSeadragon instance
let viewer = null;

// File list
let inventory = null;

// GUI logic
const _openSeadragonElement = ref(null);
const _isLoaded = ref(false);
const _colorbarTitle = ref(null);
const _colorbarTicks = ref([]);
const _colormap = ref(null);
const _errorMessage = ref(null);

onMounted(() => {
    requestDzi();
});


watch(() => props.folderUrl, (newValue, oldValue) => {
    refreshDzi();
});


watch(() => props.prefix, (newValue, oldValue) => {
    refreshDzi();
});


function getTileSource(meta) {
    return {
        // Custom tile source, see dzitilesource.js, line 324
        height: parseInt(meta.Image.Size.Height, 10),
        width: parseInt(meta.Image.Size.Width, 10),
        tileWidth: parseInt(meta.Image.TileSize, 10),
        tileHeight: parseInt(meta.Image.TileSize, 10),
        tileOverlap: parseInt(meta.Image.Overlap, 10),
        getTileUrl: function (level, x, y) {
            const fn = `${props.prefix}dzi_files/${level}/${x}_${y}.jpg`;
            return inventory[fn].file;
        }
    }
}


function refreshDzi() {
    // We are loading a new image
    _isLoaded.value = false;

    // Request new image and replace current one
    axios.get(props.folderUrl).then(response => {
        inventory = response.data;
        axios.get(inventory[`${props.prefix}dzi.json`].file).then(response => {
            viewer.addTiledImage({
                tileSource: getTileSource(response.data),
                success: () => {
                    _isLoaded.value = true;
                }
            });
        });
    }).catch(error => {
        show?.({
            props: {
                title: "Error rendering zoomable image",
                body: error.message,
                variant: 'danger'
            }
        });
    });
}


function requestDzi() {
    _isLoaded.value = false;

    axios.get(props.folderUrl).then(response => {
        const dziJson = `${props.prefix}dzi.json`;
        inventory = response.data;
        if (!(dziJson in inventory)) {
            _errorMessage.value = `DZI metadata file ${dziJson} not found.`;
            return;
        }
        axios.get(inventory[dziJson].file).then(response => {
            // DZI metadata
            const meta = response.data;

            // Create OpenSeadragon viewer
            viewer = new OpenSeadragon.Viewer({
                element: _openSeadragonElement.value,
                tileSources: getTileSource(meta),
                showNavigator: true,
                navigatorPosition: 'TOP_LEFT',
                navigatorSizeRatio: 0.1,
                wrapHorizontal: false,
                wrapVertical: false,
                minZoomImageRatio: 0.5,
                maxZoomPixelRatio: 5.0,
                crossOriginPolicy: "Anonymous",
                showNavigationControl: false,
            });

            // Add a scale bar
            if (meta.Image.PixelsPerMeter) {
                viewer.scalebar({
                    type: OpenSeadragon.ScalebarType.MICROSCOPY,
                    pixelsPerMeter: (meta.Image.PixelsPerMeter.Width + meta.Image.PixelsPerMeter.Height) / 2,
                    minWidth: "75px",
                    location: OpenSeadragon.ScalebarLocation.BOTTOM_LEFT,
                    xOffset: 10,
                    yOffset: 10,
                    stayInsideImage: true,
                    color: "black",
                    fontColor: "black",
                    backgroundColor: "rgba(255, 255, 255, 0.5)",
                    fontSize: "medium",
                    barThickness: 2
                });
            }

            // Configure color bar
            if (props.colorbar && meta.Image.ColorbarRange && meta.Image.ColorbarTitle && meta.Image.Colormap) {
                // Set title and colormap
                _colorbarTitle.value = meta.Image.ColorbarTitle;
                _colormap.value = meta.Image.Colormap;

                // Generate tick positions and labels
                const mn = meta.Image.ColorbarRange.Minimum;
                const mx = meta.Image.ColorbarRange.Maximum;

                const log10_tick_dist = (Math.round(Math.log10(mx - mn)) - 1);
                const fraction_digits = log10_tick_dist > 0 ? 0 : -log10_tick_dist;
                let tick_dist = 10 ** log10_tick_dist;
                let nb_ticks = Math.trunc((mx - mn) / tick_dist) + 1;

                while (nb_ticks > 15) {
                    tick_dist *= 2;
                    nb_ticks = Math.trunc((mx - mn) / tick_dist) + 1;
                }

                for (let i = 0; i < nb_ticks; i++) {
                    const v = Math.trunc(mn / tick_dist) * tick_dist + tick_dist * i;
                    const relpos = (mx - v) * 100 / (mx - mn);
                    if (relpos > 0 && relpos < 100) {
                        _colorbarTicks.value.push({
                            relpos: relpos,
                            label: v.toFixed(fraction_digits)
                        });
                    }
                }
            }

            _isLoaded.value = true;
        }).catch(error => {
            show?.({
                props: {
                    title: "Error rendering zoomable image",
                    body: error.message,
                    variant: 'danger'
                }
            });
        });
    }).catch(error => {
        let error_has_response = "response" in error;
        /**
         * If an error occurs *not* because of XMLHttpRequest.abort(), show an
         * error message. Do not show error on .abort(). See also
         * https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/abort
         * */
        console.log(error);

        if (error_has_response && (error.response.status == 0)) {
            _errorMessage.value = "Canceled loading of plot.";
        } else if (error_has_response && (error.response.status == 404)) {
            /* 404 indicates the resource is not yet available, retry */
            console.log("Resource not yet available, retrying..")
            setTimeout(requestDzi, props.retryDelay);
        } else {
            /* Treat any other code as an actual error */
            _errorMessage.value = error.message;
        }
    });
}


function download() {
    // Image download. Code has been adapted from:
    // https://github.com/KTGLeiden/Openseadragon-screenshot/blob/master/openseadragonScreenshot.js
    var downloadImage = () => {
        viewer.world.getItemAt(0).removeAllHandlers('fully-loaded-change');

        var imgCanvas = viewer.drawer.canvas;
        var downloadCanvas = document.createElement("canvas");
        downloadCanvas.width = imgCanvas.width;
        downloadCanvas.height = imgCanvas.height;

        var context = downloadCanvas.getContext('2d');
        context.drawImage(imgCanvas, 0, 0);

        var scalebarCanvas = viewer.scalebarInstance.getAsCanvas();
        var location = viewer.scalebarInstance.getScalebarLocation();
        context.drawImage(scalebarCanvas, location.x, location.y);

        downloadCanvas.toBlob(function (blob) {
            saveAs(blob, "screenshot.png");
        });
    }

    if (viewer.world.getItemAt(0).getFullyLoaded()) {
        downloadImage();
    } else {
        viewer.world.getItemAt(0).addHandler('fully-loaded-change', downloadImage);
    }
}

defineExpose({
    download
});

</script>

<template>
    <div class="dzi-container">
        <div ref="_openSeadragonElement" class="dzi-view">
            <div v-if="!_isLoaded && _errorMessage === null"
                 class="d-flex justify-content-center mt-5">
                <div class="flex-column text-center">
                    <b-spinner/>
                    <p>Loading...</p>
                </div>
            </div>
            <div v-if="_errorMessage !== null" class='alert alert-danger'>
                Could not load plot data. Error: {{ _errorMessage }}
            </div>
        </div>
        <div v-if="colorbar && _isLoaded" class="dzi-colorbar">
            <div class="dzi-colorbar-title">
                {{ _colorbarTitle }}
            </div>
            <div :class='"dzi-colorbar-column background-" + _colormap'>
                <div v-for="tick in _colorbarTicks" class="dzi-colorbar-tick"
                     :style='"top: " + tick.relpos + "%;"'></div>
            </div>
            <div class="dzi-colorbar-column">
                <div v-for="tick in _colorbarTicks" class="dzi-colorbar-text"
                     :style='"top: " + tick.relpos + "%;"'>
                    {{ tick.label }}
                </div>
            </div>
        </div>
    </div>
</template>
