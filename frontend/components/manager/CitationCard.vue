<script setup lang="ts">
/**
 * "How to cite" card for a published dataset: license, recommended citation
 * wording and bibliographic references in several formats.
 */

import {BAccordion, BAccordionItem, BAlert} from 'bootstrap-vue-next';

import {ccLicenseInfo} from "@/utils/licenses";
import HelpTooltip from "@/components/ui/HelpTooltip.vue";

defineProps({
    publication: {
        type: Object,
        required: true
    }
});
</script>

<template>
    <div class="w-100">
        <p class="mb-5">
            <a :href="ccLicenseInfo[publication.license].descriptionUrl">
                <img
                    :src="`/static/images/cc/${publication.license}.svg`"
                    :title="`Dataset can be reused under the terms of the ${ccLicenseInfo[publication.license].title}.`"
                    style="float:right; margin-left: 0.25rem;"/>
            </a>
            This dataset can be reused under the terms of the
            <a :href="ccLicenseInfo[publication.license].descriptionUrl">
                {{ ccLicenseInfo[publication.license].title }}
            </a>.
            When reusing this dataset, please cite the original
            source.
        </p>
        <h6>Recommended citation</h6>
        <p>
            When referencing this dataset or the
            Contact.Engineering platform in a publication, we
            recommend the following wording:
        </p>
        <p class="fw-semibold mb-1">
            In the main text (software citation):
        </p>
        <BAlert :model-value="true" variant="secondary">
            Portions of the topography analysis were conducted
            using the open-source Contact.Engineering software
            [<a href="https://doi.org/10.1088/2051-672X/ac860a"
                target="_blank" rel="noopener">Röttger et al.,
            Surface Topography: Metrology and Properties 10.3
            (2022): 035032</a>].
        </BAlert>
        <template v-if="publication.doi_name">
            <p class="fw-semibold mb-1">
                In the Data Availability Statement:
            </p>
            <BAlert :model-value="true" variant="secondary">
                Measured topographies have been made publicly
                available through Contact.Engineering
                [<a href="https://doi.org/10.1088/2051-672X/ac860a"
                    target="_blank" rel="noopener">Röttger et al.,
                Surface Topography: Metrology and Properties 10.3
                (2022): 035032</a>], and are accessible via DOI:
                <a :href="`https://doi.org/${publication.doi_name}`"
                   target="_blank"
                   rel="noopener">https://doi.org/{{ publication.doi_name }}</a>.
            </BAlert>
        </template>
        <hr/>
        <p class="fw-semibold">
            Bibliographic reference for this dataset:
            <HelpTooltip label="About citation formats"
                text="Copy the reference in the format your tools use: plain Citation (human-readable), or RIS / BibTeX / BibLaTeX for import into reference managers (EndNote, Zotero, LaTeX, etc.)."/>
        </p>
        <BAccordion>
            <BAccordionItem title="Citation" visible>
                <div v-html="publication.citation.html"/>
            </BAccordionItem>
            <BAccordionItem title="RIS">
                <code>
                    <pre>{{ publication.citation.ris }}</pre>
                </code>
            </BAccordionItem>
            <BAccordionItem title="BibTeX">
                <code>
                    <pre>{{ publication.citation.bibtex }}</pre>
                </code>
            </BAccordionItem>
            <BAccordionItem title="BibLaTeX">
                <code>
                    <pre>{{ publication.citation.biblatex }}</pre>
                </code>
            </BAccordionItem>
        </BAccordion>
    </div>
</template>
