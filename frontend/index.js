import 'topobank/scss/custom.scss';

import DatasetList from './manager/DatasetList.vue';
import DatasetDetail from './manager/DatasetDetail.vue';
import TopographyDetail from './manager/TopographyDetail.vue';

export const componentIndex = [
    {name: "dataset-list", implementation: DatasetList},
    {name: "dataset-detail", implementation: DatasetDetail},
    {name: "topography-detail", implementation: TopographyDetail}
];