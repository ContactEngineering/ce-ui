import '../scss/custom.scss';

import Home from './Home.vue';

import AnalysisResultsDetail from "./AnalysisResultsDetail.vue";
import AnalysisResultsList from "./AnalysisResultsList.vue";
import DatasetDetail from './DatasetDetail.vue';
import DatasetList from './DatasetList.vue';
import TopographyDetail from './TopographyDetail.vue';

export const componentIndex = [
    {name: "analysis-detail", implementation: AnalysisResultsDetail},
    {name: "analysis-list", implementation: AnalysisResultsList},
    {name: "dataset-list", implementation: DatasetList},
    {name: "dataset-detail", implementation: DatasetDetail},
    {name: "home", implementation: Home},
    {name: "topography-detail", implementation: TopographyDetail}
];