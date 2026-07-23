import axios from "axios";

const manifestUrl: string = "/files/manifest/";

/** Register a new file with the file storage system, yielding upload instructions. */
export function createFileManifest({folderUrl, fileName}) {
    const body = {
        folder: folderUrl, filename: fileName
    };
    return axios.post(manifestUrl, body);
}

/** Upload a file according to the upload instructions returned by `createFileManifest`. */
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
        throw new Error(`Unknown upload method: "${uploadInstructions.method}"`);
    }
}
