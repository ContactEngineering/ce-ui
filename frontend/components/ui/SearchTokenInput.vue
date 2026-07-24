<script setup lang="ts">
/**
 * Search input with filter chips ("tokens").
 *
 * Typing a known prefix followed by a colon (e.g. `author:`) turns the prefix
 * into a chip; the text typed next becomes the chip's value and is committed
 * with Enter, comma or blur. Committed chips are rendered as badges with a
 * remove button. Anything that is not a chip is emitted as free search text.
 *
 * Keyboard interaction:
 *   - Enter / comma  commit the chip value being typed
 *   - Escape         cancel the active chip (turns it back into plain text)
 *   - Backspace      in an empty input: cancel the active chip, or pop the
 *                    last committed chip back into edit mode
 *
 * While an `author:` chip is being typed, matching user names are suggested
 * (fetched from the user API).
 */

import axios from "axios";
import {computed, ref} from "vue";

// Chip types offered via `prefix:` syntax
const TOKEN_TYPES = {
    author: {label: "Author"},
    tag: {label: "Tag"},
    name: {label: "Name"}
};

// Committed chips: [{type: 'author'|'tag'|'name', value: string}]
const tokens = defineModel<any[]>("tokens", {default: () => []});
// Free search text (everything that is not a chip)
const text = defineModel<string>("text", {default: ""});

const props = defineProps({
    placeholder: {type: String, default: "Type to start searching..."},
    userApiUrl: {type: String, default: "/users/v1/user/"},
    tagApiUrl: {type: String, default: "/manager/api/tag/"},
    suggestionLimit: {type: Number, default: 5},
    suggestionDelay: {type: Number, default: 250}
});

// Autocomplete sources per chip type: how to build the request URL and how to
// extract a list of suggestion strings from the response.
const SUGGESTION_SOURCES = {
    author: {
        url: (term: string, limit: number) =>
            `${props.userApiUrl}?name=${encodeURIComponent(term)}&limit=${limit}`,
        extract: (data: any) => (data.results ?? []).map((user: any) => user.name)
    },
    tag: {
        url: (term: string, limit: number) =>
            `${props.tagApiUrl}?search=${encodeURIComponent(term)}&limit=${limit}`,
        extract: (data: any) => data ?? []
    }
};

// Chip currently being typed (value lives in the input), or null
const _activeType = ref<string | null>(null);
// Current contents of the text input
const _input = ref<string>(text.value);
// Autocomplete state
const _suggestions = ref<any[]>([]);
const _highlighted = ref<number>(-1);
let suggestionTimer: any = null;
let suggestionSequence = 0;

const _inputElement = ref<HTMLInputElement | null>(null);

const prefixPattern = new RegExp(`^(${Object.keys(TOKEN_TYPES).join("|")}):$`, "i");

function tokenLabel(type: string): string {
    return TOKEN_TYPES[type]?.label ?? type;
}

function emitText() {
    // Free text only applies when no chip is being typed
    text.value = _activeType.value == null ? _input.value : "";
}

function onInput() {
    if (_activeType.value == null) {
        const match = _input.value.match(prefixPattern);
        if (match) {
            // `author:` (etc.) typed -- convert the prefix into an active chip
            _activeType.value = match[1].toLowerCase();
            _input.value = "";
            text.value = "";
            return;
        }
        emitText();
    } else {
        requestSuggestions();
    }
}

function commitToken() {
    if (_activeType.value != null && _input.value.trim().length > 0) {
        tokens.value = [...tokens.value, {type: _activeType.value, value: _input.value.trim()}];
        _activeType.value = null;
        _input.value = "";
        clearSuggestions();
    }
}

function cancelToken() {
    if (_activeType.value != null) {
        // Turn the chip back into plain text, e.g. "author:lar"
        _input.value = `${_activeType.value}:${_input.value}`;
        _activeType.value = null;
        clearSuggestions();
        emitText();
    }
}

function removeToken(index: number) {
    tokens.value = tokens.value.filter((token, i) => i !== index);
}

function onKeydown(event: KeyboardEvent) {
    if (event.key === "Enter" || event.key === ",") {
        if (_activeType.value != null) {
            event.preventDefault();
            if (_highlighted.value >= 0 && _highlighted.value < _suggestions.value.length) {
                selectSuggestion(_suggestions.value[_highlighted.value]);
            } else {
                commitToken();
            }
        } else if (event.key === "Enter") {
            event.preventDefault();  // do not submit any surrounding form
        }
    } else if (event.key === "Escape") {
        if (_activeType.value != null) {
            event.preventDefault();
            cancelToken();
        }
    } else if (event.key === "Backspace" && _input.value.length === 0) {
        if (_activeType.value != null) {
            // Drop the colon: back to editing the bare prefix as text
            event.preventDefault();
            _input.value = _activeType.value;
            _activeType.value = null;
            clearSuggestions();
            emitText();
        } else if (tokens.value.length > 0) {
            // Pop the last chip back into edit mode
            event.preventDefault();
            const last = tokens.value[tokens.value.length - 1];
            tokens.value = tokens.value.slice(0, -1);
            _activeType.value = last.type;
            _input.value = last.value;
            requestSuggestions();
        }
    } else if (event.key === "ArrowDown" && _suggestions.value.length > 0) {
        event.preventDefault();
        _highlighted.value = (_highlighted.value + 1) % _suggestions.value.length;
    } else if (event.key === "ArrowUp" && _suggestions.value.length > 0) {
        event.preventDefault();
        _highlighted.value =
            (_highlighted.value - 1 + _suggestions.value.length) % _suggestions.value.length;
    }
}

function onBlur() {
    // Commit a chip value typed so far; drop an empty active chip. Delay so a
    // click on a suggestion is processed first.
    setTimeout(() => {
        if (_activeType.value != null) {
            if (_input.value.trim().length > 0) {
                commitToken();
            } else {
                cancelToken();
            }
        }
        clearSuggestions();
    }, 200);
}

function clearSuggestions() {
    if (suggestionTimer != null) {
        clearTimeout(suggestionTimer);
        suggestionTimer = null;
    }
    suggestionSequence++;
    _suggestions.value = [];
    _highlighted.value = -1;
}

function requestSuggestions() {
    const source = _activeType.value != null ? SUGGESTION_SOURCES[_activeType.value] : null;
    if (source == null || _input.value.trim().length < 2) {
        clearSuggestions();
        return;
    }
    if (suggestionTimer != null) {
        clearTimeout(suggestionTimer);
    }
    suggestionTimer = setTimeout(() => {
        suggestionTimer = null;
        const requestId = ++suggestionSequence;
        axios.get(source.url(_input.value.trim(), props.suggestionLimit))
            .then(response => {
                if (requestId !== suggestionSequence) {
                    return;  // stale response
                }
                _suggestions.value = source.extract(response.data);
                _highlighted.value = -1;
            })
            .catch(() => {
                /* Suggestions are a convenience; ignore errors */
            });
    }, props.suggestionDelay);
}

function selectSuggestion(suggestion: string) {
    if (_activeType.value != null) {
        tokens.value = [...tokens.value, {type: _activeType.value, value: suggestion}];
        _activeType.value = null;
        _input.value = "";
        clearSuggestions();
        _inputElement.value?.focus();
    }
}

function focusInput() {
    _inputElement.value?.focus();
}

const showSuggestions = computed(() => _suggestions.value.length > 0);

</script>

<template>
    <div class="position-relative flex-grow-1">
        <div class="form-control d-flex flex-wrap align-items-center gap-1 search-token-input"
             @click="focusInput">
            <!-- Committed chips -->
            <span v-for="(token, index) in tokens"
                  :key="`${token.type}-${index}`"
                  class="badge text-bg-primary d-flex align-items-center gap-1">
                {{ tokenLabel(token.type) }}: {{ token.value }}
                <button type="button"
                        class="btn-close btn-close-white btn-close-sm"
                        :aria-label="`Remove ${tokenLabel(token.type)} filter`"
                        @click.stop="removeToken(index)"></button>
            </span>
            <!-- Chip being typed -->
            <span v-if="_activeType != null"
                  class="badge text-bg-primary">
                {{ tokenLabel(_activeType) }}:
            </span>
            <input ref="_inputElement"
                   v-model="_input"
                   type="search"
                   class="search-token-text flex-grow-1"
                   :placeholder="tokens.length === 0 && _activeType == null ? placeholder : ''"
                   @input="onInput"
                   @keydown="onKeydown"
                   @blur="onBlur"/>
        </div>
        <!-- Autocomplete suggestions (authors, tags) -->
        <div v-if="showSuggestions"
             class="list-group position-absolute w-100 shadow-sm search-token-suggestions">
            <button v-for="(suggestion, index) in _suggestions"
                    :key="suggestion"
                    type="button"
                    class="list-group-item list-group-item-action py-1"
                    :class="{active: index === _highlighted}"
                    @mousedown.prevent="selectSuggestion(suggestion)">
                {{ suggestion }}
            </button>
        </div>
    </div>
</template>

<style scoped>
.search-token-text {
    border: none;
    outline: none;
    background: transparent;
    min-width: 10rem;
}

.btn-close-sm {
    font-size: 0.6em;
}

.search-token-suggestions {
    z-index: 1050;
}
</style>
