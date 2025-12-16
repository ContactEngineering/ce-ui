import axios from "axios";
import {filesV2ManifestCreate} from "@/api";

export async function createFileManifest({folderUrl, fileName}) {
    const response = await filesV2ManifestCreate({
        body: {
            folder: folderUrl,
            filename: fileName
        }
    });
    // Return axios-compatible response format for backwards compatibility
    return response;
}

export function uploadFile({uploadInstructions, file, onUploadProgress}) {
    if (uploadInstructions.method === 'POST') {
        return axios.postForm(uploadInstructions.url, {
            ...uploadInstructions.fields, file: file
        }, {onUploadProgress: onUploadProgress});
    } else if (uploadInstructions.method === 'PUT') {
        return axios.put(uploadInstructions.url, file, {
            headers: {'Content-Type': 'binary/octet-stream'},
            onUploadProgress: onUploadProgress
        });
    } else {
        alert(`Unknown upload method: "${uploadInstructions.method}`);
    }
}
