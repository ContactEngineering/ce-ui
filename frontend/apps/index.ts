import '../scss/custom.scss';

import Home from './Home.vue';

import AnalysisResultsDetail from "./AnalysisResultsDetail.vue";
import AnalysisResultsList from "./AnalysisResultsList.vue";
import DatasetDetail from './DatasetDetail.vue';
import DatasetList from './DatasetList.vue';
import DatasetPublish from './DatasetPublish.vue';
import TopographyDetail from './TopographyDetail.vue';

interface ComponentIndex {
    name: string,
    implementation: any
}

const componentIndex: ComponentIndex = [
    {name: "AnalysisDetail", implementation: AnalysisResultsDetail},
    {name: "AnalysisList", implementation: AnalysisResultsList},
    {name: "DatasetList", implementation: DatasetList},
    {name: "DatasetDetail", implementation: DatasetDetail},
    {name: "DatasetPublish", implementation: DatasetPublish},
    {name: "Home", implementation: Home},
    {name: "TopographyDetail", implementation: TopographyDetail}
];

export function registerAppComponents(app) {
    for (const component of componentIndex) {
        app.component(component.name, component.implementation);
    }
}