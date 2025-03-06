import 'topobank/scss/custom.scss';

import Home from './Home.vue';

import DatasetDetail from './DatasetDetail.vue';
import DatasetList from './DatasetList.vue';
import TopographyDetail from './TopographyDetail.vue';

export const componentIndex = [
    {name: "home", implementation: Home},
    {name: "dataset-list", implementation: DatasetList},
    {name: "dataset-detail", implementation: DatasetDetail},
    {name: "topography-detail", implementation: TopographyDetail}
];