import ContactMechanicsCard from 'topobank_contact/ContactMechanicsCard.vue';
import RoughnessParametersCard from 'topobank_statistics/RoughnessParametersCard.vue';
import SeriesCard from 'topobank/analysis/SeriesCard.vue';


export function registerAnalysisCardComponents(app) {
    app.component('ContactMechanicsCard', ContactMechanicsCard);
    app.component('RoughnessParametersCard', RoughnessParametersCard);
    app.component('SeriesCard', SeriesCard);
}
