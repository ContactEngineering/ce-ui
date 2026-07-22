<script setup lang="ts">
/**
 * A deep-zoom image together with a button for downloading it as PNG.
 */

import {ref} from "vue";

import DeepZoomImage from "@/components/ui/DeepZoomImage.vue";

defineProps({
    folderUrl: String,
    prefix: {
        type: String,
        default: ''
    },
    colorbar: {
        type: Boolean,
        default: false
    }
});

const _image = ref(null);
</script>

<template>
    <DeepZoomImage ref="_image"
                   :colorbar="colorbar"
                   :folder-url="folderUrl"
                   :prefix="prefix">
    </DeepZoomImage>
    <div class="pull-right">
        <a class="btn btn-default btn-block btn-lg mt-3"
           @click="_image.download()">
            Download PNG
        </a>
    </div>
</template>
