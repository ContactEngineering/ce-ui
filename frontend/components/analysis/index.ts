import ContactMechanicsCard from '@/components/analysis/ContactMechanicsCard.vue';
import RoughnessParametersCard from '@/components/analysis/RoughnessParametersCard.vue';
import SeriesCard from '@/components/analysis/SeriesCard.vue';


export function registerAnalysisCardComponents(app) {
    app.component('ContactMechanicsCard', ContactMechanicsCard);
    app.component('RoughnessParametersCard', RoughnessParametersCard);
    app.component('SeriesCard', SeriesCard);
}
