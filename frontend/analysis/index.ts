import ContactMechanicsCard from '@/analysis/ContactMechanicsCard.vue';
import RoughnessParametersCard from '@/analysis/RoughnessParametersCard.vue';
import SeriesCard from '@/analysis/SeriesCard.vue';


export function registerAnalysisCardComponents(app) {
    app.component('ContactMechanicsCard', ContactMechanicsCard);
    app.component('RoughnessParametersCard', RoughnessParametersCard);
    app.component('SeriesCard', SeriesCard);
}
