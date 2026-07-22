<script setup lang="ts">
/**
 * Modal explaining the dataset search expression syntax.
 */

import {BModal} from "bootstrap-vue-next";

const visible = defineModel('visible', {
    type: Boolean,
    default: false
});
</script>

<template>
    <BModal v-model="visible"
            :ok-only="true"
            size="xl"
            title="Tips for searching">
        <p>Searching is performed over these fields:</p>
        <ul>
            <li>Names of surface and measurements</li>
            <li>Names of tags</li>
            <li>Descriptions of digital surface twins and measurements</li>
        </ul>

        <p>All texts in the search field is split into a list of tokens.
            Searching finds matches
            of the search expression among these tokens. You can build
            search
            expression from search terms
            as follows:</p>

        <table class="table table-bordered table-condensed">
            <thead class="thead-light">
            <tr>
                <th>Search result should list items with</th>
                <th>Search expression</th>
                <th>Comment</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>both <em>AFM</em> and <em>surface</em></td>
                <td><input readonly size="40" type="text"
                           value="AFM surface">
                </td>
                <td>text not inside quote marks will be interpreted as AND
                </td>
            </tr>
            <tr>
                <td>either <em>AFM</em> or <em>surface</em> or both</td>
                <td><input readonly size="40" type="text"
                           value="AFM OR surface"></td>
                <td>logical OR, least precedence</td>
            </tr>
            <tr>
                <td><em>AFM</em> but not <em>surface</em></td>
                <td><input readonly size="40" type="text"
                           value="AFM -surface">
                </td>
                <td>the logical not operator is written by using -, has
                    highest
                    precedence
                </td>
            </tr>
            <tr>
                <td>the phrase <em>AFM Surface</em></td>
                <td><input readonly size="40" type="text"
                           value='"AFM surface"'>
                </td>
                <td><em>AFM</em> and <em>surface</em> are found if next to
                    each
                    other
                </td>
            </tr>
            <tr>
                <td><em>AFM Surface</em> as a phrase and <em>imported</em>
                    somewhere else
                </td>
                <td><input readonly size="40"
                           type="text"
                           value='"AFM surface" imported'></td>
                <td></td>
            </tr>
            <tr>
                <td><em>AFM Surface</em> as a phrase and <em>imported</em>
                    but
                    not <em>material</em></td>
                <td><input readonly
                           size="40"
                           type="text" value='"AFM surface" imported -material'></td>
                <td>The above can also be combined. Parentheses are not
                    allowed,
                    all entries
                    are valid search expressions.
                </td>
            </tr>
            </tbody>
        </table>
    </BModal>
</template>
