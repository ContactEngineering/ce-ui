import axios from "axios";

const manifestUrl = "/files/manifest/";

export function createFileManifest({folderUrl, fileName}) {
    const body = {
        folder: folderUrl, filename: fileName
    }
    return axios.post(manifestUrl, body);
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
